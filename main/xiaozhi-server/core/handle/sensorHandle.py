import json
import time
from typing import Dict, Any, Optional, Tuple

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
        # 验证传感器数据
        is_valid, error_msg, processed_data = validate_sensor_data(sensor_data)
        
        if not is_valid:
            conn.logger.bind(tag=TAG).error(f"传感器数据验证失败: {error_msg}")
            # 发送错误响应
            error_response = {
                "type": "sensor_data_response",
                "status": "error",
                "message": error_msg,
                "timestamp": time.time()
            }
            await conn.websocket.send(json.dumps(error_response))
            return
        
        # 记录成功接收的传感器数据
        device_id = processed_data["device_info"].get("device_id", "unknown")
        
        conn.logger.bind(tag=TAG).info(
            f"接收到设备 {device_id} 的传感器数据: "
            f"{len(processed_data['sensor_values'])} 个传感器"
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
            "message": "传感器数据接收成功",
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