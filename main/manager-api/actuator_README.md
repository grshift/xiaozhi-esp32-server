# 执行器模块 (Actuator Module)

## 概述

执行器模块提供了对设备执行器（如水泵、阀门、开关等）的控制和管理功能。该模块遵循项目现有的架构模式，提供了完整的CRUD操作、状态管理、日志记录等功能。

## 功能特性

- **执行器管理**: 支持多种类型的执行器配置和管理
- **命令控制**: 提供统一的命令发送接口，支持参数化控制
- **状态监控**: 实时监控执行器状态，支持缓存优化
- **操作日志**: 完整的操作历史记录，便于追踪和调试
- **事务保障**: 重要的控制操作具有事务保障
- **缓存支持**: 使用Redis缓存提升查询性能

## 核心API接口

### 水泵控制相关接口

#### 1. 发送水泵控制命令
```
POST /xiaozhi/pump/control
Content-Type: application/json

{
    "deviceId": "device-uuid-123",
    "actuatorCode": "pump_01",
    "action": "start",
    "parameters": {
        "flowRate": 50.0,
        "duration": 300
    }
}
```

**支持的命令(action)**:
- `start`: 启动水泵
- `stop`: 停止水泵
- `set_flow`: 设置流量（仅在运行时有效）

**参数说明**:
- `flowRate`: 流量 (L/min)，范围: 0-100
- `duration`: 持续时间 (秒)，范围: 0-3600

#### 2. 获取水泵状态
```
GET /xiaozhi/pump/status/{deviceId}
```

#### 3. 获取水泵操作历史
```
GET /xiaozhi/pump/history/{deviceId}?current=1&size=10
```

## 数据库表结构

模块包含以下三个核心表：

1. **ai_actuator_type**: 执行器类型定义表
2. **ai_device_actuator**: 设备执行器配置表
3. **ai_actuator_data**: 执行器数据日志表

## 使用说明

### 1. 数据库初始化
执行 `main/manager-api/src/main/resources/db/changelog/actuator_tables.sql` 来创建所需的数据库表。

### 2. 集成到现有设备
1. 为设备添加执行器配置记录到 `ai_device_actuator` 表
2. 确保执行器类型在 `ai_actuator_type` 表中存在
3. 调用相应的API接口进行控制

### 3. 扩展新的执行器类型
1. 在 `ai_actuator_type` 表中添加新的执行器类型
2. 根据需要扩展DTO和业务逻辑
3. 添加相应的控制器方法

## 架构特点

- **分层架构**: 严格遵循Controller -> Service -> DAO的分层模式
- **依赖注入**: 使用Spring的依赖注入管理组件关系
- **异常处理**: 统一的异常处理机制
- **缓存策略**: Redis缓存提升性能
- **事务管理**: 重要操作的事务保障
- **API文档**: 完整的Swagger注解支持

## 与Python客户端集成

Python客户端 (`manage_api_client.py`) 已更新以支持新的Java API接口：

```python
# 发送水泵控制命令
result = send_pump_command(device_id, "start", {"flowRate": 50.0, "duration": 300})

# 获取水泵状态
status = get_pump_status(device_id)

# 获取操作历史
history = get_pump_history(device_id, limit=10)
```

## 注意事项

1. **设备通信**: 当前实现中，`sendCommandToDevice` 方法只是记录日志。实际部署时需要集成真实的设备通信机制（如MQTT、WebSocket等）。

2. **缓存清理**: 控制命令执行后会自动清理相关缓存，确保状态查询的实时性。

3. **参数验证**: API层已实现基础参数验证，复杂的业务验证可在Service层扩展。

4. **权限控制**: 当前实现未包含权限控制，实际使用时可根据项目需要添加相应的权限注解。

## 设备通信集成

### Redis发布订阅机制

系统通过Redis发布订阅机制实现Java API与Python WebSocket服务器之间的通信：

#### Java端实现
- 在 `ActuatorControlServiceImpl.sendCommandToDevice()` 方法中将控制命令发布到Redis频道
- 使用频道名：`device_control_channel`
- 消息格式：
```json
{
  "deviceId": "设备ID",
  "actuatorCode": "执行器编码",
  "action": "控制命令",
  "parameters": {...},
  "timestamp": 1234567890
}
```

#### Python端实现
- `redis_subscriber.py`: Redis订阅器模块
- `DeviceControlSubscriber`: 订阅设备控制命令并转发给WebSocket客户端
- `WebSocketServer.send_to_device()`: 向指定设备发送消息

#### 通信流程
```
Java API → Redis发布 → Python订阅器 → WebSocket消息 → ESP32设备
```

### 部署说明

#### 1. 依赖安装
```bash
# Python端
cd main/xiaozhi-server
pip install -r requirements.txt
```

#### 2. 配置检查
确保Redis配置正确：
- Java: `application-dev.yml` 中的Redis配置
- Python: `config.yaml` 中的Redis配置

#### 3. 启动顺序
1. 启动Redis服务器
2. 启动Java Spring Boot应用
3. 启动Python WebSocket服务器

## API测试

### 控制命令测试
```bash
# 启动水泵
curl -X POST "http://localhost:8002/xiaozhi/pump/control" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test-device-001",
    "actuatorCode": "pump_01",
    "action": "start",
    "parameters": {"flowRate": 50.0, "duration": 300}
  }'

# 停止水泵
curl -X POST "http://localhost:8002/xiaozhi/pump/control" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test-device-001",
    "actuatorCode": "pump_01",
    "action": "stop",
    "parameters": {}
  }'
```

### 状态查询测试
```bash
curl -X GET "http://localhost:8002/xiaozhi/pump/status/test-device-001"
```

### 历史查询测试
```bash
curl -X GET "http://localhost:8002/xiaozhi/pump/history/test-device-001?current=1&size=10"
```

## 扩展建议

1. **消息队列集成**: 将控制命令发送到消息队列，由专门的设备网关服务处理
2. **状态同步**: 实现设备状态上报和服务器状态同步机制
3. **定时任务**: 添加定时控制功能，支持预设的控制计划
4. **报警机制**: 当执行器异常时触发报警通知
5. **批量操作**: 支持对多个执行器进行批量控制
6. **设备发现**: 实现自动设备发现和注册机制
7. **安全加固**: 添加设备认证和命令签名验证
