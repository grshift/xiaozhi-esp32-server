"""
Mock传感器数据生成器

该模块提供完整的Mock传感器数据生成功能，包括：
- 虚拟设备管理
- 智能数据生成
- 实时和历史数据生成
- 自动数据生成任务调度
- 数据发送到Java后端
"""

import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import uuid

# 导入现有的传感器处理模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.handle.sensorHandle import handle_sensor_data_message


@dataclass
class MockDevice:
    """Mock设备信息"""
    mac_address: str
    name: str
    created_at: datetime
    last_active: Optional[datetime] = None
    is_active: bool = True
    auto_generation_task: Optional[threading.Timer] = None
    generation_interval: int = 30  # 默认30秒间隔


@dataclass 
class SensorConfig:
    """传感器配置"""
    sensor_type: str
    min_value: float
    max_value: float
    precision: int
    unit: str
    variation_range: float = 0.1  # 变化范围比例


class MockSensorDataGenerator:
    """Mock传感器数据生成器"""
    
    # 传感器类型配置 - 严格按照文档定义
    SENSOR_CONFIGS = {
        "temperature": SensorConfig("temperature", 18.0, 35.0, 2, "°C", 0.05),
        "humidity": SensorConfig("humidity", 30.0, 80.0, 1, "%", 0.08),
        "light": SensorConfig("light", 0, 2000, 0, "lux", 0.15),
        "motion": SensorConfig("motion", 0, 1, 0, "", 0.0),
        "air_quality": SensorConfig("air_quality", 0, 500, 0, "ppm", 0.1),
        "co2": SensorConfig("co2", 300, 2000, 0, "ppm", 0.1)
    }
    
    def __init__(self):
        self.devices: Dict[str, MockDevice] = {}
        self.sensor_history: Dict[str, Dict[str, List[float]]] = {}  # mac -> sensor_type -> values
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=10)
        
    def create_device(self, mac_address: Optional[str] = None, name: Optional[str] = None) -> MockDevice:
        """
        创建Mock设备
        
        Args:
            mac_address: 设备MAC地址，如果为None则自动生成
            name: 设备名称，如果为None则使用默认名称
            
        Returns:
            MockDevice: 创建的设备对象
        """
        with self._lock:
            if mac_address is None:
                mac_address = self._generate_mac_address()
            
            if name is None:
                name = f"Mock设备_{mac_address[-5:]}"
            
            if mac_address in self.devices:
                raise ValueError(f"设备 {mac_address} 已存在")
            
            device = MockDevice(
                mac_address=mac_address,
                name=name,
                created_at=datetime.now(),
                is_active=True
            )
            
            self.devices[mac_address] = device
            self.sensor_history[mac_address] = {}
            
            print(f"✅ 已创建Mock设备: {name} ({mac_address})")
            return device
    
    def remove_device(self, mac_address: str) -> bool:
        """
        删除Mock设备
        
        Args:
            mac_address: 设备MAC地址
            
        Returns:
            bool: 是否成功删除
        """
        with self._lock:
            if mac_address not in self.devices:
                return False
            
            device = self.devices[mac_address]
            
            # 停止自动生成任务
            if device.auto_generation_task:
                device.auto_generation_task.cancel()
            
            # 删除设备和历史数据
            del self.devices[mac_address]
            if mac_address in self.sensor_history:
                del self.sensor_history[mac_address]
            
            print(f"✅ 已删除Mock设备: {device.name} ({mac_address})")
            return True
    
    def list_devices(self) -> List[MockDevice]:
        """获取所有Mock设备列表"""
        with self._lock:
            return list(self.devices.values())
    
    def get_device(self, mac_address: str) -> Optional[MockDevice]:
        """获取指定设备信息"""
        return self.devices.get(mac_address)
    
    def generate_sensor_value(self, sensor_type: str, previous_value: Optional[float] = None) -> float:
        """
        生成单个传感器的智能数据
        
        Args:
            sensor_type: 传感器类型
            previous_value: 上一次的值，用于生成连续性数据
            
        Returns:
            float: 生成的传感器值
        """
        if sensor_type not in self.SENSOR_CONFIGS:
            raise ValueError(f"不支持的传感器类型: {sensor_type}")
        
        config = self.SENSOR_CONFIGS[sensor_type]
        
        # 特殊处理运动传感器
        if sensor_type == "motion":
            return random.choice([0, 1])
        
        # 如果有历史值，基于历史值生成连续性数据
        if previous_value is not None:
            variation = (config.max_value - config.min_value) * config.variation_range
            change = random.uniform(-variation, variation)
            new_value = previous_value + change
            
            # 确保在有效范围内
            new_value = max(config.min_value, min(config.max_value, new_value))
        else:
            # 生成初始随机值
            new_value = random.uniform(config.min_value, config.max_value)
        
        # 根据精度要求四舍五入
        if config.precision > 0:
            return round(new_value, config.precision)
        else:
            return int(new_value)
    
    def generate_device_data(self, mac_address: str, sensor_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        为指定设备生成一次完整的传感器数据
        
        Args:
            mac_address: 设备MAC地址
            sensor_types: 要生成的传感器类型列表，如果为None则生成所有类型
            
        Returns:
            Dict: 生成的传感器数据
        """
        if mac_address not in self.devices:
            raise ValueError(f"设备 {mac_address} 不存在")
        
        device = self.devices[mac_address]
        
        if sensor_types is None:
            sensor_types = list(self.SENSOR_CONFIGS.keys())
        
        # 生成传感器数据
        sensors = []
        current_time = time.time()
        
        for sensor_type in sensor_types:
            # 获取历史值用于生成连续性数据
            previous_value = None
            if mac_address in self.sensor_history and sensor_type in self.sensor_history[mac_address]:
                history = self.sensor_history[mac_address][sensor_type]
                if history:
                    previous_value = history[-1]
            
            # 生成新值
            value = self.generate_sensor_value(sensor_type, previous_value)
            
            # 记录到历史
            if mac_address not in self.sensor_history:
                self.sensor_history[mac_address] = {}
            if sensor_type not in self.sensor_history[mac_address]:
                self.sensor_history[mac_address][sensor_type] = []
            
            self.sensor_history[mac_address][sensor_type].append(value)
            
            # 保持历史记录在合理范围内（最多1000条）
            if len(self.sensor_history[mac_address][sensor_type]) > 1000:
                self.sensor_history[mac_address][sensor_type] = self.sensor_history[mac_address][sensor_type][-1000:]
            
            # 构建传感器数据
            sensors.append({
                "sensor_code": self._map_sensor_type_to_code(sensor_type),
                "value": value
            })
        
        # 更新设备活跃时间
        device.last_active = datetime.now()
        
        # 构建完整的消息数据
        message_data = {
            "mac_address": mac_address,
            "timestamp": current_time,
            "sensors": sensors
        }
        
        return message_data
    
    def send_data_to_backend(self, message_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        发送数据到后端（集成现有的传感器处理流程）
        
        Args:
            message_data: 消息数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查API客户端是否已初始化
            from config.manage_api_client import ManageApiClient
            if ManageApiClient._instance is None:
                # API客户端未初始化，使用模拟模式
                return self._send_data_mock_mode(message_data)
            
            # 使用现有的传感器数据处理函数
            is_success, message, processed_data = handle_sensor_data_message(message_data)
            
            if is_success:
                mac_address = message_data["mac_address"]
                sensor_count = len(message_data["sensors"])
                print(f"✅ 成功发送设备 {mac_address} 的 {sensor_count} 个传感器数据到后端")
                return True, message
            else:
                print(f"❌ 发送数据失败: {message}")
                return False, message
                
        except Exception as e:
            error_msg = f"发送数据异常: {str(e)}"
            print(f"❌ {error_msg}")
            # 如果是API客户端问题，尝试模拟模式
            if "'NoneType' object has no attribute '_execute_request'" in str(e):
                return self._send_data_mock_mode(message_data)
            return False, error_msg
    
    def _send_data_mock_mode(self, message_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        模拟模式：在没有后端API的情况下验证数据处理逻辑
        
        Args:
            message_data: 消息数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 验证消息数据格式
            mac_address = message_data.get("mac_address", "")
            if not mac_address:
                return False, "缺少设备MAC地址"
            
            sensors = message_data.get("sensors", [])
            if not sensors:
                return False, "缺少传感器数据"
            
            # 验证每个传感器数据
            valid_sensors = []
            for sensor in sensors:
                sensor_code = sensor.get("sensor_code", "")
                sensor_value = sensor.get("value")
                
                if sensor_code and sensor_value is not None:
                    valid_sensors.append(f"{sensor_code}={sensor_value}")
            
            if not valid_sensors:
                return False, "没有有效的传感器数据"
            
            # 模拟成功响应
            sensor_count = len(valid_sensors)
            print(f"🔄 [模拟模式] 设备 {mac_address} 的 {sensor_count} 个传感器数据已验证")
            print(f"   传感器数据: {', '.join(valid_sensors)}")
            
            return True, f"模拟模式：成功处理 {sensor_count} 个传感器数据"
            
        except Exception as e:
            return False, f"模拟模式处理异常: {str(e)}"
    
    def generate_and_send_data(self, mac_address: str, sensor_types: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        生成数据并发送到后端
        
        Args:
            mac_address: 设备MAC地址
            sensor_types: 传感器类型列表
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 生成数据
            message_data = self.generate_device_data(mac_address, sensor_types)
            
            # 发送到后端
            return self.send_data_to_backend(message_data)
            
        except Exception as e:
            error_msg = f"生成并发送数据失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def generate_history_data(self, mac_address: str, hours: int = 24, interval_minutes: int = 5) -> List[Tuple[bool, str]]:
        """
        生成历史数据
        
        Args:
            mac_address: 设备MAC地址
            hours: 生成多少小时的历史数据
            interval_minutes: 数据间隔（分钟）
            
        Returns:
            List[Tuple[bool, str]]: 每次发送的结果
        """
        if mac_address not in self.devices:
            raise ValueError(f"设备 {mac_address} 不存在")
        
        results = []
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=hours)
        
        # 计算需要生成的数据点数量
        total_minutes = hours * 60
        data_points = total_minutes // interval_minutes
        
        print(f"🔄 开始为设备 {mac_address} 生成 {hours} 小时的历史数据...")
        print(f"   数据点数量: {data_points}, 间隔: {interval_minutes} 分钟")
        
        for i in range(data_points):
            # 计算当前数据点的时间戳
            data_time = start_time + timedelta(minutes=i * interval_minutes)
            timestamp = data_time.timestamp()
            
            try:
                # 生成传感器数据（不包含时间戳，会在后续设置）
                message_data = self.generate_device_data(mac_address)
                message_data["timestamp"] = timestamp  # 使用历史时间戳
                
                # 发送到后端
                success, message = self.send_data_to_backend(message_data)
                results.append((success, message))
                
                # 显示进度
                if (i + 1) % 50 == 0 or i == data_points - 1:
                    progress = (i + 1) / data_points * 100
                    print(f"   进度: {progress:.1f}% ({i + 1}/{data_points})")
                
                # 添加小延迟避免过快发送
                time.sleep(0.05)
                
            except Exception as e:
                error_msg = f"生成历史数据失败 (第{i+1}条): {str(e)}"
                print(f"❌ {error_msg}")
                results.append((False, error_msg))
        
        successful_count = sum(1 for success, _ in results if success)
        print(f"✅ 历史数据生成完成: {successful_count}/{len(results)} 条成功")
        
        return results
    
    def start_auto_generation(self, mac_address: str, interval_seconds: int = 30) -> bool:
        """
        启动自动数据生成
        
        Args:
            mac_address: 设备MAC地址
            interval_seconds: 生成间隔（秒）
            
        Returns:
            bool: 是否成功启动
        """
        if mac_address not in self.devices:
            return False
        
        device = self.devices[mac_address]
        
        # 停止现有的自动生成任务
        if device.auto_generation_task:
            device.auto_generation_task.cancel()
        
        device.generation_interval = interval_seconds
        
        def auto_generate():
            try:
                self.generate_and_send_data(mac_address)
            except Exception as e:
                print(f"❌ 自动生成数据异常: {str(e)}")
            
            # 安排下一次生成
            if device.is_active and mac_address in self.devices:
                device.auto_generation_task = threading.Timer(interval_seconds, auto_generate)
                device.auto_generation_task.start()
        
        # 启动自动生成
        device.auto_generation_task = threading.Timer(interval_seconds, auto_generate)
        device.auto_generation_task.start()
        
        print(f"🔄 已启动设备 {mac_address} 的自动数据生成，间隔: {interval_seconds} 秒")
        return True
    
    def stop_auto_generation(self, mac_address: str) -> bool:
        """
        停止自动数据生成
        
        Args:
            mac_address: 设备MAC地址
            
        Returns:
            bool: 是否成功停止
        """
        if mac_address not in self.devices:
            return False
        
        device = self.devices[mac_address]
        
        if device.auto_generation_task:
            device.auto_generation_task.cancel()
            device.auto_generation_task = None
            print(f"⏹️  已停止设备 {mac_address} 的自动数据生成")
            return True
        
        return False
    
    def get_device_status(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """
        获取设备状态信息
        
        Args:
            mac_address: 设备MAC地址
            
        Returns:
            Dict: 设备状态信息
        """
        if mac_address not in self.devices:
            return None
        
        device = self.devices[mac_address]
        
        # 获取传感器历史统计
        sensor_stats = {}
        if mac_address in self.sensor_history:
            for sensor_type, history in self.sensor_history[mac_address].items():
                if history:
                    sensor_stats[sensor_type] = {
                        "count": len(history),
                        "latest_value": history[-1],
                        "min_value": min(history),
                        "max_value": max(history),
                        "avg_value": sum(history) / len(history)
                    }
        
        return {
            "mac_address": device.mac_address,
            "name": device.name,
            "created_at": device.created_at.isoformat(),
            "last_active": device.last_active.isoformat() if device.last_active else None,
            "is_active": device.is_active,
            "auto_generation_active": device.auto_generation_task is not None,
            "generation_interval": device.generation_interval,
            "sensor_stats": sensor_stats
        }
    
    def _generate_mac_address(self) -> str:
        """生成随机MAC地址"""
        mac_parts = []
        for _ in range(6):
            mac_parts.append(f"{random.randint(0, 255):02X}")
        return ":".join(mac_parts)
    
    def _map_sensor_type_to_code(self, sensor_type: str) -> str:
        """映射传感器类型到代码"""
        mapping = {
            "temperature": "temp_01",
            "humidity": "humi_01", 
            "light": "light_01",
            "motion": "motion_01",
            "air_quality": "air_quality_01",
            "co2": "co2_01"
        }
        return mapping.get(sensor_type, sensor_type)


# 全局生成器实例
_generator_instance = None

def get_generator() -> MockSensorDataGenerator:
    """获取全局生成器实例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = MockSensorDataGenerator()
    return _generator_instance