# Mock传感器数据生成系统 - 使用指南

## 📖 概述

Mock传感器数据生成系统是一个完整的模拟传感器数据生成解决方案，用于在没有真实ESP32设备的情况下测试和验证传感器管理系统。

### 🎯 主要功能

- **虚拟设备管理**：创建、删除、查看Mock设备
- **智能数据生成**：支持7种传感器类型的真实数据模拟
- **历史数据生成**：批量生成指定时间范围的历史数据
- **自动数据生成**：定时自动生成实时数据
- **完整日志系统**：详细的操作日志和性能监控
- **命令行工具**：友好的CLI管理界面
- **快速演示**：一键启动演示环境

### 🔧 支持的传感器类型

| 传感器类型 | 数值范围 | 单位 | 精度 | 描述 |
|-----------|---------|------|------|------|
| temperature | 18.0-35.0 | °C | 2位小数 | 温度传感器 |
| humidity | 30.0-80.0 | % | 1位小数 | 湿度传感器 |
| light | 0-2000 | lux | 整数 | 光照传感器 |
| motion | 0/1 | - | 布尔值 | 运动传感器 |
| air_quality | 0-500 | ppm | 整数 | 空气质量传感器 |
| pressure | 900-1100 | hPa | 1位小数 | 气压传感器 |
| co2 | 300-2000 | ppm | 整数 | CO2传感器 |

## 🚀 快速开始

### 1. 环境准备

确保以下服务正在运行：
- Java后端服务（端口8002）
- 前端开发服务器（端口8001）
- Python环境和依赖

### 2. 一键演示

```bash
# 进入项目目录
cd main/xiaozhi-server

# 启动快速演示
python start_mock_demo.py
```

这将自动：
1. 创建默认Mock设备（MAC: 00:1A:2B:3C:4D:5E）
2. 生成2小时历史数据
3. 启动30秒间隔的自动数据生成
4. 提供交互式控制界面

### 3. 前端验证

1. 打开传感器监控页面
2. 选择设备：`00:1A:2B:3C:4D:5E`
3. 查看实时数据更新
4. 测试历史数据查询
5. 验证告警功能

## 🛠️ 命令行工具使用

### 基本语法

```bash
python mock_sensor_cli.py <command> [options]
```

### 设备管理命令

#### 创建设备

```bash
# 创建默认设备
python mock_sensor_cli.py create

# 创建指定设备
python mock_sensor_cli.py create --mac 00:AA:BB:CC:DD:EE --name "自定义设备"
```

#### 查看设备列表

```bash
python mock_sensor_cli.py list
```

#### 删除设备

```bash
python mock_sensor_cli.py remove --mac 00:1A:2B:3C:4D:5E
```

#### 查看设备状态

```bash
# 查看所有设备状态
python mock_sensor_cli.py status

# 查看指定设备状态
python mock_sensor_cli.py status --mac 00:1A:2B:3C:4D:5E
```

### 数据生成命令

#### 生成实时数据

```bash
python mock_sensor_cli.py generate --mac 00:1A:2B:3C:4D:5E
```

#### 生成历史数据

```bash
# 生成24小时历史数据（默认）
python mock_sensor_cli.py history --mac 00:1A:2B:3C:4D:5E

# 生成指定小时数的历史数据
python mock_sensor_cli.py history --mac 00:1A:2B:3C:4D:5E --hours 48
```

### 自动生成控制

#### 启动自动生成

```bash
# 使用默认间隔（30秒）
python mock_sensor_cli.py auto-start --mac 00:1A:2B:3C:4D:5E

# 指定生成间隔
python mock_sensor_cli.py auto-start --mac 00:1A:2B:3C:4D:5E --interval 60
```

#### 停止自动生成

```bash
python mock_sensor_cli.py auto-stop --mac 00:1A:2B:3C:4D:5E
```

## 🎮 快速演示脚本

### 基本用法

```bash
# 默认配置演示
python start_mock_demo.py

# 自定义配置
python start_mock_demo.py --hours 4 --interval 60 --skip-history
```

### 参数说明

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--hours` | 历史数据小时数 | 2 |
| `--interval` | 自动生成间隔（秒） | 30 |
| `--skip-history` | 跳过历史数据生成 | False |

### 交互式控制

演示启动后，提供以下交互命令：

| 命令 | 功能 |
|------|------|
| `Enter` | 显示当前状态 |
| `help` | 显示帮助信息 |
| `status` | 显示详细状态 |
| `generate` | 手动生成一次数据 |
| `interval <秒数>` | 更改生成间隔 |
| `quit` | 退出演示 |

## 📊 日志系统

### 日志目录结构

```
tmp/mock_logs/
├── mock_sensor.log      # 主日志文件
├── mock_errors.log      # 错误日志文件
├── mock_performance.log # 性能日志文件
└── archived/           # 归档日志目录
```

### 日志级别

- **DEBUG**：详细的调试信息
- **INFO**：一般信息和状态更新
- **WARNING**：警告信息
- **ERROR**：错误信息
- **CRITICAL**：严重错误

### 日志组件

| 组件 | 描述 |
|------|------|
| GENERATOR | 数据生成器核心 |
| DEVICE | 设备管理操作 |
| DATA_GEN | 数据生成过程 |
| DATA_SEND | 数据发送过程 |
| HISTORY | 历史数据生成 |
| AUTO_GEN | 自动生成控制 |

## 🔧 高级配置

### 传感器配置自定义

```python
from mock.sensor_data_generator import MockSensorDataGenerator

# 获取生成器实例
generator = MockSensorDataGenerator()

# 自定义传感器范围
generator.SENSOR_CONFIGS["temperature"].min_value = 15.0
generator.SENSOR_CONFIGS["temperature"].max_value = 40.0
```

### 日志配置自定义

```python
from mock.mock_logger import MockLogConfig, setup_mock_logging

# 自定义日志配置
config = MockLogConfig(
    log_level="DEBUG",
    log_dir="custom/logs",
    console_output=True,
    file_output=True,
    max_file_size="20 MB",
    retention_days=14
)

setup_mock_logging(config=config)
```

## 🧪 测试场景

### 功能验证测试

```bash
# 1. 创建测试设备
python mock_sensor_cli.py create --mac 00:TEST:DEVICE:01 --name "功能测试设备"

# 2. 生成测试数据
python mock_sensor_cli.py generate --mac 00:TEST:DEVICE:01

# 3. 生成历史数据
python mock_sensor_cli.py history --mac 00:TEST:DEVICE:01 --hours 2

# 4. 启动自动生成
python mock_sensor_cli.py auto-start --mac 00:TEST:DEVICE:01 --interval 30
```

### 性能压力测试

```bash
# 创建多个设备进行压力测试
for i in {1..5}; do
    python mock_sensor_cli.py create --mac "00:1A:2B:3C:4D:0$i" --name "压力测试设备$i"
    python mock_sensor_cli.py auto-start --mac "00:1A:2B:3C:4D:0$i" --interval 10
done
```

### 长期稳定性测试

```bash
# 启动长期运行的演示
python start_mock_demo.py --interval 60

# 让系统运行24-48小时，监控日志文件
tail -f tmp/mock_logs/mock_sensor.log
```

## 🚨 故障排除

### 常见问题

#### 1. 数据发送失败

**现象**：CLI显示"❌ 发送数据失败"

**解决方案**：
- 检查Java后端服务是否运行在8002端口
- 检查网络连接
- 查看错误日志：`tmp/mock_logs/mock_errors.log`

#### 2. 设备创建失败

**现象**：设备创建时出现异常

**解决方案**：
- 检查MAC地址格式是否正确（XX:XX:XX:XX:XX:XX）
- 确保MAC地址未被使用
- 检查文件权限

#### 3. 自动生成停止

**现象**：自动生成突然停止工作

**解决方案**：
- 检查Python进程是否正常运行
- 查看性能日志检查是否有异常
- 重新启动自动生成

#### 4. 前端无法显示数据

**现象**：前端页面无数据显示

**解决方案**：
- 确认设备MAC地址正确
- 检查Java后端API接口
- 验证数据库连接

### 日志分析

#### 查看最近的错误

```bash
tail -n 100 tmp/mock_logs/mock_errors.log
```

#### 查看性能统计

```bash
grep "操作耗时" tmp/mock_logs/mock_performance.log | tail -20
```

#### 监控实时日志

```bash
tail -f tmp/mock_logs/mock_sensor.log
```

## 📈 性能优化

### 建议配置

| 场景 | 生成间隔 | 历史数据量 | 并发设备数 |
|------|----------|------------|------------|
| 开发测试 | 30秒 | 2-24小时 | 1-3个 |
| 功能验证 | 10-60秒 | 24-72小时 | 3-5个 |
| 性能测试 | 10-30秒 | 72-168小时 | 5-10个 |
| 长期稳定性 | 60-300秒 | 168小时+ | 1-5个 |

### 优化建议

1. **数据生成间隔**：不建议小于5秒
2. **历史数据批量**：单次不超过1000条
3. **设备数量**：同时运行不超过10个设备
4. **日志级别**：生产环境使用INFO级别
5. **定期清理**：定期清理历史日志和测试数据

## 🔗 相关文档

- [传感器管理系统设计文档](../notes/sensor-management-design.md)
- [API接口文档](../notes/api-documentation.md)
- [数据库设计文档](../notes/database-schema.md)
- [Mock传感器完整方案](../notes/mock-sensor-data-solution.md)

## 📞 技术支持

如果遇到问题，请：

1. 查看相关日志文件
2. 检查系统配置
3. 参考故障排除章节
4. 联系开发团队

---

*该文档会随着系统的发展持续更新和完善。*

