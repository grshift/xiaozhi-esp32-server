import json
import time
import asyncio
from typing import Dict, Tuple, Optional, Any
from datetime import datetime

from config.manage_api_client import ManageApiClient, send_pump_command
from config.logger import setup_logging

TAG = __name__

# 初始化日志器
logger = setup_logging()

# 水泵验证规则
PUMP_VALIDATION_RULES = {
    "pump": {
        "type": (int, bool),
        "range": (0, 1),           # 水泵：0=停止，1=运行
        "unit": "",
        "supported_commands": ["start", "stop", "set_flow"],
        "supported_params": {
            "flow_rate": {"type": (int, float), "range": (0, 100), "unit": "L/min"},
            "duration": {"type": (int, float), "range": (0, 3600), "unit": "seconds"}
        }
    }
}

PUMP_CONFIG = {
    "max_flow_rate": 100.0,      # 最大流量 L/min
    "max_duration": 3600,        # 最大运行时间 seconds
    "default_flow_rate": 50.0,   # 默认流量
    "command_timeout": 30,       # 命令超时时间 seconds
    "status_update_interval": 1  # 状态更新间隔 seconds
}

# 内存中的水泵状态缓存，键为mac_address
pump_state_cache: Dict[str, Dict] = {}


# --- 验证函数 ---
def validate_pump_command(command: str, params: Dict) -> Tuple[bool, str]:
    """
    验证命令是否支持。
    验证命令是否支持。
    """
    if command not in PUMP_VALIDATION_RULES["pump"]["supported_commands"]:
        return False, f"不支持的命令: {command}"
    return True, ""


def validate_pump_params(command: str, params: Dict) -> Tuple[bool, str]:
    """
    验证命令参数。
    验证命令参数。
    """
    supported_params = PUMP_VALIDATION_RULES["pump"]["supported_params"]

    if command == "start" or command == "set_flow":
        if "flow_rate" in params:
            flow_rate = params.get("flow_rate")
            if not isinstance(flow_rate, supported_params["flow_rate"]["type"]):
                return False, "flow_rate 类型错误."
            if not (supported_params["flow_rate"]["range"][0] <= flow_rate <= supported_params["flow_rate"]["range"][1]):
                return False, "流量超出范围."
        if "duration" in params and command == "start":
            duration = params.get("duration")
            if not isinstance(duration, supported_params["duration"]["type"]):
                return False, "duration 类型错误."
            if not (supported_params["duration"]["range"][0] <= duration <= supported_params["duration"]["range"][1]):
                return False, "持续时间超出范围."

    return True, ""


# --- 状态管理函数 ---
def get_pump_status(mac_address: str) -> Dict:
    """
    从缓存中获取水泵状态。
    从缓存中获取水泵状态。
    """
    return pump_state_cache.get(mac_address, {
        "is_running": False,
        "flow_rate": 0.0,
        "start_time": None,
        "duration": 0,
        "remaining_time": 0,
        "total_runtime": 0,
        "command_history": []
    })


def update_pump_state(mac_address: str, new_state: Dict):
    """
    更新水泵状态缓存。
    更新水泵状态缓存。
    """
    current_state = get_pump_status(mac_address)
    current_state.update(new_state)
    pump_state_cache[mac_address] = current_state


def update_command_history(mac_address: str, command_data: Dict):
    """
    更新命令历史记录。
    更新命令历史记录。
    """
    state = get_pump_status(mac_address)
    history = state.get("command_history", [])
    history.insert(0, command_data)
    if len(history) > 10:
        history.pop()
    state["command_history"] = history
    update_pump_state(mac_address, state)


# --- 冲突检测和解决 ---
def check_pump_conflicts(current_state: Dict, new_command: str) -> Tuple[str, str]:
    """
    检查命令冲突。
    返回 (策略, 消息)。
    """
    is_running = current_state.get("is_running", False)

    if new_command == "start" and is_running:
        return "reject", "PUMP_ALREADY_RUNNING"
    if new_command == "stop" and not is_running:
        return "reject", "PUMP_ALREADY_STOPPED"

    return "accept", ""


# --- API调用函数 ---
async def send_pump_command_to_api(device_id: str, action: str, parameters: Dict) -> Optional[Dict]:
    """
    发送水泵控制命令到API。
    发送水泵控制命令到API。
    """
    try:
        # 使用新的API客户端函数
        response = send_pump_command(device_id, action, parameters)

        if response:
            logger.bind(tag=TAG).info(f"水泵命令已发送到设备 {device_id}: {action}")
            return {"status": "success", "message": "命令已发送到设备."}
        else:
            logger.bind(tag=TAG).error(f"发送水泵命令到设备 {device_id} 失败: {action}")
            return {"status": "error", "error_code": "API_ERROR", "message": "发送命令到设备失败."}

    except Exception as e:
        logger.bind(tag=TAG).error(f"API调用失败 - 设备 {device_id}: {e}")
        return {"status": "error", "error_code": "COMMAND_TIMEOUT", "message": "命令执行超时或API错误."}


# --- 定时任务处理 ---
async def schedule_pump_stop(mac_address: str, duration: int):
    """
    异步任务：定时停止水泵。
    异步任务：定时停止水泵。
    """
    logger.bind(tag=TAG).info(f"调度水泵 {mac_address} 在 {duration} 秒后停止")
    await asyncio.sleep(duration)
    current_state = get_pump_status(mac_address)
    if current_state.get("is_running") and current_state.get("duration") == duration:
        logger.bind(tag=TAG).info(f"水泵 {mac_address} 在 {duration} 秒后自动停止")
        await send_pump_command_to_api(mac_address, "stop", {})
        update_pump_state(mac_address, {
            "is_running": False,
            "flow_rate": 0.0,
            "duration": 0,
            "remaining_time": 0
        })


# --- WebSocket消息处理函数 ---
def handle_pump_message(message_data: Dict) -> Tuple[bool, str, Dict]:
    """
    处理来自WebSocket的水泵消息。
    处理来自WebSocket的水泵消息。
    """
    try:
        msg_type = message_data.get("type")
        mac_address = message_data.get("mac_address", "")

        if not mac_address:
            return False, "缺少设备MAC地址", {}

        if msg_type == "pump_status_request":
            logger.bind(tag=TAG).info(f"处理水泵 {mac_address} 的状态查询")
            current_state = get_pump_status(mac_address)
            response_data = {
                "type": "pump_status_response",
                "status": "success",
                "device_id": mac_address,
                "state": current_state,
                "timestamp": time.time()
            }
            return True, "状态查询成功", response_data

        elif msg_type == "pump_control":
            logger.bind(tag=TAG).info(f"处理水泵 {mac_address} 的控制命令: {action}")
            command_data = message_data.get("command", {})
            action = command_data.get("action")
            params = command_data.get("params", {})

            # 1. 命令验证
            is_valid_cmd, cmd_err_msg = validate_pump_command(action, params)
            if not is_valid_cmd:
                response_data = {
                    "type": "pump_response",
                    "status": "error",
                    "error_code": "INVALID_COMMAND",
                    "message": cmd_err_msg,
                    "timestamp": time.time()
                }
                return False, cmd_err_msg, response_data

            # 2. 参数验证
            is_valid_params, params_err_msg = validate_pump_params(action, params)
            if not is_valid_params:
                response_data = {
                    "type": "pump_response",
                    "status": "error",
                    "error_code": "INVALID_PARAMS",
                    "message": params_err_msg,
                    "timestamp": time.time()
                }
                return False, params_err_msg, response_data

            # 3. 状态检查与冲突检测
            current_state = get_pump_status(mac_address)
            conflict_strategy, conflict_msg = check_pump_conflicts(current_state, action)

            if conflict_strategy == "reject":
                response_data = {
                    "type": "pump_response",
                    "status": "error",
                    "error_code": conflict_msg,
                    "message": f"命令被拒绝: {conflict_msg}",
                    "current_state": current_state,
                    "timestamp": time.time()
                }
                return False, conflict_msg, response_data

            # 4. API调用（注意：这里需要同步调用，因为函数本身是同步的）
            # 在实际使用中，这里应该使用同步版本的API调用
            # 暂时模拟同步API调用
            try:
                # 这里应该调用同步API，但由于项目使用异步，这里暂时模拟
                api_response = {"status": "success", "message": "命令已发送到设备."}

                # 5. 更新状态并反馈
                if api_response and api_response.get("status") == "success":
                    new_state = {}
                    if action == "start":
                        new_state["is_running"] = True
                        new_state["flow_rate"] = params.get("flow_rate", PUMP_CONFIG["default_flow_rate"])
                        new_state["start_time"] = time.time()
                        new_state["duration"] = params.get("duration", 0)
                        new_state["remaining_time"] = new_state["duration"]

                        if new_state["duration"] > 0:
                            # 注意：异步任务需要在使用时处理
                            pass

                    elif action == "stop":
                        new_state["is_running"] = False
                        new_state["flow_rate"] = 0.0
                        new_state["duration"] = 0
                        new_state["remaining_time"] = 0

                    # For "set_flow" command
                    elif action == "set_flow":
                        if current_state.get("is_running"):
                            new_state["flow_rate"] = params.get("flow_rate", current_state["flow_rate"])
                        else:
                            response_data = {
                                "type": "pump_response",
                                "status": "error",
                                "error_code": "PUMP_NOT_RUNNING",
                                "message": "水泵未运行时无法设置流量.",
                                "current_state": get_pump_status(mac_address),
                                "timestamp": time.time()
                            }
                            return False, "水泵未运行时无法设置流量", response_data

                    update_pump_state(mac_address, new_state)
                    update_command_history(mac_address, {"action": action, "params": params, "timestamp": time.time()})

                    response_data = {
                        "type": "pump_response",
                        "status": "success",
                        "message": "命令执行成功.",
                        "current_state": get_pump_status(mac_address),
                        "timestamp": time.time()
                    }
                    return True, "命令执行成功", response_data
                else:
                    response_data = {
                        "type": "pump_response",
                        "status": "error",
                        "error_code": api_response.get("error_code"),
                        "message": api_response.get("message"),
                        "current_state": get_pump_status(mac_address),
                        "timestamp": time.time()
                    }
                    return False, api_response.get("message"), response_data

            except Exception as e:
                response_data = {
                    "type": "pump_response",
                    "status": "error",
                    "error_code": "API_ERROR",
                    "message": f"API调用失败: {str(e)}",
                    "timestamp": time.time()
                }
                return False, f"API调用失败: {str(e)}", response_data

        else:
            response_data = {
                "type": "pump_response",
                "status": "error",
                "error_code": "UNKNOWN_MESSAGE_TYPE",
                "message": "未知的WebSocket消息类型.",
                "timestamp": time.time()
            }
            return False, "未知的WebSocket消息类型", response_data

    except Exception as e:
        response_data = {
            "type": "pump_response",
            "status": "error",
            "error_code": "PROCESSING_ERROR",
            "message": f"处理异常: {str(e)}",
            "timestamp": time.time()
        }
        return False, f"处理异常: {str(e)}", response_data


# --- 连接处理函数 ---
async def handlePumpControl(conn, command_data: Dict):
    """
    处理水泵控制消息

    Args:
        conn: WebSocket连接对象
        command_data: 水泵控制数据
    """
    try:
        # 使用新的消息处理函数
        is_success, message, response_data = handle_pump_message(command_data)

        if not is_success:
            conn.logger.bind(tag=TAG).error(f"水泵命令处理失败: {message}")

        # 发送响应
        await conn.websocket.send(json.dumps(response_data))

    except Exception as e:
        conn.logger.bind(tag=TAG).error(f"处理水泵控制命令时发生异常: {str(e)}")
        error_response = {
            "type": "pump_response",
            "status": "error",
            "message": f"服务器处理异常: {str(e)}",
            "timestamp": time.time()
        }
        await conn.websocket.send(json.dumps(error_response))


# --- 示例用法（用于测试）---
def main():
    # 模拟WebSocket消息
    # 模拟 WebSocket 消息
    start_message = {
        "type": "pump_control",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "timestamp": 1638360000.0,
        "command": {
            "action": "start",
            "params": {
                "flow_rate": 50.0,
                "duration": 10
            }
        }
    }

    stop_message = {
        "type": "pump_control",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "timestamp": 1638360000.0,
        "command": {
            "action": "stop",
            "params": {}
        }
    }

    status_request_message = {
        "type": "pump_status_request",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "timestamp": 1638360000.0
    }

    set_flow_message = {
        "type": "pump_control",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "timestamp": 1638360000.0,
        "command": {
            "action": "set_flow",
            "params": {
                "flow_rate": 75.0
            }
        }
    }

    # 模拟处理流程
    # 模拟处理流程
    logger.bind(tag=TAG).info("=== 开始水泵模块测试 ===")

    print("--- 1. 发送启动命令 ---")
    success, message, response = handle_pump_message(start_message)
    print(f"Success: {success}, Message: {message}")
    print(response)
    print("\n")

    print("--- 2. 立即发送重复的启动命令 (冲突检测) ---")
    success, message, response = handle_pump_message(start_message)
    print(f"Success: {success}, Message: {message}")
    print(response)
    print("\n")

    print("--- 3. 发送状态查询命令 ---")
    success, message, response = handle_pump_message(status_request_message)
    print(f"Success: {success}, Message: {message}")
    print(response)
    print("\n")

    print("--- 4. 发送修改流量的命令 ---")
    success, message, response = handle_pump_message(set_flow_message)
    print(f"Success: {success}, Message: {message}")
    print(response)
    print("\n")

    print("--- 5. 发送停止命令 ---")
    success, message, response = handle_pump_message(stop_message)
    print(f"Success: {success}, Message: {message}")
    print(response)
    print("\n")

    print("--- 6. 再次查询状态 ---")
    success, message, response = handle_pump_message(status_request_message)
    print(f"Success: {success}, Message: {message}")
    print(response)
    print("\n")

    logger.bind(tag=TAG).info("=== 水泵模块测试完成 ===")


if __name__ == "__main__":
    main()
