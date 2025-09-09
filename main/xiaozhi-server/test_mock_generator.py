"""
测试Mock传感器数据生成器
"""

import sys
import os
import time
from datetime import datetime

# 添加路径以便导入mock模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mock.sensor_data_generator import get_generator

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试Mock传感器数据生成器...")
    
    generator = get_generator()
    
    # 测试1: 创建设备
    print("\n📱 测试1: 创建Mock设备")
    try:
        device = generator.create_device(
            mac_address="00:1A:2B:3C:4D:5E",
            name="测试设备1"
        )
        print(f"   ✅ 设备创建成功: {device.name} ({device.mac_address})")
    except Exception as e:
        print(f"   ❌ 设备创建失败: {e}")
        return False
    
    # 测试2: 生成单次数据
    print("\n📊 测试2: 生成传感器数据")
    try:
        message_data = generator.generate_device_data("00:1A:2B:3C:4D:5E")
        print(f"   ✅ 数据生成成功，包含 {len(message_data['sensors'])} 个传感器")
        
        # 显示生成的数据
        for sensor in message_data['sensors']:
            print(f"      - {sensor['sensor_code']}: {sensor['value']}")
            
    except Exception as e:
        print(f"   ❌ 数据生成失败: {e}")
        return False
    
    # 测试3: 发送数据到后端（模拟）
    print("\n🚀 测试3: 发送数据到后端")
    try:
        success, message = generator.send_data_to_backend(message_data)
        if success:
            print(f"   ✅ 数据发送成功: {message}")
        else:
            print(f"   ⚠️  数据发送失败（可能是后端未启动）: {message}")
    except Exception as e:
        print(f"   ❌ 数据发送异常: {e}")
    
    # 测试4: 生成并发送数据
    print("\n🔄 测试4: 生成并发送数据")
    try:
        success, message = generator.generate_and_send_data("00:1A:2B:3C:4D:5E")
        if success:
            print(f"   ✅ 生成并发送成功: {message}")
        else:
            print(f"   ⚠️  生成并发送失败（可能是后端未启动）: {message}")
    except Exception as e:
        print(f"   ❌ 生成并发送异常: {e}")
    
    # 测试5: 设备状态查询
    print("\n📋 测试5: 设备状态查询")
    try:
        status = generator.get_device_status("00:1A:2B:3C:4D:5E")
        if status:
            print(f"   ✅ 设备状态获取成功:")
            print(f"      - 设备名称: {status['name']}")
            print(f"      - MAC地址: {status['mac_address']}")
            print(f"      - 创建时间: {status['created_at']}")
            print(f"      - 最后活跃: {status['last_active']}")
            print(f"      - 传感器统计: {len(status['sensor_stats'])} 个传感器")
        else:
            print(f"   ❌ 设备状态获取失败")
    except Exception as e:
        print(f"   ❌ 设备状态查询异常: {e}")
    
    # 测试6: 设备列表
    print("\n📝 测试6: 设备列表")
    try:
        devices = generator.list_devices()
        print(f"   ✅ 设备列表获取成功，共 {len(devices)} 个设备")
        for device in devices:
            print(f"      - {device.name} ({device.mac_address})")
    except Exception as e:
        print(f"   ❌ 设备列表获取异常: {e}")
    
    # 测试7: 数据连续性
    print("\n🔗 测试7: 数据连续性测试")
    try:
        print("   生成连续3次数据，观察数值变化...")
        for i in range(3):
            success, message = generator.generate_and_send_data("00:1A:2B:3C:4D:5E")
            if success:
                print(f"   第{i+1}次: ✅ 成功")
            else:
                print(f"   第{i+1}次: ⚠️  {message}")
            time.sleep(1)
    except Exception as e:
        print(f"   ❌ 连续性测试异常: {e}")
    
    print("\n🎉 基本功能测试完成！")
    return True

def test_auto_generation():
    """测试自动生成功能（短时间测试）"""
    print("\n🤖 测试自动数据生成功能...")
    
    generator = get_generator()
    
    # 确保有设备存在
    if not generator.get_device("00:1A:2B:3C:4D:5E"):
        generator.create_device("00:1A:2B:3C:4D:5E", "自动测试设备")
    
    try:
        # 启动自动生成（5秒间隔）
        print("   启动自动生成（5秒间隔）...")
        success = generator.start_auto_generation("00:1A:2B:3C:4D:5E", 5)
        
        if success:
            print("   ✅ 自动生成已启动，运行15秒后停止...")
            time.sleep(15)
            
            # 停止自动生成
            stop_success = generator.stop_auto_generation("00:1A:2B:3C:4D:5E")
            if stop_success:
                print("   ✅ 自动生成已停止")
            else:
                print("   ❌ 停止自动生成失败")
        else:
            print("   ❌ 启动自动生成失败")
            
    except Exception as e:
        print(f"   ❌ 自动生成测试异常: {e}")
    
    print("🎉 自动生成测试完成！")

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Mock传感器数据生成器测试")
    print("=" * 60)
    
    # 基本功能测试
    if test_basic_functionality():
        print("\n" + "=" * 60)
        
        # 询问是否进行自动生成测试
        response = input("是否进行自动生成测试？(y/n): ").lower().strip()
        if response == 'y' or response == 'yes':
            test_auto_generation()
        else:
            print("跳过自动生成测试")
    
    print("\n" + "=" * 60)
    print("🏁 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()