#!/usr/bin/env python3
"""
Mock传感器数据生成系统 - 使用示例

本文件包含各种使用场景的示例代码，帮助开发者快速上手Mock传感器系统。
"""

import time
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mock.sensor_data_generator import get_generator, MockSensorDataGenerator
from mock.mock_logger import MockLogConfig, setup_mock_logging


def example_basic_usage():
    """示例1: 基本使用方法"""
    print("=" * 60)
    print("示例1: 基本使用方法")
    print("=" * 60)
    
    # 获取生成器实例
    generator = get_generator()
    
    # 创建设备
    device = generator.create_device("00:AA:BB:CC:DD:EE", "示例设备1")
    print(f"创建设备: {device.name} ({device.mac_address})")
    
    # 生成一次数据
    success, message = generator.generate_and_send_data(device.mac_address)
    print(f"数据生成结果: {message}")
    
    # 查看设备状态
    status = generator.get_device_status(device.mac_address)
    print(f"设备状态: {status['is_active']}")
    print(f"传感器数据: {len(status.get('sensor_stats', {}))}")
    
    # 清理
    generator.remove_device(device.mac_address)
    print("设备已删除")


def example_multiple_devices():
    """示例2: 多设备管理"""
    print("\n" + "=" * 60)
    print("示例2: 多设备管理")
    print("=" * 60)
    
    generator = get_generator()
    
    # 创建多个设备
    devices = []
    for i in range(3):
        mac = f"00:1A:2B:3C:4D:{i:02X}"
        name = f"多设备示例_{i+1}"
        device = generator.create_device(mac, name)
        devices.append(device)
        print(f"创建设备 {i+1}: {device.name}")
    
    # 为每个设备生成数据
    for device in devices:
        success, message = generator.generate_and_send_data(device.mac_address)
        print(f"设备 {device.name}: {message}")
    
    # 显示所有设备状态
    all_devices = generator.list_devices()
    print(f"\n当前共有 {len(all_devices)} 个设备:")
    for device in all_devices:
        status = generator.get_device_status(device.mac_address)
        sensor_count = len(status.get('sensor_stats', {}))
        print(f"  - {device.name}: {sensor_count} 种传感器有数据")
    
    # 清理所有设备
    for device in devices:
        generator.remove_device(device.mac_address)
    print("\n所有示例设备已清理")


def example_history_data():
    """示例3: 历史数据生成"""
    print("\n" + "=" * 60)
    print("示例3: 历史数据生成")
    print("=" * 60)
    
    generator = get_generator()
    
    # 创建设备
    device = generator.create_device("00:HISTORY:TEST:01", "历史数据测试设备")
    
    # 生成少量历史数据用于演示（1小时，每10分钟一个点）
    print("开始生成历史数据...")
    results = generator.generate_history_data(device.mac_address, hours=1, interval_minutes=10)
    
    # 统计结果
    successful = sum(1 for success, _ in results if success)
    total = len(results)
    print(f"历史数据生成完成: {successful}/{total} 条成功")
    
    # 显示统计信息
    status = generator.get_device_status(device.mac_address)
    sensor_stats = status.get('sensor_stats', {})
    
    print(f"\n传感器数据统计:")
    for sensor_type, stats in sensor_stats.items():
        print(f"  {sensor_type}: {stats['count']} 条数据")
        print(f"    最新值: {stats['latest_value']}")
        print(f"    范围: {stats['min_value']} - {stats['max_value']}")
    
    # 清理
    generator.remove_device(device.mac_address)
    print("\n历史数据测试设备已清理")


def example_auto_generation():
    """示例4: 自动数据生成"""
    print("\n" + "=" * 60)
    print("示例4: 自动数据生成")
    print("=" * 60)
    
    generator = get_generator()
    
    # 创建设备
    device = generator.create_device("00:AUTO:GEN:TEST", "自动生成测试设备")
    
    # 启动自动生成（10秒间隔用于演示）
    generator.start_auto_generation(device.mac_address, 10)
    print("自动数据生成已启动，间隔: 10秒")
    
    # 监控30秒
    print("监控30秒...")
    start_time = time.time()
    
    while time.time() - start_time < 30:
        status = generator.get_device_status(device.mac_address)
        sensor_stats = status.get('sensor_stats', {})
        
        if sensor_stats:
            total_data = sum(stats['count'] for stats in sensor_stats.values())
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] 累计数据: {total_data} 条")
        
        time.sleep(5)
    
    # 停止自动生成
    generator.stop_auto_generation(device.mac_address)
    print("自动数据生成已停止")
    
    # 最终统计
    status = generator.get_device_status(device.mac_address)
    sensor_stats = status.get('sensor_stats', {})
    total_data = sum(stats['count'] for stats in sensor_stats.values())
    print(f"最终数据总量: {total_data} 条")
    
    # 清理
    generator.remove_device(device.mac_address)
    print("自动生成测试设备已清理")


def example_custom_sensors():
    """示例5: 自定义传感器配置"""
    print("\n" + "=" * 60)
    print("示例5: 自定义传感器配置")
    print("=" * 60)
    
    generator = get_generator()
    
    # 备份原始配置
    original_temp_config = generator.SENSOR_CONFIGS["temperature"]
    
    # 自定义温度传感器范围
    generator.SENSOR_CONFIGS["temperature"].min_value = 10.0
    generator.SENSOR_CONFIGS["temperature"].max_value = 50.0
    print("已自定义温度传感器范围: 10.0-50.0°C")
    
    # 创建设备并生成数据
    device = generator.create_device("00:CUSTOM:SENSOR", "自定义传感器设备")
    
    # 生成多次数据查看范围
    temp_values = []
    for i in range(10):
        success, message = generator.generate_and_send_data(device.mac_address)
        if success:
            status = generator.get_device_status(device.mac_address)
            sensor_stats = status.get('sensor_stats', {})
            if 'temperature' in sensor_stats:
                temp_values.append(sensor_stats['temperature']['latest_value'])
    
    print(f"生成的温度值: {temp_values}")
    print(f"温度范围: {min(temp_values):.2f} - {max(temp_values):.2f}°C")
    
    # 恢复原始配置
    generator.SENSOR_CONFIGS["temperature"] = original_temp_config
    print("已恢复原始传感器配置")
    
    # 清理
    generator.remove_device(device.mac_address)
    print("自定义传感器测试设备已清理")


def example_logging_configuration():
    """示例6: 日志配置"""
    print("\n" + "=" * 60)
    print("示例6: 日志配置")
    print("=" * 60)
    
    # 自定义日志配置
    log_config = MockLogConfig(
        log_level="DEBUG",
        log_dir="tmp/example_logs",
        console_output=True,
        file_output=True,
        max_file_size="5 MB",
        retention_days=3
    )
    
    # 应用日志配置
    setup_mock_logging(log_config)
    print("已应用自定义日志配置:")
    print(f"  日志级别: {log_config.log_level}")
    print(f"  日志目录: {log_config.log_dir}")
    print(f"  文件大小限制: {log_config.max_file_size}")
    print(f"  保留天数: {log_config.retention_days}")
    
    # 创建设备并生成一些日志
    generator = get_generator()
    device = generator.create_device("00:LOG:TEST:DEV", "日志测试设备")
    
    # 生成数据（会产生详细的DEBUG日志）
    for i in range(3):
        generator.generate_and_send_data(device.mac_address)
        time.sleep(1)
    
    print("已生成测试日志，请查看 tmp/example_logs/ 目录")
    
    # 清理
    generator.remove_device(device.mac_address)


def example_performance_monitoring():
    """示例7: 性能监控"""
    print("\n" + "=" * 60)
    print("示例7: 性能监控")
    print("=" * 60)
    
    generator = get_generator()
    
    # 创建设备
    device = generator.create_device("00:PERF:TEST:01", "性能测试设备")
    
    # 测试单次数据生成性能
    print("测试单次数据生成性能...")
    times = []
    for i in range(10):
        start_time = time.time()
        generator.generate_and_send_data(device.mac_address)
        end_time = time.time()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"单次数据生成性能统计:")
    print(f"  平均耗时: {avg_time:.3f}秒")
    print(f"  最短耗时: {min_time:.3f}秒")
    print(f"  最长耗时: {max_time:.3f}秒")
    
    # 测试历史数据生成性能
    print("\n测试历史数据生成性能...")
    start_time = time.time()
    results = generator.generate_history_data(device.mac_address, hours=1, interval_minutes=30)
    end_time = time.time()
    
    successful = sum(1 for success, _ in results if success)
    total_time = end_time - start_time
    throughput = len(results) / total_time if total_time > 0 else 0
    
    print(f"历史数据生成性能:")
    print(f"  总耗时: {total_time:.3f}秒")
    print(f"  数据点数: {len(results)}")
    print(f"  成功率: {successful/len(results)*100:.1f}%")
    print(f"  吞吐量: {throughput:.2f} 点/秒")
    
    # 清理
    generator.remove_device(device.mac_address)
    print("\n性能测试设备已清理")


def example_error_handling():
    """示例8: 错误处理"""
    print("\n" + "=" * 60)
    print("示例8: 错误处理")
    print("=" * 60)
    
    generator = get_generator()
    
    # 测试各种错误情况
    print("1. 测试无效MAC地址...")
    try:
        generator.create_device("invalid-mac", "无效MAC测试")
    except Exception as e:
        print(f"   捕获异常: {e}")
    
    print("\n2. 测试重复创建设备...")
    device = generator.create_device("00:ERROR:TEST:01", "错误处理测试设备")
    try:
        generator.create_device("00:ERROR:TEST:01", "重复设备")
    except ValueError as e:
        print(f"   捕获异常: {e}")
    
    print("\n3. 测试操作不存在的设备...")
    result = generator.generate_and_send_data("00:NOT:EXIST:01")
    print(f"   操作结果: {result}")
    
    print("\n4. 测试停止未启动的自动生成...")
    result = generator.stop_auto_generation("00:ERROR:TEST:01")
    print(f"   停止结果: {result}")
    
    # 清理
    generator.remove_device(device.mac_address)
    print("\n错误处理测试完成")


def run_all_examples():
    """运行所有示例"""
    print("🎯 Mock传感器数据生成系统 - 使用示例")
    print("=" * 80)
    
    examples = [
        example_basic_usage,
        example_multiple_devices,
        example_history_data,
        example_auto_generation,
        example_custom_sensors,
        example_logging_configuration,
        example_performance_monitoring,
        example_error_handling
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n🔄 运行示例 {i}/{len(examples)}: {example_func.__doc__.split(':')[1].strip()}")
            example_func()
            print(f"✅ 示例 {i} 完成")
        except Exception as e:
            print(f"❌ 示例 {i} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 所有示例运行完成！")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mock传感器数据生成系统使用示例")
    parser.add_argument('--example', type=int, choices=range(1, 9), 
                       help='运行指定示例 (1-8)')
    parser.add_argument('--all', action='store_true', 
                       help='运行所有示例')
    
    args = parser.parse_args()
    
    if args.all:
        run_all_examples()
    elif args.example:
        examples = [
            example_basic_usage,
            example_multiple_devices, 
            example_history_data,
            example_auto_generation,
            example_custom_sensors,
            example_logging_configuration,
            example_performance_monitoring,
            example_error_handling
        ]
        
        example_func = examples[args.example - 1]
        print(f"🔄 运行示例 {args.example}: {example_func.__doc__.split(':')[1].strip()}")
        example_func()
        print("✅ 示例完成")
    else:
        parser.print_help()
        print("\n可用示例:")
        examples_info = [
            "基本使用方法",
            "多设备管理", 
            "历史数据生成",
            "自动数据生成",
            "自定义传感器配置",
            "日志配置",
            "性能监控",
            "错误处理"
        ]
        
        for i, info in enumerate(examples_info, 1):
            print(f"  {i}. {info}")
        
        print(f"\n示例用法:")
        print(f"  python examples.py --example 1    # 运行示例1")
        print(f"  python examples.py --all          # 运行所有示例")

