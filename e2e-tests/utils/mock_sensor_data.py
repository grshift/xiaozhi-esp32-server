import asyncio
import websockets
import json
import time
import random

# 定义用于测试的唯一传感器ID
TEST_DEVICE_ID = "sensor-e2e-test-01"

# 为所有传感器指标生成唯一的、可预测的测试值
TEST_VALUES = {
    "temperature": round(random.uniform(20.0, 30.0), 2),
    "humidity": round(random.uniform(40.0, 60.0), 1),
    "battery_level": random.randint(80, 100),
    "signal_strength": random.randint(-60, -40)
}

# 你的 Python WebSocket 服务的地址
SERVER_URL = f"ws://localhost:8000/xiaozhi/v1/?device-id={TEST_DEVICE_ID}&client-id={TEST_DEVICE_ID}"

async def send_single_sensor_reading():
    """
    连接到 WebSocket 服务器, 发送一条包含所有指标的传感器数据, 然后断开.
    """
    print(f"尝试连接到服务器: {SERVER_URL}")
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print("✅ WebSocket 连接成功.")
            
            # 1. 发送 hello 消息
            hello_message = {
                "type": "hello",
                "version": 1,
                "features": {"mcp": True, "sensor_data": True}
            }
            await websocket.send(json.dumps(hello_message))
            response = await websocket.recv()
            print(f"📥 服务器对 hello 的响应: {response}")

            # 2. 构造并发送包含所有唯一测试值的传感器数据
            sensor_data_payload = {
                "type": "sensor_data",
                "timestamp": time.time(),
                "device_info": {
                    "device_id": TEST_DEVICE_ID
                },
                "sensor_values": TEST_VALUES
            }
            await websocket.send(json.dumps(sensor_data_payload))
            response = await websocket.recv()
            print(f"📤 成功发送传感器数据: {TEST_VALUES}")
            print(f"📥 服务器对 sensor_data 的响应: {response}")

            # 3. 将生成的测试值作为一个 JSON 字符串打印到标准输出, 供 Playwright 捕获
            # 使用一个唯一的前缀 E2E_TEST_VALUES= 来确保我们能准确解析
            print(f"E2E_TEST_VALUES={json.dumps(TEST_VALUES)}")

    except Exception as e:
        print(f"❌ E2E 模拟脚本执行失败: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(send_single_sensor_reading())
