import asyncio
import websockets
import json
import time
import random
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ESP32SensorSimulator:
    """
    ESP32传感器数据模拟器
    用于生成和发送模拟的传感器数据到WebSocket服务器
    """
    
    def __init__(self, device_id: str, server_url: str = None):
        self.device_id = device_id
        # Add device-id and client-id as query parameters
        if server_url is None:
            self.server_url = f"ws://localhost:8000/xiaozhi/v1/?device-id={device_id}&client-id={device_id}"
        else:
            # If custom URL provided, append the required parameters
            separator = "&" if "?" in server_url else "?"
            self.server_url = f"{server_url}{separator}device-id={device_id}&client-id={device_id}"
        self.websocket = None
        self.is_connected = False
        self.is_running = False
        
        # 传感器数据范围
        self.sensor_ranges = {
            "temperature": {"min": -10.0, "max": 50.0, "normal_min": 15.0, "normal_max": 35.0},
            "humidity": {"min": 0.0, "max": 100.0, "normal_min": 30.0, "normal_max": 80.0},
            "battery_level": {"min": 0, "max": 100, "normal_min": 20, "normal_max": 100},
            "signal_strength": {"min": -100, "max": -30, "normal_min": -80, "normal_max": -40}
        }
    
    async def connect(self) -> bool:
        """
        连接到WebSocket服务器
        """
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.is_connected = True
            logger.info(f"✅ 设备 {self.device_id} 已连接到服务器: {self.server_url}")
            
            # 发送hello消息
            await self._send_hello_message()
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            self.is_connected = False
            return False
    
    async def _send_hello_message(self):
        """
        发送hello消息到服务器
        """
        hello_message = {
            "type": "hello",
            "version": 1,
            "features": {"mcp": True, "sensor_data": True},
            "transport": "websocket",
            "audio_params": {"format": "pcm"},
            "device_info": {
                "device_id": self.device_id,
                "device_type": "ESP32",
                "firmware_version": "1.0.0"
            }
        }
        
        try:
            await self.websocket.send(json.dumps(hello_message))
            response = await self.websocket.recv()
            logger.info(f"📥 服务器响应: {response}")
        except Exception as e:
            logger.error(f"❌ 发送hello消息失败: {e}")
    
    def generate_normal_sensor_data(self) -> Dict[str, Any]:
        """
        生成正常范围内的传感器数据
        """
        temp_range = self.sensor_ranges["temperature"]
        humidity_range = self.sensor_ranges["humidity"]
        battery_range = self.sensor_ranges["battery_level"]
        signal_range = self.sensor_ranges["signal_strength"]
        
        return {
            "timestamp": time.time(),
            "device_info": {
                "device_id": self.device_id
            },
            "sensor_values": {
                "temperature": round(random.uniform(temp_range["normal_min"], temp_range["normal_max"]), 1),
                "humidity": round(random.uniform(humidity_range["normal_min"], humidity_range["normal_max"]), 1),
                "battery_level": random.randint(battery_range["normal_min"], battery_range["normal_max"]),
                "signal_strength": random.randint(signal_range["normal_min"], signal_range["normal_max"])
            }
        }
    
    def generate_invalid_sensor_data(self) -> Dict[str, Any]:
        """
        生成无效的传感器数据（用于测试错误处理）
        """
        invalid_types = [
            "extreme_temperature",
            "negative_humidity",
            "over_humidity",
            "negative_battery",
            "over_battery",
            "missing_device_id",
            "invalid_timestamp"
        ]
        
        invalid_type = random.choice(invalid_types)
        base_data = self.generate_normal_sensor_data()
        
        if invalid_type == "extreme_temperature":
            base_data["sensor_values"]["temperature"] = random.choice([-50.0, 100.0])
        elif invalid_type == "negative_humidity":
            base_data["sensor_values"]["humidity"] = -10.0
        elif invalid_type == "over_humidity":
            base_data["sensor_values"]["humidity"] = 150.0
        elif invalid_type == "negative_battery":
            base_data["sensor_values"]["battery_level"] = -10
        elif invalid_type == "over_battery":
            base_data["sensor_values"]["battery_level"] = 150
        elif invalid_type == "missing_device_id":
            del base_data["device_info"]["device_id"]
        elif invalid_type == "invalid_timestamp":
            base_data["timestamp"] = "invalid_timestamp"
        
        return base_data
    
    async def send_sensor_data(self, data: Dict[str, Any]) -> Optional[str]:
        """
        发送传感器数据到服务器
        """
        if not self.is_connected or not self.websocket:
            logger.error("❌ 未连接到服务器")
            return None
        
        # 直接发送数据，不包装在data字段中
        message = {
            "type": "sensor_data",
            **data  # 展开数据字段
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            response = await self.websocket.recv()
            device_id = data.get('device_info', {}).get('device_id', 'Unknown')
            temperature = data.get('sensor_values', {}).get('temperature', 'N/A')
            logger.info(f"📤 发送数据: {device_id} - 温度: {temperature}°C")
            logger.info(f"📥 服务器响应: {response}")
            return response
        except Exception as e:
            logger.error(f"❌ 发送数据失败: {e}")
            return None
    
    async def start_continuous_sending(self, interval: float = 5.0, include_invalid: bool = False, invalid_ratio: float = 0.1):
        """
        开始连续发送传感器数据
        
        Args:
            interval: 发送间隔（秒）
            include_invalid: 是否包含无效数据
            invalid_ratio: 无效数据的比例（0.0-1.0）
        """
        if not self.is_connected:
            logger.error("❌ 请先连接到服务器")
            return
        
        self.is_running = True
        logger.info(f"🚀 开始连续发送数据，间隔: {interval}秒")
        
        try:
            while self.is_running:
                # 决定发送正常数据还是无效数据
                if include_invalid and random.random() < invalid_ratio:
                    data = self.generate_invalid_sensor_data()
                    logger.info("🧪 发送无效数据进行测试")
                else:
                    data = self.generate_normal_sensor_data()
                
                await self.send_sensor_data(data)
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"❌ 连续发送过程中出错: {e}")
        finally:
            self.is_running = False
    
    def stop(self):
        """
        停止连续发送
        """
        self.is_running = False
        logger.info("⏹️ 停止连续发送")
    
    async def disconnect(self):
        """
        断开与服务器的连接
        """
        self.stop()
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info(f"🔌 设备 {self.device_id} 已断开连接")


async def test_single_device():
    """
    测试单个设备的传感器数据发送
    """
    simulator = ESP32SensorSimulator("ESP32_TEST_001")
    
    try:
        # 连接到服务器
        if await simulator.connect():
            # 发送几条正常数据
            for i in range(3):
                data = simulator.generate_normal_sensor_data()
                await simulator.send_sensor_data(data)
                await asyncio.sleep(2)
            
            # 发送一条无效数据
            invalid_data = simulator.generate_invalid_sensor_data()
            await simulator.send_sensor_data(invalid_data)
            
        await simulator.disconnect()
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")


async def test_multiple_devices():
    """
    测试多个设备同时发送数据
    """
    devices = [
        ESP32SensorSimulator(f"ESP32_MULTI_{i:03d}")
        for i in range(1, 4)  # 创建3个设备
    ]
    
    try:
        # 连接所有设备
        connect_tasks = [device.connect() for device in devices]
        results = await asyncio.gather(*connect_tasks)
        
        connected_devices = [device for device, connected in zip(devices, results) if connected]
        logger.info(f"✅ 成功连接 {len(connected_devices)} 个设备")
        
        # 开始连续发送（包含无效数据）
        send_tasks = [
            device.start_continuous_sending(interval=3.0, include_invalid=True, invalid_ratio=0.2)
            for device in connected_devices
        ]
        
        # 运行10秒后停止
        await asyncio.sleep(10)
        
        # 停止所有设备
        for device in connected_devices:
            device.stop()
        
        # 等待发送任务完成
        await asyncio.gather(*send_tasks, return_exceptions=True)
        
        # 断开所有连接
        disconnect_tasks = [device.disconnect() for device in connected_devices]
        await asyncio.gather(*disconnect_tasks)
        
    except Exception as e:
        logger.error(f"❌ 多设备测试失败: {e}")


async def interactive_menu():
    """
    交互式菜单
    """
    print("\n🔧 ESP32传感器模拟器")
    print("请选择测试模式:")
    print("1. 单设备测试")
    print("2. 多设备测试")
    print("3. 自定义设备测试")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 开始单设备测试...")
                await test_single_device()
                print("✅ 单设备测试完成")
                
            elif choice == "2":
                print("\n🚀 开始多设备测试...")
                await test_multiple_devices()
                print("✅ 多设备测试完成")
                
            elif choice == "3":
                device_id = input("请输入设备ID: ").strip()
                if not device_id:
                    device_id = "ESP32_CUSTOM"
                
                interval = input("请输入发送间隔（秒，默认5）: ").strip()
                try:
                    interval = float(interval) if interval else 5.0
                except ValueError:
                    interval = 5.0
                
                include_invalid = input("是否包含无效数据测试？(y/n，默认n): ").strip().lower() == 'y'
                
                simulator = ESP32SensorSimulator(device_id)
                if await simulator.connect():
                    print(f"\n🚀 开始发送数据，按Ctrl+C停止...")
                    try:
                        await simulator.start_continuous_sending(
                            interval=interval,
                            include_invalid=include_invalid,
                            invalid_ratio=0.1
                        )
                    except KeyboardInterrupt:
                        print("\n⏹️ 用户中断")
                    finally:
                        await simulator.disconnect()
                
            elif choice == "4":
                print("👋 再见！")
                break
                
            else:
                print("❌ 无效选择，请输入1-4")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            logger.error(f"❌ 操作失败: {e}")


if __name__ == "__main__":
    print("🔧 ESP32传感器数据模拟器")
    print("请确保xiaozhi-server正在运行...")
    
    try:
        asyncio.run(interactive_menu())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")