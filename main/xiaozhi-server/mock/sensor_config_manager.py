#!/usr/bin/env python3
"""
传感器配置管理工具

该工具用于管理和验证传感器配置的动态创建：
- 自动创建缺失的传感器类型定义
- 为Mock设备创建传感器配置
- 验证传感器配置的完整性
- 支持传感器配置的批量操作
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mock.mock_logger import create_mock_logger_helper, setup_mock_logging

class SensorConfigManager:
    """传感器配置管理器"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip('/')
        
        # 设置日志
        setup_mock_logging("INFO", "tmp/mock_logs", True)
        self.logger = create_mock_logger_helper("CONFIG_MANAGER")
        
        # API端点
        self.endpoints = {
            "sensor_types": "/xiaozhi/sensor/type",
            "device_sensors": "/xiaozhi/sensor/device/sensors",
            "devices": "/xiaozhi/device"
        }
        
        # 预定义的传感器类型配置
        self.predefined_sensor_types = {
            "temperature": {
                "typeCode": "temperature",
                "typeName": "温度传感器",
                "unit": "°C",
                "dataType": "number",
                "icon": "thermometer",
                "description": "环境温度检测传感器",
                "valueRange": json.dumps({"min": -40, "max": 85}),
                "precision": 2,
                "sort": 1
            },
            "humidity": {
                "typeCode": "humidity", 
                "typeName": "湿度传感器",
                "unit": "%",
                "dataType": "number",
                "icon": "droplet",
                "description": "环境湿度检测传感器",
                "valueRange": json.dumps({"min": 0, "max": 100}),
                "precision": 1,
                "sort": 2
            },
            "light": {
                "typeCode": "light",
                "typeName": "光照传感器", 
                "unit": "lux",
                "dataType": "number",
                "icon": "sun",
                "description": "环境光照强度检测传感器",
                "valueRange": json.dumps({"min": 0, "max": 100000}),
                "precision": 0,
                "sort": 3
            },
            "motion": {
                "typeCode": "motion",
                "typeName": "运动传感器",
                "unit": "",
                "dataType": "boolean", 
                "icon": "activity",
                "description": "人体运动检测传感器",
                "valueRange": json.dumps({"values": [0, 1]}),
                "precision": 0,
                "sort": 4
            },
            "air_quality": {
                "typeCode": "air_quality",
                "typeName": "空气质量传感器",
                "unit": "ppm",
                "dataType": "number",
                "icon": "wind",
                "description": "空气质量检测传感器",
                "valueRange": json.dumps({"min": 0, "max": 1000}),
                "precision": 0,
                "sort": 5
            },
            "co2": {
                "typeCode": "co2",
                "typeName": "CO2传感器",
                "unit": "ppm", 
                "dataType": "number",
                "icon": "cloud",
                "description": "二氧化碳浓度检测传感器",
                "valueRange": json.dumps({"min": 200, "max": 5000}),
                "precision": 0,
                "sort": 6
            },
            "pressure": {
                "typeCode": "pressure",
                "typeName": "气压传感器",
                "unit": "hPa",
                "dataType": "number", 
                "icon": "gauge",
                "description": "大气压力检测传感器",
                "valueRange": json.dumps({"min": 800, "max": 1200}),
                "precision": 1,
                "sort": 7
            }
        }
        
        # 传感器代码映射
        self.sensor_code_mapping = {
            "temp_01": "temperature",
            "humi_01": "humidity", 
            "light_01": "light",
            "motion_01": "motion",
            "air_quality_01": "air_quality",
            "co2_01": "co2",
            "pressure_01": "pressure"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Optional[Dict], str]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.debug(f"发送{method}请求: {url}", "HTTP_REQUEST")
            
            response = requests.request(method, url, timeout=10, **kwargs)
            
            self.logger.debug(f"响应状态: {response.status_code}", "HTTP_RESPONSE")
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    return True, data, "请求成功"
                except json.JSONDecodeError:
                    return True, None, "请求成功（无JSON响应）"
            else:
                return False, None, f"HTTP错误: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, None, "连接失败：后端服务未启动或不可访问"
        except requests.exceptions.Timeout:
            return False, None, "请求超时"
        except Exception as e:
            return False, None, f"请求异常: {str(e)}"
    
    def get_existing_sensor_types(self) -> Dict[str, Any]:
        """获取现有的传感器类型"""
        self.logger.info("获取现有传感器类型", "SENSOR_TYPES")
        
        success, data, message = self._make_request("GET", f"{self.endpoints['sensor_types']}/list")
        
        if success and data and data.get("code") == 0:
            sensor_types = data.get("data", [])
            type_map = {st["typeCode"]: st for st in sensor_types}
            self.logger.info(f"获取到 {len(sensor_types)} 个传感器类型", "SENSOR_TYPES")
            return type_map
        else:
            self.logger.warning(f"获取传感器类型失败: {message}", "SENSOR_TYPES")
            return {}
    
    def create_sensor_type(self, sensor_type_config: Dict[str, Any]) -> bool:
        """创建传感器类型"""
        type_code = sensor_type_config["typeCode"]
        self.logger.info(f"创建传感器类型: {type_code}", "CREATE_TYPE")
        
        success, data, message = self._make_request(
            "POST",
            f"{self.endpoints['sensor_types']}/save",
            json=sensor_type_config,
            headers={"Content-Type": "application/json"}
        )
        
        if success:
            self.logger.info(f"传感器类型创建成功: {type_code}", "CREATE_TYPE")
            return True
        else:
            self.logger.error(f"传感器类型创建失败: {type_code} - {message}", "CREATE_TYPE")
            return False
    
    def ensure_sensor_types_exist(self) -> Dict[str, bool]:
        """确保所有预定义的传感器类型存在"""
        self.logger.info("开始确保传感器类型存在", "ENSURE_TYPES")
        
        # 获取现有类型
        existing_types = self.get_existing_sensor_types()
        
        results = {}
        
        for type_code, type_config in self.predefined_sensor_types.items():
            if type_code in existing_types:
                self.logger.debug(f"传感器类型已存在: {type_code}", "ENSURE_TYPES")
                results[type_code] = True
            else:
                self.logger.info(f"创建缺失的传感器类型: {type_code}", "ENSURE_TYPES")
                success = self.create_sensor_type(type_config)
                results[type_code] = success
        
        successful_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        self.logger.info(f"传感器类型确保完成: {successful_count}/{total_count}", "ENSURE_TYPES")
        
        return results
    
    def get_device_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """根据MAC地址获取设备信息"""
        self.logger.debug(f"查询设备: {mac_address}", "DEVICE_QUERY")
        
        success, data, message = self._make_request(
            "GET",
            f"{self.endpoints['devices']}/mac/{mac_address}"
        )
        
        if success and data and data.get("code") == 0:
            device = data.get("data")
            if device:
                self.logger.debug(f"找到设备: {device.get('name', 'Unknown')}", "DEVICE_QUERY")
                return device
        
        self.logger.debug(f"设备不存在: {mac_address}", "DEVICE_QUERY")
        return None
    
    def create_device(self, mac_address: str, device_name: str) -> Optional[Dict[str, Any]]:
        """创建设备"""
        self.logger.info(f"创建设备: {device_name} ({mac_address})", "CREATE_DEVICE")
        
        device_config = {
            "name": device_name,
            "macAddress": mac_address,
            "deviceType": "ESP32",
            "status": 1,  # 启用状态
            "description": f"Mock测试设备 - {device_name}",
            "location": "测试环境"
        }
        
        success, data, message = self._make_request(
            "POST",
            f"{self.endpoints['devices']}/save",
            json=device_config,
            headers={"Content-Type": "application/json"}
        )
        
        if success and data and data.get("code") == 0:
            device = data.get("data")
            self.logger.info(f"设备创建成功: {device_name}", "CREATE_DEVICE")
            return device
        else:
            self.logger.error(f"设备创建失败: {device_name} - {message}", "CREATE_DEVICE")
            return None
    
    def get_device_sensors(self, device_id: str) -> List[Dict[str, Any]]:
        """获取设备的传感器配置"""
        self.logger.debug(f"获取设备传感器配置: {device_id}", "DEVICE_SENSORS")
        
        success, data, message = self._make_request(
            "GET",
            f"{self.endpoints['device_sensors']}/{device_id}"
        )
        
        if success and data and data.get("code") == 0:
            sensors = data.get("data", [])
            self.logger.debug(f"获取到 {len(sensors)} 个传感器配置", "DEVICE_SENSORS")
            return sensors
        else:
            self.logger.debug(f"获取设备传感器配置失败: {message}", "DEVICE_SENSORS")
            return []
    
    def create_device_sensor(self, device_id: str, sensor_type_id: str, sensor_code: str, sensor_name: str) -> bool:
        """为设备创建传感器配置"""
        self.logger.info(f"创建设备传感器配置: {sensor_code}", "CREATE_SENSOR")
        
        sensor_config = {
            "deviceId": device_id,
            "sensorTypeId": sensor_type_id,
            "sensorCode": sensor_code,
            "sensorName": sensor_name,
            "isEnabled": 1,
            "status": 1,
            "location": "默认位置",
            "sort": self._get_sensor_sort_order(sensor_code)
        }
        
        success, data, message = self._make_request(
            "POST",
            f"{self.endpoints['device_sensors']}/save",
            json=sensor_config,
            headers={"Content-Type": "application/json"}
        )
        
        if success:
            self.logger.info(f"设备传感器配置创建成功: {sensor_code}", "CREATE_SENSOR")
            return True
        else:
            self.logger.error(f"设备传感器配置创建失败: {sensor_code} - {message}", "CREATE_SENSOR")
            return False
    
    def setup_device_sensors(self, device_id: str, sensor_codes: List[str]) -> Dict[str, bool]:
        """为设备设置传感器配置"""
        self.logger.info(f"开始设置设备传感器配置: {len(sensor_codes)} 个传感器", "SETUP_SENSORS")
        
        # 获取现有传感器类型
        existing_types = self.get_existing_sensor_types()
        
        # 获取现有设备传感器配置
        existing_sensors = self.get_device_sensors(device_id)
        existing_codes = {sensor["sensorCode"] for sensor in existing_sensors}
        
        results = {}
        
        for sensor_code in sensor_codes:
            if sensor_code in existing_codes:
                self.logger.debug(f"传感器配置已存在: {sensor_code}", "SETUP_SENSORS")
                results[sensor_code] = True
                continue
            
            # 获取传感器类型
            sensor_type_code = self.sensor_code_mapping.get(sensor_code)
            if not sensor_type_code:
                self.logger.warning(f"未知的传感器代码: {sensor_code}", "SETUP_SENSORS")
                results[sensor_code] = False
                continue
            
            sensor_type = existing_types.get(sensor_type_code)
            if not sensor_type:
                self.logger.warning(f"传感器类型不存在: {sensor_type_code}", "SETUP_SENSORS")
                results[sensor_code] = False
                continue
            
            # 创建传感器配置
            sensor_name = f"{sensor_type['typeName']}_{sensor_code.split('_')[-1]}"
            success = self.create_device_sensor(
                device_id, 
                sensor_type["id"], 
                sensor_code, 
                sensor_name
            )
            results[sensor_code] = success
        
        successful_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        self.logger.info(f"设备传感器配置设置完成: {successful_count}/{total_count}", "SETUP_SENSORS")
        
        return results
    
    def setup_mock_device_complete(self, mac_address: str, device_name: str, sensor_codes: List[str]) -> Dict[str, Any]:
        """完整设置Mock设备（设备+传感器类型+传感器配置）"""
        self.logger.info(f"开始完整设置Mock设备: {device_name}", "SETUP_COMPLETE")
        
        setup_results = {
            "device_creation": False,
            "sensor_types": {},
            "device_sensors": {},
            "overall_success": False
        }
        
        try:
            # 1. 确保传感器类型存在
            self.logger.info("步骤1: 确保传感器类型存在", "SETUP_COMPLETE")
            type_results = self.ensure_sensor_types_exist()
            setup_results["sensor_types"] = type_results
            
            # 2. 创建或获取设备
            self.logger.info("步骤2: 创建或获取设备", "SETUP_COMPLETE")
            device = self.get_device_by_mac(mac_address)
            
            if not device:
                device = self.create_device(mac_address, device_name)
                if device:
                    setup_results["device_creation"] = True
                else:
                    self.logger.error("设备创建失败，无法继续", "SETUP_COMPLETE")
                    return setup_results
            else:
                self.logger.info("设备已存在，使用现有设备", "SETUP_COMPLETE")
                setup_results["device_creation"] = True
            
            # 3. 设置设备传感器配置
            self.logger.info("步骤3: 设置设备传感器配置", "SETUP_COMPLETE")
            sensor_results = self.setup_device_sensors(device["id"], sensor_codes)
            setup_results["device_sensors"] = sensor_results
            
            # 4. 检查整体成功率
            type_success_rate = sum(1 for success in type_results.values() if success) / len(type_results)
            sensor_success_rate = sum(1 for success in sensor_results.values() if success) / len(sensor_results)
            
            overall_success = (
                setup_results["device_creation"] and 
                type_success_rate >= 0.8 and 
                sensor_success_rate >= 0.8
            )
            
            setup_results["overall_success"] = overall_success
            
            if overall_success:
                self.logger.info("Mock设备完整设置成功", "SETUP_COMPLETE")
            else:
                self.logger.warning("Mock设备设置部分失败", "SETUP_COMPLETE")
            
            return setup_results
            
        except Exception as e:
            self.logger.error(f"Mock设备设置异常: {str(e)}", "SETUP_COMPLETE")
            setup_results["error"] = str(e)
            return setup_results
    
    def _get_sensor_sort_order(self, sensor_code: str) -> int:
        """获取传感器排序顺序"""
        sort_mapping = {
            "temp_01": 1,
            "humi_01": 2,
            "light_01": 3,
            "motion_01": 4,
            "air_quality_01": 5,
            "co2_01": 6,
            "pressure_01": 7
        }
        return sort_mapping.get(sensor_code, 99)
    
    def validate_sensor_configuration(self, mac_address: str) -> Dict[str, Any]:
        """验证传感器配置的完整性"""
        self.logger.info(f"验证传感器配置: {mac_address}", "VALIDATE_CONFIG")
        
        validation_results = {
            "device_exists": False,
            "sensor_types_count": 0,
            "device_sensors_count": 0,
            "missing_types": [],
            "missing_sensors": [],
            "validation_success": False
        }
        
        try:
            # 检查设备是否存在
            device = self.get_device_by_mac(mac_address)
            if device:
                validation_results["device_exists"] = True
                
                # 检查传感器类型
                sensor_types = self.get_existing_sensor_types()
                validation_results["sensor_types_count"] = len(sensor_types)
                
                expected_types = set(self.predefined_sensor_types.keys())
                existing_types = set(sensor_types.keys())
                missing_types = expected_types - existing_types
                validation_results["missing_types"] = list(missing_types)
                
                # 检查设备传感器配置
                device_sensors = self.get_device_sensors(device["id"])
                validation_results["device_sensors_count"] = len(device_sensors)
                
                existing_sensor_codes = {sensor["sensorCode"] for sensor in device_sensors}
                expected_sensor_codes = set(self.sensor_code_mapping.keys())
                missing_sensors = expected_sensor_codes - existing_sensor_codes
                validation_results["missing_sensors"] = list(missing_sensors)
                
                # 判断验证是否成功
                validation_success = (
                    validation_results["device_exists"] and
                    len(missing_types) == 0 and
                    len(missing_sensors) == 0
                )
                validation_results["validation_success"] = validation_success
                
                if validation_success:
                    self.logger.info("传感器配置验证成功", "VALIDATE_CONFIG")
                else:
                    self.logger.warning("传感器配置验证失败", "VALIDATE_CONFIG")
            else:
                self.logger.warning("设备不存在", "VALIDATE_CONFIG")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"传感器配置验证异常: {str(e)}", "VALIDATE_CONFIG")
            validation_results["error"] = str(e)
            return validation_results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="传感器配置管理工具")
    parser.add_argument('--url', type=str, default='http://localhost:8002',
                       help='后端API基础URL (默认: http://localhost:8002)')
    parser.add_argument('--mac', type=str, default='00:1A:2B:3C:4D:5E',
                       help='设备MAC地址 (默认: 00:1A:2B:3C:4D:5E)')
    parser.add_argument('--name', type=str, default='Mock传感器测试设备',
                       help='设备名称')
    parser.add_argument('--action', type=str, choices=['setup', 'validate', 'types'], 
                       default='setup', help='操作类型')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_mock_logging(log_level, "tmp/mock_logs", True)
    
    try:
        print("🔧 传感器配置管理工具")
        print("=" * 50)
        
        manager = SensorConfigManager(args.url)
        
        if args.action == 'types':
            print("📋 确保传感器类型存在...")
            results = manager.ensure_sensor_types_exist()
            
            print(f"\n传感器类型处理结果:")
            for type_code, success in results.items():
                status = "✅ 成功" if success else "❌ 失败"
                print(f"  {type_code}: {status}")
                
        elif args.action == 'setup':
            print(f"🚀 完整设置Mock设备...")
            print(f"设备: {args.name} ({args.mac})")
            
            sensor_codes = ["temp_01", "humi_01", "light_01", "motion_01", "air_quality_01", "co2_01"]
            results = manager.setup_mock_device_complete(args.mac, args.name, sensor_codes)
            
            print(f"\n设备设置结果:")
            print(f"  设备创建: {'✅ 成功' if results['device_creation'] else '❌ 失败'}")
            
            type_success = sum(1 for s in results['sensor_types'].values() if s)
            type_total = len(results['sensor_types'])
            print(f"  传感器类型: ✅ {type_success}/{type_total}")
            
            sensor_success = sum(1 for s in results['device_sensors'].values() if s)
            sensor_total = len(results['device_sensors'])
            print(f"  设备传感器: ✅ {sensor_success}/{sensor_total}")
            
            print(f"  整体状态: {'✅ 成功' if results['overall_success'] else '❌ 失败'}")
            
        elif args.action == 'validate':
            print(f"🔍 验证传感器配置...")
            print(f"设备: {args.mac}")
            
            results = manager.validate_sensor_configuration(args.mac)
            
            print(f"\n配置验证结果:")
            print(f"  设备存在: {'✅ 是' if results['device_exists'] else '❌ 否'}")
            print(f"  传感器类型数量: {results['sensor_types_count']}")
            print(f"  设备传感器数量: {results['device_sensors_count']}")
            
            if results['missing_types']:
                print(f"  缺失的传感器类型: {', '.join(results['missing_types'])}")
            
            if results['missing_sensors']:
                print(f"  缺失的设备传感器: {', '.join(results['missing_sensors'])}")
            
            print(f"  验证状态: {'✅ 通过' if results['validation_success'] else '❌ 失败'}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🔄 操作被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 操作异常: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
