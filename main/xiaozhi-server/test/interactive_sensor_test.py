import asyncio
import websockets
import json
import time


async def interactive_test():
    """
    交互式传感器数据测试
    """
    # Add required device-id and client-id parameters
    device_id = "ESP32_INTERACTIVE_TEST"
    server_url = f"ws://localhost:8000/xiaozhi/v1/?device-id={device_id}&client-id={device_id}"
    try:
        # 连接到服务器
        websocket = await websockets.connect(server_url)
        print(f"✅ 已连接到服务器: {server_url}")
        
        # 发送hello消息
        hello_message = {
            "type": "hello",
            "version": 1,
            "features": {"mcp": True, "sensor_data": True},
            "transport": "websocket",
            "audio_params": {"format": "pcm"}
        }
        await websocket.send(json.dumps(hello_message))
        response = await websocket.recv()
        print(f"📥 服务器响应: {response}")
        
        # 发送正常传感器数据
        print("\n📤 发送正常传感器数据...")
        normal_data = {
            "type": "sensor_data",
            "timestamp": time.time(),
            "device_info": {
                "device_id": "ESP32_INTERACTIVE_TEST"
            },
            "sensor_values": {
                "temperature": 23.5,
                "humidity": 65.2,
                "battery_level": 85,
                "signal_strength": -45
            }
        }
        await websocket.send(json.dumps(normal_data))
        response = await websocket.recv()
        print(f"📥 服务器响应: {response}")
        
        # 发送无效数据测试（温度超出范围）
        print("\n🧪 发送无效数据测试（温度超出范围）...")
        invalid_data = {
            "type": "sensor_data",
            "timestamp": time.time(),
            "device_info": {
                "device_id": "ESP32_INTERACTIVE_TEST"
            },
            "sensor_values": {
                "temperature": 150.0,  # 超出范围
                "humidity": 65.0
            }
        }
        await websocket.send(json.dumps(invalid_data))
        response = await websocket.recv()
        print(f"📥 服务器响应: {response}")
        
        # 测试缺少必需字段（缺少device_id）
        print("\n🧪 发送缺少设备ID的数据...")
        missing_id_data = {
            "type": "sensor_data",
            "timestamp": time.time(),
            "device_info": {
                # 缺少 device_id
            },
            "sensor_values": {
                "temperature": 25.0,
                "humidity": 60.0
            }
        }
        await websocket.send(json.dumps(missing_id_data))
        response = await websocket.recv()
        print(f"📥 服务器响应: {response}")
        
        # 测试负湿度（无效数据）
        print("\n🧪 发送负湿度数据（无效）...")
        negative_humidity_data = {
            "type": "sensor_data",
            "timestamp": time.time(),
            "device_info": {
                "device_id": "ESP32_INVALID_TEST"
            },
            "sensor_values": {
                "temperature": 24.8,
                "humidity": -10.0,  # 负湿度，无效
                "battery_level": 92,
                "signal_strength": -38
            }
        }
        await websocket.send(json.dumps(negative_humidity_data))
        response = await websocket.recv()
        print(f"📥 服务器响应: {response}")
        
        # 测试电池电量超出范围
        print("\n🧪 发送电池电量超出范围数据...")
        over_battery_data = {
            "type": "sensor_data",
            "timestamp": time.time(),
            "device_info": {
                "device_id": "ESP32_BATTERY_TEST"
            },
            "sensor_values": {
                "temperature": 25.0,
                "humidity": 60.0,
                "battery_level": 150,  # 超出0-100范围
                "signal_strength": -45
            }
        }
        await websocket.send(json.dumps(over_battery_data))
        response = await websocket.recv()
        print(f"📥 服务器响应: {response}")
        
        await websocket.close()
        print("\n🔌 连接已关闭")
        print("✅ 所有测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    print("🔧 交互式传感器数据测试")
    print("请确保xiaozhi-server正在运行...")
    asyncio.run(interactive_test())