import json
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from config.manage_api_client import ManageApiClient, report_sensor_data

TAG = __name__

# 传感器数据验证规则
SENSOR_VALIDATION_RULES = {
    "temperature": {
        "type": (int, float),
        "range": (-50, 100),  # 温度范围：-50°C 到 100°C
        "unit": "°C"
    },
    "humidity": {
        "type": (int, float),
        "range": (0, 100),    # 湿度范围：0% 到 100%
        "unit": "%"
    },
    "battery_level": {
        "type": (int, float),
        "range": (0, 100),    # 电池电量：0% 到 100%
        "unit": "%"
    },
    "signal_strength": {
        "type": (int, float),
        "range": (-120, 0),   # 信号强度：-120dBm 到 0dBm
        "unit": "dBm"
    }
}

# 设备信息验证规则（移除位置信息）
DEVICE_INFO_RULES = {
    "device_id": {
        "type": str,
        "max_length": 64,
        "required": True
    },
    "timestamp": {
        "type": (int, float),
        "required": False
    }
}


def validate_sensor_value(sensor_type: str, value: Any) -> Tuple[bool, str]:
    """
    验证单个传感器数值
    
    Args:
        sensor_type: 传感器类型
        value: 传感器数值
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if sensor_type not in SENSOR_VALIDATION_RULES:
        return False, f"未知的传感器类型: {sensor_type}"
    
    rule = SENSOR_VALIDATION_RULES[sensor_type]
    
    # 检查数据类型
    if not isinstance(value, rule["type"]):
        return False, f"{sensor_type} 数据类型错误，期望 {rule['type']}，实际 {type(value)}"
    
    # 检查数值范围
    min_val, max_val = rule["range"]
    if not (min_val <= value <= max_val):
        return False, f"{sensor_type} 数值超出范围，期望 [{min_val}, {max_val}]，实际 {value}"
    
    return True, ""


def validate_device_info(device_info: Dict[str, Any]) -> Tuple[bool, str]:
    """
    验证设备信息
    
    Args:
        device_info: 设备信息字典
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    for field, rule in DEVICE_INFO_RULES.items():
        if rule.get("required", False) and field not in device_info:
            return False, f"缺少必需字段: {field}"
        
        if field in device_info:
            value = device_info[field]
            
            # 检查数据类型
            if not isinstance(value, rule["type"]):
                return False, f"{field} 数据类型错误，期望 {rule['type']}，实际 {type(value)}"
            
            # 检查字符串长度
            if isinstance(value, str) and "max_length" in rule:
                if len(value) > rule["max_length"]:
                    return False, f"{field} 长度超出限制，最大 {rule['max_length']}，实际 {len(value)}"
    
    return True, ""


def validate_sensor_data(sensor_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证完整的传感器数据
    
    Args:
        sensor_data: 传感器数据字典
        
    Returns:
        Tuple[bool, str, Dict]: (是否有效, 错误信息, 处理后的数据)
    """
    try:
        # 验证基本结构
        if not isinstance(sensor_data, dict):
            return False, "传感器数据必须是字典格式", {}
        
        processed_data = {
            "timestamp": sensor_data.get("timestamp", time.time()),
            "device_info": {},
            "sensor_values": {},
            "validation_status": "success"
        }
        
        # 验证设备信息
        device_info = sensor_data.get("device_info", {})
        is_valid, error_msg = validate_device_info(device_info)
        if not is_valid:
            return False, f"设备信息验证失败: {error_msg}", {}
        
        processed_data["device_info"] = device_info
        
        # 验证传感器数值
        sensor_values = sensor_data.get("sensor_values", {})
        if not isinstance(sensor_values, dict):
            return False, "sensor_values 必须是字典格式", {}
        
        validated_sensors = {}
        for sensor_type, value in sensor_values.items():
            is_valid, error_msg = validate_sensor_value(sensor_type, value)
            if not is_valid:
                return False, f"传感器数据验证失败: {error_msg}", {}
            
            validated_sensors[sensor_type] = {
                "value": value,
                "unit": SENSOR_VALIDATION_RULES[sensor_type]["unit"],
                "timestamp": processed_data["timestamp"]
            }
        
        processed_data["sensor_values"] = validated_sensors
        
        return True, "", processed_data
        
    except Exception as e:
        return False, f"数据处理异常: {str(e)}", {}


async def handleSensorData(conn, sensor_data: Dict[str, Any]):
    """
    处理传感器数据消息
    
    Args:
        conn: WebSocket连接对象
        sensor_data: 传感器数据
    """
    try:
        # 使用新的消息处理函数
        is_success, message, processed_data = handle_sensor_data_message(sensor_data)
        
        if not is_success:
            conn.logger.bind(tag=TAG).error(f"传感器数据处理失败: {message}")
            # 发送错误响应
            error_response = {
                "type": "sensor_data_response",
                "status": "error",
                "message": message,
                "timestamp": time.time()
            }
            await conn.websocket.send(json.dumps(error_response))
            return
        
        # 记录成功接收的传感器数据
        device_id = processed_data["device_info"].get("device_id", "unknown")
        
        conn.logger.bind(tag=TAG).info(
            f"接收到设备 {device_id} 的传感器数据: "
            f"{len(processed_data['sensor_values'])} 个传感器，已发送到后端API"
        )
        
        # 详细记录每个传感器的数值
        for sensor_type, sensor_info in processed_data["sensor_values"].items():
            conn.logger.bind(tag=TAG).debug(
                f"传感器 {sensor_type}: {sensor_info['value']}{sensor_info['unit']}"
            )
        
        # 存储传感器数据到连接对象（可用于后续处理）
        if not hasattr(conn, 'sensor_data_history'):
            conn.sensor_data_history = []
        
        conn.sensor_data_history.append(processed_data)
        
        # 保持最近100条记录
        if len(conn.sensor_data_history) > 100:
            conn.sensor_data_history = conn.sensor_data_history[-100:]
        
        # 发送成功响应
        success_response = {
            "type": "sensor_data_response",
            "status": "success",
            "message": "传感器数据接收并处理成功",
            "device_id": device_id,
            "received_sensors": list(processed_data["sensor_values"].keys()),
            "timestamp": processed_data["timestamp"]
        }
        
        await conn.websocket.send(json.dumps(success_response))
        
    except Exception as e:
        conn.logger.bind(tag=TAG).error(f"处理传感器数据时发生异常: {str(e)}")
        error_response = {
            "type": "sensor_data_response",
            "status": "error",
            "message": f"服务器处理异常: {str(e)}",
            "timestamp": time.time()
        }
        await conn.websocket.send(json.dumps(error_response))


def get_sensor_data_summary(conn) -> Optional[Dict[str, Any]]:
    """
    获取传感器数据摘要
    
    Args:
        conn: WebSocket连接对象
        
    Returns:
        Dict: 传感器数据摘要
    """
    if not hasattr(conn, 'sensor_data_history') or not conn.sensor_data_history:
        return None
    
    latest_data = conn.sensor_data_history[-1]
    
    summary = {
        "device_id": latest_data["device_info"].get("device_id", "unknown"),
        "last_update": latest_data["timestamp"],
        "total_records": len(conn.sensor_data_history),
        "available_sensors": list(latest_data["sensor_values"].keys()),
        "latest_values": {}
    }
    
    for sensor_type, sensor_info in latest_data["sensor_values"].items():
        summary["latest_values"][sensor_type] = {
            "value": sensor_info["value"],
            "unit": sensor_info["unit"]
        }
    
    return summary


def send_sensor_data_to_api(mac_address: str, sensor_data: Dict[str, Any]) -> Optional[Dict]:
    """
    将传感器数据发送到Java后端API
    
    Args:
        mac_address: 设备MAC地址
        sensor_data: 处理后的传感器数据
        
    Returns:
        Dict: API响应结果
    """
    try:
        # 构建API请求数据
        api_data = {
            "timestamp": datetime.fromtimestamp(sensor_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "sensors": []
        }
        
        # 转换传感器数据格式
        for sensor_type, sensor_info in sensor_data["sensor_values"].items():
            sensor_entry = {
                "sensorCode": sensor_type,
                "value": sensor_info["value"]
            }
            api_data["sensors"].append(sensor_entry)
        
        # 使用新的API函数
        response = report_sensor_data(mac_address, api_data)
        
        return response
        
    except Exception as e:
        print(f"发送传感器数据到API失败: {e}")
        return None


def handle_sensor_data_message(message_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    处理WebSocket传感器数据消息
    
    Args:
        message_data: WebSocket消息数据
        
    Returns:
        Tuple[bool, str, Dict]: (是否成功, 消息, 处理后的数据)
    """
    try:
        # 提取MAC地址
        mac_address = message_data.get("mac_address", "")
        if not mac_address:
            return False, "缺少设备MAC地址", {}
        
        # 提取传感器数据
        sensors = message_data.get("sensors", [])
        if not sensors:
            return False, "缺少传感器数据", {}
        
        # 转换为内部格式
        sensor_values = {}
        for sensor in sensors:
            sensor_code = sensor.get("sensor_code", "")
            sensor_value = sensor.get("value")
            
            if sensor_code and sensor_value is not None:
                # 映射传感器代码到内部类型
                sensor_type = map_sensor_code_to_type(sensor_code)
                if sensor_type:
                    sensor_values[sensor_type] = sensor_value
        
        # 构建传感器数据结构
        sensor_data = {
            "device_info": {
                "device_id": mac_address
            },
            "sensor_values": sensor_values,
            "timestamp": message_data.get("timestamp", time.time())
        }
        
        # 验证数据
        is_valid, error_msg, processed_data = validate_sensor_data(sensor_data)
        if not is_valid:
            return False, error_msg, {}
        
        # 发送到Java后端API
        api_response = send_sensor_data_to_api(mac_address, processed_data)
        if api_response is None:
            return False, "发送数据到后端API失败", processed_data
        
        return True, "传感器数据处理成功", processed_data
        
    except Exception as e:
        return False, f"处理传感器数据异常: {str(e)}", {}


def map_sensor_code_to_type(sensor_code: str) -> Optional[str]:
    """
    映射传感器代码到内部类型
    
    Args:
        sensor_code: 传感器代码（如：temp_01, humi_01）
        
    Returns:
        str: 内部传感器类型，如果无法映射则返回None
    """
    # 传感器代码映射规则
    code_mapping = {
        "temp": "temperature",
        "humi": "humidity",
        "light": "light",
        "motion": "motion",
        "air_quality": "air_quality",
        "co2": "co2"
    }
    
    # 提取传感器类型前缀
    for prefix, sensor_type in code_mapping.items():
        if sensor_code.startswith(prefix):
            return sensor_type
    
    # 如果没有匹配，返回原始代码（可能是自定义传感器）
    return sensor_code


# 扩展传感器验证规则 - 严格按照文档定义
SENSOR_VALIDATION_RULES.update({
    "light": {
        "type": (int, float),
        "range": (0, 2000),  # 光照强度：0 到 2000 lux
        "unit": "lux"
    },
    "motion": {
        "type": (int, bool),
        "range": (0, 1),       # 运动检测：0或1
        "unit": ""
    },
    "air_quality": {
        "type": (int, float),
        "range": (0, 500),     # 空气质量指数：0 到 500 ppm
        "unit": "ppm"
    },
    "co2": {
        "type": (int, float),
        "range": (300, 2000),  # CO2浓度：300 到 2000 ppm
        "unit": "ppm"
    }
})