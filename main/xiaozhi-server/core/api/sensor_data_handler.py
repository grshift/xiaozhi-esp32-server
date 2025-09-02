import json
import asyncio
from datetime import datetime
from aiohttp import web
from core.api.base_handler import BaseHandler
from core.utils.llm import LLMHelper
from config.logger import setup_logging

TAG = __name__

class SensorDataHandler(BaseHandler):
    """传感器数据处理处理器"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.logger = setup_logging()
        self.llm = LLMHelper(config)
        self.sensor_history = {}
    
    async def process_sensor_data(self, sensor_data: dict, plant_info: dict = None):
        """处理传感器数据并生成植物养护决策"""
        
        sensor_summary = self._build_sensor_summary(sensor_data)
        plant_context = self._build_plant_context(plant_info) if plant_info else ""
        
        prompt = f"""
你是一个专业的植物养护专家。请根据以下传感器数据为植物提供养护决策：

## 当前传感器数据：
{sensor_summary}

## 植物信息：
{plant_context}

请提供：
1. 环境评估
2. 养护决策（浇水、光照、温度、施肥）
3. 自动化建议
4. 健康预警
5. 数据趋势分析
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm.generate_response(messages)
            decisions = self._extract_decisions(response)
            
            return {
                "success": True,
                "analysis": response,
                "decisions": decisions,
                "timestamp": datetime.now().isoformat(),
                "sensor_data": sensor_data
            }
            
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"传感器数据处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_sensor_summary(self, sensor_data: dict) -> str:
        """构建传感器数据摘要"""
        summary = []
        if "temperature" in sensor_data:
            summary.append(f"- 温度: {sensor_data['temperature']}°C")
        if "humidity" in sensor_data:
            summary.append(f"- 空气湿度: {sensor_data['humidity']}%")
        if "soil_moisture" in sensor_data:
            summary.append(f"- 土壤湿度: {sensor_data['soil_moisture']}%")
        if "light_intensity" in sensor_data:
            summary.append(f"- 光照强度: {sensor_data['light_intensity']} lux")
        return "\n".join(summary) if summary else "无传感器数据"
    
    def _build_plant_context(self, plant_info: dict) -> str:
        """构建植物上下文信息"""
        if not plant_info:
            return "未知植物种类"
        
        context = []
        if "species" in plant_info:
            context.append(f"- 植物种类: {plant_info['species']}")
        if "growth_stage" in plant_info:
            context.append(f"- 生长阶段: {plant_info['growth_stage']}")
        return "\n".join(context) if context else "植物信息不完整"
    
    def _extract_decisions(self, response: str) -> dict:
        """从大模型响应中提取关键决策"""
        decisions = {
            "watering_needed": False,
            "light_adjustment": False,
            "temperature_adjustment": False,
            "fertilization_needed": False,
            "health_alert": False,
            "actions": []
        }
        
        response_lower = response.lower()
        
        if any(word in response_lower for word in ["浇水", "water", "缺水"]):
            decisions["watering_needed"] = True
            decisions["actions"].append("需要浇水")
        
        if any(word in response_lower for word in ["光照", "light", "阳光"]):
            decisions["light_adjustment"] = True
            decisions["actions"].append("需要调整光照")
        
        if any(word in response_lower for word in ["温度", "temperature"]):
            decisions["temperature_adjustment"] = True
            decisions["actions"].append("需要调整温度")
        
        if any(word in response_lower for word in ["施肥", "fertilizer"]):
            decisions["fertilization_needed"] = True
            decisions["actions"].append("需要施肥")
        
        if any(word in response_lower for word in ["警告", "alert", "危险"]):
            decisions["health_alert"] = True
            decisions["actions"].append("健康预警")
        
        return decisions
    
    async def handle_post(self, request):
        """处理传感器数据POST请求"""
        try:
            is_valid, token_device_id = self._verify_auth_token(request)
            if not is_valid:
                return web.Response(
                    text=json.dumps(self._create_error_response("无效的认证token")),
                    content_type="application/json",
                    status=401
                )
            
            data = await request.json()
            
            if not data or "sensor_data" not in data:
                raise ValueError("缺少传感器数据")
            
            sensor_data = data["sensor_data"]
            plant_info = data.get("plant_info", {})
            
            if not isinstance(sensor_data, dict):
                raise ValueError("传感器数据格式错误")
            
            result = await self.process_sensor_data(sensor_data, plant_info)
            
            response = web.Response(
                text=json.dumps(result, ensure_ascii=False),
                content_type="application/json"
            )
            
            self._add_cors_headers(response)
            return response
            
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"传感器数据处理请求失败: {e}")
            error_response = web.Response(
                text=json.dumps(self._create_error_response(str(e)), ensure_ascii=False),
                content_type="application/json",
                status=400
            )
            self._add_cors_headers(error_response)
            return error_response
    
    async def handle_get(self, request):
        """处理GET请求，返回API使用说明"""
        usage_info = {
            "api_name": "传感器数据处理接口",
            "description": "处理传感器数据并生成植物养护决策",
            "method": "POST",
            "content_type": "application/json",
            "request_format": {
                "sensor_data": {
                    "temperature": "温度 (°C)",
                    "humidity": "空气湿度 (%)",
                    "soil_moisture": "土壤湿度 (%)",
                    "light_intensity": "光照强度 (lux)"
                },
                "plant_info": {
                    "species": "植物种类",
                    "growth_stage": "生长阶段"
                }
            }
        }
        
        response = web.Response(
            text=json.dumps(usage_info, ensure_ascii=False),
            content_type="application/json"
        )
        self._add_cors_headers(response)
        return response 