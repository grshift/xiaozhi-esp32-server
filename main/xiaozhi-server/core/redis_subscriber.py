#!/usr/bin/env python3
"""
Redis订阅器模块
用于接收来自Java API的设备控制命令，并转发给WebSocket客户端
"""

import asyncio
import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class DeviceControlSubscriber:
    """设备控制命令Redis订阅器"""

    def __init__(self, redis_config: Dict[str, Any], websocket_server):
        self.redis_config = redis_config
        self.websocket_server = websocket_server
        self.redis_client = None
        self.pubsub = None
        self.running = False

    async def connect(self):
        """连接到Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_config.get("host", "127.0.0.1"),
                port=self.redis_config.get("port", 6379),
                password=self.redis_config.get("password"),
                db=self.redis_config.get("database", 0),
                decode_responses=True
            )

            # 测试连接
            await self.redis_client.ping()
            logger.bind(tag=TAG).info("Redis连接成功")

            # 创建发布订阅对象
            self.pubsub = self.redis_client.pubsub()

        except Exception as e:
            logger.bind(tag=TAG).error(f"Redis连接失败: {e}")
            raise

    async def subscribe(self):
        """订阅设备控制频道"""
        if not self.pubsub:
            raise Exception("Redis连接未建立")

        try:
            await self.pubsub.subscribe("device_control_channel")
            logger.bind(tag=TAG).info("已订阅设备控制频道: device_control_channel")
            self.running = True

            # 开始监听消息
            await self._listen_messages()

        except Exception as e:
            logger.bind(tag=TAG).error(f"订阅频道失败: {e}")
            raise

    async def _listen_messages(self):
        """监听并处理消息"""
        while self.running:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message:
                    await self._handle_message(message)

            except Exception as e:
                logger.bind(tag=TAG).error(f"监听消息时出错: {e}")
                await asyncio.sleep(1)  # 避免频繁重试

    async def _handle_message(self, message: Dict[str, Any]):
        """处理接收到的消息"""
        try:
            if message.get("type") == "message":
                data = json.loads(message.get("data", "{}"))
                logger.bind(tag=TAG).info(f"收到设备控制命令: {data}")

                await self._process_control_command(data)

        except json.JSONDecodeError as e:
            logger.bind(tag=TAG).error(f"解析消息失败: {e}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"处理消息失败: {e}")

    async def _process_control_command(self, command_data: Dict[str, Any]):
        """处理控制命令"""
        try:
            device_id = command_data.get("deviceId")
            actuator_code = command_data.get("actuatorCode")
            action = command_data.get("action")
            parameters = command_data.get("parameters", {})
            timestamp = command_data.get("timestamp")

            if not device_id or not actuator_code or not action:
                logger.bind(tag=TAG).error(f"控制命令参数不完整: {command_data}")
                return

            # 构造WebSocket消息
            ws_message = {
                "type": "pump_control",
                "mac_address": device_id,  # 假设device_id就是MAC地址
                "timestamp": timestamp or asyncio.get_event_loop().time(),
                "command": {
                    "action": action,
                    "params": parameters
                }
            }

            # 通过WebSocket服务器发送给对应的设备
            success = await self.websocket_server.send_to_device(device_id, ws_message)

            if success:
                logger.bind(tag=TAG).info(f"控制命令已转发给设备 {device_id}: {action}")
            else:
                logger.bind(tag=TAG).warning(f"转发控制命令失败，设备 {device_id} 可能不在线")

        except Exception as e:
            logger.bind(tag=TAG).error(f"处理控制命令失败: {e}")

    async def unsubscribe(self):
        """取消订阅"""
        self.running = False
        if self.pubsub:
            await self.pubsub.unsubscribe("device_control_channel")
            logger.bind(tag=TAG).info("已取消订阅设备控制频道")

    async def close(self):
        """关闭连接"""
        await self.unsubscribe()
        if self.redis_client:
            await self.redis_client.close()
            logger.bind(tag=TAG).info("Redis连接已关闭")


class DeviceControlManager:
    """设备控制管理器"""

    def __init__(self, websocket_server):
        self.websocket_server = websocket_server
        self.subscriber = None
        self.redis_config = None

    def initialize(self, config: Dict[str, Any]):
        """初始化Redis配置"""
        self.redis_config = config.get("data", {}).get("redis", {
            "host": "127.0.0.1",
            "port": 6379,
            "password": None,
            "database": 0
        })

    async def start(self):
        """启动订阅器"""
        if not self.redis_config:
            logger.bind(tag=TAG).warning("Redis配置未设置，跳过设备控制订阅")
            return

        try:
            self.subscriber = DeviceControlSubscriber(self.redis_config, self.websocket_server)
            await self.subscriber.connect()
            await self.subscriber.subscribe()

            logger.bind(tag=TAG).info("设备控制订阅器已启动")

        except Exception as e:
            logger.bind(tag=TAG).error(f"启动设备控制订阅器失败: {e}")

    async def stop(self):
        """停止订阅器"""
        if self.subscriber:
            await self.subscriber.close()
            logger.bind(tag=TAG).info("设备控制订阅器已停止")
