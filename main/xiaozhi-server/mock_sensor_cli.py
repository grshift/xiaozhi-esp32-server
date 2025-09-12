#!/usr/bin/env python3
"""
Mock传感器数据CLI管理工具

提供完整的命令行界面来管理Mock传感器设备和数据生成：
- 设备管理：创建、删除、查看设备
- 数据生成：实时数据、历史数据生成
- 自动化控制：启动/停止自动数据生成
- 状态监控：查看设备状态和运行情况

使用方法：
    python mock_sensor_cli.py <command> [options]

示例：
    python mock_sensor_cli.py create --mac 00:1A:2B:3C:4D:5E --name "测试设备"
    python mock_sensor_cli.py generate --mac 00:1A:2B:3C:4D:5E
    python mock_sensor_cli.py auto-start --mac 00:1A:2B:3C:4D:5E --interval 30
"""

import argparse
import sys
import os
import time
import signal
from datetime import datetime
from typing import Optional

# 添加项目路径以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mock.sensor_data_generator import get_generator, MockSensorDataGenerator

class MockSensorCLI:
    """Mock传感器CLI控制器"""
    
    def __init__(self):
        self.generator = get_generator()
        self._running = True
        
        # 注册信号处理器用于优雅关闭
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅关闭"""
        print(f"\n🔄 接收到退出信号 {signum}，正在安全关闭...")
        self._running = False
        sys.exit(0)
    
    def _print_header(self, title: str):
        """打印标题头部"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def _print_success(self, message: str):
        """打印成功消息"""
        print(f"✅ {message}")
    
    def _print_error(self, message: str):
        """打印错误消息"""
        print(f"❌ {message}")
    
    def _print_info(self, message: str):
        """打印信息消息"""
        print(f"ℹ️  {message}")
    
    def _print_warning(self, message: str):
        """打印警告消息"""
        print(f"⚠️  {message}")
    
    def _validate_mac_address(self, mac_address: str) -> bool:
        """验证MAC地址格式"""
        if not mac_address:
            return False
        
        parts = mac_address.split(':')
        if len(parts) != 6:
            return False
        
        for part in parts:
            if len(part) != 2:
                return False
            try:
                int(part, 16)
            except ValueError:
                return False
        
        return True
    
    def create_device(self, mac_address: Optional[str] = None, name: Optional[str] = None) -> bool:
        """创建Mock设备"""
        self._print_header("创建Mock设备")
        
        try:
            # 使用默认MAC地址如果未提供
            if mac_address is None:
                mac_address = "00:1A:2B:3C:4D:5E"
                self._print_info(f"使用默认MAC地址: {mac_address}")
            
            # 验证MAC地址格式
            if not self._validate_mac_address(mac_address):
                self._print_error("MAC地址格式无效，正确格式: XX:XX:XX:XX:XX:XX")
                return False
            
            # 检查设备是否已存在
            if self.generator.get_device(mac_address):
                self._print_warning(f"设备 {mac_address} 已存在")
                return False
            
            # 创建设备
            device = self.generator.create_device(mac_address, name)
            
            self._print_success(f"成功创建Mock设备:")
            print(f"   📱 设备名称: {device.name}")
            print(f"   🔗 MAC地址: {device.mac_address}")
            print(f"   📅 创建时间: {device.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   🔧 支持传感器: {', '.join(self.generator.SENSOR_CONFIGS.keys())}")
            
            return True
            
        except Exception as e:
            self._print_error(f"创建设备失败: {str(e)}")
            return False
    
    def list_devices(self) -> bool:
        """列出所有Mock设备"""
        self._print_header("Mock设备列表")
        
        try:
            devices = self.generator.list_devices()
            
            if not devices:
                self._print_info("暂无Mock设备")
                print("   使用 'python mock_sensor_cli.py create' 创建设备")
                return True
            
            print(f"📱 共找到 {len(devices)} 个Mock设备:\n")
            
            for i, device in enumerate(devices, 1):
                status = self.generator.get_device_status(device.mac_address)
                
                print(f"设备 {i}:")
                print(f"   📱 名称: {device.name}")
                print(f"   🔗 MAC: {device.mac_address}")
                print(f"   📅 创建: {device.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   ⏰ 最后活跃: {device.last_active.strftime('%Y-%m-%d %H:%M:%S') if device.last_active else '从未活跃'}")
                print(f"   🔄 自动生成: {'运行中' if status['auto_generation_active'] else '已停止'}")
                
                if status['auto_generation_active']:
                    print(f"   ⏱️  生成间隔: {status['generation_interval']} 秒")
                
                # 显示传感器统计
                sensor_stats = status.get('sensor_stats', {})
                if sensor_stats:
                    print(f"   📊 传感器数据:")
                    for sensor_type, stats in sensor_stats.items():
                        print(f"      {sensor_type}: {stats['count']} 条数据, 最新值: {stats['latest_value']}")
                else:
                    print(f"   📊 传感器数据: 暂无数据")
                
                print()  # 空行分隔
            
            return True
            
        except Exception as e:
            self._print_error(f"获取设备列表失败: {str(e)}")
            return False
    
    def remove_device(self, mac_address: str) -> bool:
        """删除Mock设备"""
        self._print_header("删除Mock设备")
        
        try:
            if not mac_address:
                self._print_error("请提供设备MAC地址")
                return False
            
            # 检查设备是否存在
            device = self.generator.get_device(mac_address)
            if not device:
                self._print_error(f"设备 {mac_address} 不存在")
                return False
            
            # 确认删除
            print(f"📱 即将删除设备: {device.name} ({mac_address})")
            confirm = input("⚠️  确认删除? (y/N): ").strip().lower()
            
            if confirm not in ['y', 'yes']:
                self._print_info("取消删除操作")
                return True
            
            # 删除设备
            success = self.generator.remove_device(mac_address)
            
            if success:
                self._print_success(f"成功删除设备: {device.name} ({mac_address})")
            else:
                self._print_error("删除设备失败")
            
            return success
            
        except Exception as e:
            self._print_error(f"删除设备失败: {str(e)}")
            return False
    
    def show_status(self, mac_address: Optional[str] = None) -> bool:
        """显示设备状态"""
        if mac_address:
            self._print_header(f"设备状态 - {mac_address}")
        else:
            self._print_header("所有设备状态")
        
        try:
            if mac_address:
                # 显示单个设备状态
                device = self.generator.get_device(mac_address)
                if not device:
                    self._print_error(f"设备 {mac_address} 不存在")
                    return False
                
                status = self.generator.get_device_status(mac_address)
                self._print_device_detailed_status(status)
                
            else:
                # 显示所有设备状态
                devices = self.generator.list_devices()
                if not devices:
                    self._print_info("暂无Mock设备")
                    return True
                
                for device in devices:
                    status = self.generator.get_device_status(device.mac_address)
                    print(f"\n📱 {device.name} ({device.mac_address})")
                    print(f"   状态: {'🟢 活跃' if device.is_active else '🔴 非活跃'}")
                    print(f"   自动生成: {'🔄 运行中' if status['auto_generation_active'] else '⏹️ 已停止'}")
                    
                    sensor_stats = status.get('sensor_stats', {})
                    if sensor_stats:
                        total_data = sum(stats['count'] for stats in sensor_stats.values())
                        print(f"   数据总量: {total_data} 条")
                    else:
                        print(f"   数据总量: 0 条")
            
            return True
            
        except Exception as e:
            self._print_error(f"获取状态失败: {str(e)}")
            return False
    
    def _print_device_detailed_status(self, status: dict):
        """打印设备详细状态"""
        print(f"📱 设备信息:")
        print(f"   名称: {status['name']}")
        print(f"   MAC: {status['mac_address']}")
        print(f"   创建时间: {status['created_at']}")
        print(f"   最后活跃: {status['last_active'] or '从未活跃'}")
        print(f"   状态: {'🟢 活跃' if status['is_active'] else '🔴 非活跃'}")
        
        print(f"\n🔄 自动生成:")
        print(f"   状态: {'🟢 运行中' if status['auto_generation_active'] else '🔴 已停止'}")
        print(f"   间隔: {status['generation_interval']} 秒")
        
        sensor_stats = status.get('sensor_stats', {})
        if sensor_stats:
            print(f"\n📊 传感器统计:")
            for sensor_type, stats in sensor_stats.items():
                config = self.generator.SENSOR_CONFIGS.get(sensor_type, {})
                unit = getattr(config, 'unit', '')
                
                print(f"   {sensor_type}:")
                print(f"      数据量: {stats['count']} 条")
                print(f"      最新值: {stats['latest_value']}{unit}")
                print(f"      最小值: {stats['min_value']}{unit}")
                print(f"      最大值: {stats['max_value']}{unit}")
                print(f"      平均值: {stats['avg_value']:.2f}{unit}")
        else:
            print(f"\n📊 传感器统计: 暂无数据")
    
    def generate_data(self, mac_address: str) -> bool:
        """生成一次实时数据"""
        self._print_header(f"生成实时数据 - {mac_address}")
        
        try:
            if not mac_address:
                self._print_error("请提供设备MAC地址")
                return False
            
            # 检查设备是否存在
            device = self.generator.get_device(mac_address)
            if not device:
                self._print_error(f"设备 {mac_address} 不存在")
                return False
            
            self._print_info("正在生成实时传感器数据...")
            
            # 生成并发送数据
            success, message = self.generator.generate_and_send_data(mac_address)
            
            if success:
                self._print_success("实时数据生成完成")
                print(f"   📊 {message}")
                
                # 显示生成的数据
                status = self.generator.get_device_status(mac_address)
                sensor_stats = status.get('sensor_stats', {})
                if sensor_stats:
                    print(f"   📈 最新数据:")
                    for sensor_type, stats in sensor_stats.items():
                        config = self.generator.SENSOR_CONFIGS.get(sensor_type, {})
                        unit = getattr(config, 'unit', '')
                        print(f"      {sensor_type}: {stats['latest_value']}{unit}")
            else:
                self._print_error(f"数据生成失败: {message}")
            
            return success
            
        except Exception as e:
            self._print_error(f"生成数据失败: {str(e)}")
            return False
    
    def generate_history(self, mac_address: str, hours: int = 24) -> bool:
        """生成历史数据"""
        self._print_header(f"生成历史数据 - {mac_address}")
        
        try:
            if not mac_address:
                self._print_error("请提供设备MAC地址")
                return False
            
            # 检查设备是否存在
            device = self.generator.get_device(mac_address)
            if not device:
                self._print_error(f"设备 {mac_address} 不存在")
                return False
            
            # 验证小时数
            if hours <= 0 or hours > 168:  # 最多7天
                self._print_error("历史数据小时数必须在 1-168 之间")
                return False
            
            self._print_info(f"开始生成 {hours} 小时的历史数据...")
            print(f"   📅 时间范围: {hours} 小时前 → 现在")
            print(f"   ⏰ 数据间隔: 5 分钟")
            
            # 估算数据点数量
            data_points = (hours * 60) // 5
            print(f"   📊 预计生成: {data_points} 个数据点")
            
            # 确认生成
            if data_points > 500:
                confirm = input(f"⚠️  将生成大量数据 ({data_points} 条)，确认继续? (y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    self._print_info("取消历史数据生成")
                    return True
            
            start_time = time.time()
            
            # 生成历史数据
            results = self.generator.generate_history_data(mac_address, hours, 5)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 统计结果
            successful_count = sum(1 for success, _ in results if success)
            total_count = len(results)
            success_rate = (successful_count / total_count * 100) if total_count > 0 else 0
            
            print(f"\n📊 历史数据生成完成:")
            print(f"   ✅ 成功: {successful_count} 条")
            print(f"   ❌ 失败: {total_count - successful_count} 条")
            print(f"   📈 成功率: {success_rate:.1f}%")
            print(f"   ⏱️  耗时: {duration:.2f} 秒")
            
            if successful_count > 0:
                self._print_success("历史数据生成成功")
            else:
                self._print_error("历史数据生成失败")
            
            return successful_count > 0
            
        except Exception as e:
            self._print_error(f"生成历史数据失败: {str(e)}")
            return False
    
    def start_auto_generation(self, mac_address: str, interval: int = 30) -> bool:
        """启动自动数据生成"""
        self._print_header(f"启动自动数据生成 - {mac_address}")
        
        try:
            if not mac_address:
                self._print_error("请提供设备MAC地址")
                return False
            
            # 检查设备是否存在
            device = self.generator.get_device(mac_address)
            if not device:
                self._print_error(f"设备 {mac_address} 不存在")
                return False
            
            # 验证间隔时间
            if interval < 5 or interval > 3600:  # 5秒到1小时
                self._print_error("生成间隔必须在 5-3600 秒之间")
                return False
            
            # 检查是否已经在运行
            status = self.generator.get_device_status(mac_address)
            if status['auto_generation_active']:
                self._print_warning(f"设备 {mac_address} 的自动生成已在运行中")
                current_interval = status['generation_interval']
                
                if current_interval != interval:
                    print(f"   当前间隔: {current_interval} 秒")
                    print(f"   新的间隔: {interval} 秒")
                    confirm = input("⚠️  是否重新启动以应用新间隔? (y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        # 先停止现有的自动生成
                        self.generator.stop_auto_generation(mac_address)
                        time.sleep(1)  # 等待停止完成
                    else:
                        return True
                else:
                    return True
            
            # 启动自动生成
            success = self.generator.start_auto_generation(mac_address, interval)
            
            if success:
                self._print_success("自动数据生成已启动")
                print(f"   📱 设备: {device.name} ({mac_address})")
                print(f"   ⏱️  间隔: {interval} 秒")
                print(f"   🔄 状态: 运行中")
                print(f"\n   使用 'python mock_sensor_cli.py auto-stop --mac {mac_address}' 停止")
                print(f"   使用 'python mock_sensor_cli.py status --mac {mac_address}' 查看状态")
            else:
                self._print_error("启动自动生成失败")
            
            return success
            
        except Exception as e:
            self._print_error(f"启动自动生成失败: {str(e)}")
            return False
    
    def stop_auto_generation(self, mac_address: str) -> bool:
        """停止自动数据生成"""
        self._print_header(f"停止自动数据生成 - {mac_address}")
        
        try:
            if not mac_address:
                self._print_error("请提供设备MAC地址")
                return False
            
            # 检查设备是否存在
            device = self.generator.get_device(mac_address)
            if not device:
                self._print_error(f"设备 {mac_address} 不存在")
                return False
            
            # 检查是否正在运行
            status = self.generator.get_device_status(mac_address)
            if not status['auto_generation_active']:
                self._print_info(f"设备 {mac_address} 的自动生成未在运行")
                return True
            
            # 停止自动生成
            success = self.generator.stop_auto_generation(mac_address)
            
            if success:
                self._print_success("自动数据生成已停止")
                print(f"   📱 设备: {device.name} ({mac_address})")
                print(f"   🔄 状态: 已停止")
            else:
                self._print_error("停止自动生成失败")
            
            return success
            
        except Exception as e:
            self._print_error(f"停止自动生成失败: {str(e)}")
            return False


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Mock传感器数据CLI管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 设备管理
  python mock_sensor_cli.py create --mac 00:1A:2B:3C:4D:5E --name "测试设备"
  python mock_sensor_cli.py list
  python mock_sensor_cli.py remove --mac 00:1A:2B:3C:4D:5E
  
  # 数据生成
  python mock_sensor_cli.py generate --mac 00:1A:2B:3C:4D:5E
  python mock_sensor_cli.py history --mac 00:1A:2B:3C:4D:5E --hours 24
  
  # 自动化控制
  python mock_sensor_cli.py auto-start --mac 00:1A:2B:3C:4D:5E --interval 30
  python mock_sensor_cli.py auto-stop --mac 00:1A:2B:3C:4D:5E
  
  # 状态监控
  python mock_sensor_cli.py status
  python mock_sensor_cli.py status --mac 00:1A:2B:3C:4D:5E
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建设备命令
    create_parser = subparsers.add_parser('create', help='创建Mock设备')
    create_parser.add_argument('--mac', type=str, help='设备MAC地址 (默认: 00:1A:2B:3C:4D:5E)')
    create_parser.add_argument('--name', type=str, help='设备名称')
    
    # 列出设备命令
    subparsers.add_parser('list', help='列出所有Mock设备')
    
    # 删除设备命令
    remove_parser = subparsers.add_parser('remove', help='删除Mock设备')
    remove_parser.add_argument('--mac', type=str, required=True, help='设备MAC地址')
    
    # 状态查看命令
    status_parser = subparsers.add_parser('status', help='查看设备状态')
    status_parser.add_argument('--mac', type=str, help='设备MAC地址 (留空显示所有设备)')
    
    # 生成数据命令
    generate_parser = subparsers.add_parser('generate', help='生成一次实时数据')
    generate_parser.add_argument('--mac', type=str, required=True, help='设备MAC地址')
    
    # 生成历史数据命令
    history_parser = subparsers.add_parser('history', help='生成历史数据')
    history_parser.add_argument('--mac', type=str, required=True, help='设备MAC地址')
    history_parser.add_argument('--hours', type=int, default=24, help='历史数据小时数 (默认: 24)')
    
    # 启动自动生成命令
    auto_start_parser = subparsers.add_parser('auto-start', help='启动自动数据生成')
    auto_start_parser.add_argument('--mac', type=str, required=True, help='设备MAC地址')
    auto_start_parser.add_argument('--interval', type=int, default=30, help='生成间隔秒数 (默认: 30)')
    
    # 停止自动生成命令
    auto_stop_parser = subparsers.add_parser('auto-stop', help='停止自动数据生成')
    auto_stop_parser.add_argument('--mac', type=str, required=True, help='设备MAC地址')
    
    return parser


def main():
    """主函数"""
    try:
        parser = create_argument_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 1
        
        # 创建CLI控制器
        cli = MockSensorCLI()
        
        # 执行对应的命令
        success = False
        
        if args.command == 'create':
            success = cli.create_device(args.mac, args.name)
        
        elif args.command == 'list':
            success = cli.list_devices()
        
        elif args.command == 'remove':
            success = cli.remove_device(args.mac)
        
        elif args.command == 'status':
            success = cli.show_status(args.mac)
        
        elif args.command == 'generate':
            success = cli.generate_data(args.mac)
        
        elif args.command == 'history':
            success = cli.generate_history(args.mac, args.hours)
        
        elif args.command == 'auto-start':
            success = cli.start_auto_generation(args.mac, args.interval)
        
        elif args.command == 'auto-stop':
            success = cli.stop_auto_generation(args.mac)
        
        else:
            print(f"❌ 未知命令: {args.command}")
            parser.print_help()
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🔄 用户中断操作")
        return 130
    except Exception as e:
        print(f"❌ 程序异常: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

