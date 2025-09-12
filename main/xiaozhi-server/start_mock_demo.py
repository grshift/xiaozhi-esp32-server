#!/usr/bin/env python3
"""
Mock传感器数据快速演示脚本

该脚本提供一键启动的Mock传感器数据演示环境：
1. 创建默认Mock设备（MAC: 00:1A:2B:3C:4D:5E）
2. 生成2小时历史数据用于测试
3. 启动自动数据生成（30秒间隔）
4. 提供用户友好的状态提示和控制界面

使用方法：
    python start_mock_demo.py [--hours HOURS] [--interval SECONDS] [--skip-history]

示例：
    python start_mock_demo.py                    # 使用默认配置
    python start_mock_demo.py --hours 4          # 生成4小时历史数据
    python start_mock_demo.py --interval 60      # 60秒间隔自动生成
    python start_mock_demo.py --skip-history     # 跳过历史数据生成
"""

import argparse
import sys
import os
import time
import signal
import threading
from datetime import datetime
from typing import Optional

# 添加项目路径以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mock.sensor_data_generator import get_generator, MockSensorDataGenerator

class MockDemoRunner:
    """Mock传感器演示运行器"""
    
    # 默认配置
    DEFAULT_MAC = "00:1A:2B:3C:4D:5E"
    DEFAULT_DEVICE_NAME = "Mock演示设备"
    DEFAULT_HISTORY_HOURS = 2
    DEFAULT_INTERVAL = 30
    
    def __init__(self):
        self.generator = get_generator()
        self._running = True
        self._status_thread = None
        
        # 注册信号处理器用于优雅关闭
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅关闭"""
        print(f"\n\n🔄 接收到退出信号，正在安全关闭Mock演示...")
        self._running = False
        
        # 停止自动生成
        try:
            self.generator.stop_auto_generation(self.DEFAULT_MAC)
            print("✅ 已停止自动数据生成")
        except Exception as e:
            print(f"⚠️  停止自动生成时出现异常: {e}")
        
        print("👋 Mock演示已安全关闭，感谢使用！")
        sys.exit(0)
    
    def _print_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🎯 Mock传感器数据演示系统                                  ║
║                                                                              ║
║    该演示系统将创建Mock设备并生成传感器数据，用于验证完整的数据流程：              ║
║    📱 Mock设备 → 🐍 Python处理 → ☕ Java后端 → 🌐 前端展示                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def _print_step(self, step: int, title: str, description: str = ""):
        """打印步骤信息"""
        print(f"\n{'='*80}")
        print(f"📋 步骤 {step}: {title}")
        if description:
            print(f"   {description}")
        print(f"{'='*80}")
    
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
    
    def setup_demo_device(self) -> bool:
        """设置演示设备"""
        self._print_step(1, "设置Mock演示设备")
        
        try:
            # 检查设备是否已存在
            existing_device = self.generator.get_device(self.DEFAULT_MAC)
            if existing_device:
                self._print_info(f"演示设备已存在: {existing_device.name} ({self.DEFAULT_MAC})")
                
                # 询问是否重新创建
                choice = input("是否重新创建演示设备? (y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    # 删除现有设备
                    self.generator.remove_device(self.DEFAULT_MAC)
                    print("🗑️  已删除现有设备")
                else:
                    self._print_info("使用现有设备继续演示")
                    return True
            
            # 创建新设备
            device = self.generator.create_device(self.DEFAULT_MAC, self.DEFAULT_DEVICE_NAME)
            
            self._print_success("演示设备创建成功!")
            print(f"   📱 设备名称: {device.name}")
            print(f"   🔗 MAC地址: {device.mac_address}")
            print(f"   📅 创建时间: {device.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 显示支持的传感器类型
            sensor_types = list(self.generator.SENSOR_CONFIGS.keys())
            print(f"   🔧 支持传感器 ({len(sensor_types)} 种):")
            for i, sensor_type in enumerate(sensor_types, 1):
                config = self.generator.SENSOR_CONFIGS[sensor_type]
                print(f"      {i}. {sensor_type} ({config.min_value}-{config.max_value} {config.unit})")
            
            return True
            
        except Exception as e:
            self._print_error(f"设置演示设备失败: {str(e)}")
            return False
    
    def generate_demo_history(self, hours: int) -> bool:
        """生成演示历史数据"""
        if hours <= 0:
            self._print_info("跳过历史数据生成")
            return True
        
        self._print_step(2, f"生成 {hours} 小时历史数据", "为前端图表展示准备数据")
        
        try:
            # 计算数据点数量
            data_points = (hours * 60) // 5  # 每5分钟一个数据点
            print(f"📊 将生成约 {data_points} 个历史数据点")
            print(f"⏰ 数据时间范围: {hours} 小时前 → 现在")
            print(f"📈 数据间隔: 5 分钟")
            
            # 如果数据量大，询问确认
            if data_points > 200:
                print(f"⚠️  注意: 将生成较多数据 ({data_points} 条)，可能需要一些时间")
                choice = input("是否继续? (Y/n): ").strip().lower()
                if choice in ['n', 'no']:
                    self._print_info("跳过历史数据生成")
                    return True
            
            print(f"\n🔄 开始生成历史数据...")
            start_time = time.time()
            
            # 生成历史数据
            results = self.generator.generate_history_data(self.DEFAULT_MAC, hours, 5)
            
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
                self._print_success("历史数据生成成功！")
                print("   📈 现在可以在前端查看历史数据图表了")
            else:
                self._print_warning("历史数据生成失败，但不影响实时数据演示")
            
            return True
            
        except Exception as e:
            self._print_error(f"生成历史数据失败: {str(e)}")
            self._print_warning("历史数据生成失败，但不影响实时数据演示")
            return False
    
    def start_demo_auto_generation(self, interval: int) -> bool:
        """启动演示自动数据生成"""
        self._print_step(3, f"启动自动数据生成", f"每 {interval} 秒生成一次实时数据")
        
        try:
            # 启动自动生成
            success = self.generator.start_auto_generation(self.DEFAULT_MAC, interval)
            
            if success:
                self._print_success("自动数据生成已启动!")
                print(f"   📱 设备: {self.DEFAULT_DEVICE_NAME} ({self.DEFAULT_MAC})")
                print(f"   ⏱️  间隔: {interval} 秒")
                print(f"   🔄 状态: 运行中")
                print(f"   📊 传感器类型: {len(self.generator.SENSOR_CONFIGS)} 种")
                
                # 立即生成一次数据作为演示
                print(f"\n🎯 立即生成一次数据作为演示...")
                demo_success, demo_message = self.generator.generate_and_send_data(self.DEFAULT_MAC)
                
                if demo_success:
                    print(f"✅ 演示数据生成成功: {demo_message}")
                    
                    # 显示生成的数据
                    status = self.generator.get_device_status(self.DEFAULT_MAC)
                    sensor_stats = status.get('sensor_stats', {})
                    if sensor_stats:
                        print(f"   📈 最新传感器数据:")
                        for sensor_type, stats in sensor_stats.items():
                            config = self.generator.SENSOR_CONFIGS.get(sensor_type, {})
                            unit = getattr(config, 'unit', '')
                            print(f"      {sensor_type}: {stats['latest_value']}{unit}")
                else:
                    print(f"⚠️  演示数据生成失败: {demo_message}")
                
            else:
                self._print_error("启动自动生成失败")
            
            return success
            
        except Exception as e:
            self._print_error(f"启动自动生成失败: {str(e)}")
            return False
    
    def show_demo_status(self):
        """显示演示状态"""
        print(f"\n{'='*80}")
        print(f"📊 Mock传感器演示系统状态")
        print(f"{'='*80}")
        
        try:
            status = self.generator.get_device_status(self.DEFAULT_MAC)
            if not status:
                self._print_error("无法获取设备状态")
                return
            
            print(f"📱 设备信息:")
            print(f"   名称: {status['name']}")
            print(f"   MAC: {status['mac_address']}")
            print(f"   状态: {'🟢 活跃' if status['is_active'] else '🔴 非活跃'}")
            print(f"   最后活跃: {status['last_active'] or '从未活跃'}")
            
            print(f"\n🔄 自动生成:")
            print(f"   状态: {'🟢 运行中' if status['auto_generation_active'] else '🔴 已停止'}")
            print(f"   间隔: {status['generation_interval']} 秒")
            
            sensor_stats = status.get('sensor_stats', {})
            if sensor_stats:
                total_data = sum(stats['count'] for stats in sensor_stats.values())
                print(f"\n📊 数据统计:")
                print(f"   总数据量: {total_data} 条")
                print(f"   传感器类型: {len(sensor_stats)} 种")
                
                print(f"\n📈 最新数据:")
                for sensor_type, stats in sensor_stats.items():
                    config = self.generator.SENSOR_CONFIGS.get(sensor_type, {})
                    unit = getattr(config, 'unit', '')
                    print(f"   {sensor_type}: {stats['latest_value']}{unit} (共{stats['count']}条)")
            else:
                print(f"\n📊 数据统计: 暂无数据")
            
        except Exception as e:
            self._print_error(f"获取状态失败: {str(e)}")
    
    def start_status_monitor(self):
        """启动状态监控线程"""
        def monitor_loop():
            while self._running:
                try:
                    time.sleep(60)  # 每分钟更新一次
                    if self._running:
                        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Mock演示系统运行中...")
                        
                        # 显示简要状态
                        status = self.generator.get_device_status(self.DEFAULT_MAC)
                        if status:
                            sensor_stats = status.get('sensor_stats', {})
                            if sensor_stats:
                                total_data = sum(stats['count'] for stats in sensor_stats.values())
                                print(f"   📊 累计生成数据: {total_data} 条")
                            
                            if status['auto_generation_active']:
                                next_generation = status['generation_interval']
                                print(f"   ⏱️  下次生成: {next_generation} 秒后")
                        
                except Exception as e:
                    if self._running:  # 只在运行状态下报告错误
                        print(f"⚠️  状态监控异常: {e}")
        
        self._status_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._status_thread.start()
    
    def show_usage_instructions(self):
        """显示使用说明"""
        print(f"\n{'='*80}")
        print(f"🎯 Mock演示系统使用指南")
        print(f"{'='*80}")
        
        print(f"📋 前端验证步骤:")
        print(f"   1. 打开传感器监控页面")
        print(f"   2. 选择设备: {self.DEFAULT_MAC}")
        print(f"   3. 查看实时数据更新")
        print(f"   4. 测试历史数据查询")
        print(f"   5. 验证告警功能")
        
        print(f"\n🛠️  系统控制命令:")
        print(f"   查看状态: python mock_sensor_cli.py status --mac {self.DEFAULT_MAC}")
        print(f"   停止自动: python mock_sensor_cli.py auto-stop --mac {self.DEFAULT_MAC}")
        print(f"   手动生成: python mock_sensor_cli.py generate --mac {self.DEFAULT_MAC}")
        print(f"   设备列表: python mock_sensor_cli.py list")
        
        print(f"\n⌨️  演示控制:")
        print(f"   按 Ctrl+C 安全退出演示")
        print(f"   按 Enter 显示当前状态")
        print(f"   输入 'help' 显示帮助信息")
        print(f"   输入 'quit' 退出演示")
    
    def interactive_control(self):
        """交互式控制界面"""
        print(f"\n🎮 进入交互式控制模式...")
        print(f"   输入命令或按 Enter 查看状态，输入 'help' 获取帮助")
        
        while self._running:
            try:
                command = input(f"\n[Mock演示] ").strip().lower()
                
                if not command:
                    # 显示状态
                    self.show_demo_status()
                
                elif command in ['help', 'h']:
                    self.show_usage_instructions()
                
                elif command in ['quit', 'exit', 'q']:
                    print("👋 退出演示...")
                    self._signal_handler(signal.SIGINT, None)
                
                elif command in ['status', 's']:
                    self.show_demo_status()
                
                elif command in ['generate', 'g']:
                    print("🔄 手动生成一次数据...")
                    success, message = self.generator.generate_and_send_data(self.DEFAULT_MAC)
                    if success:
                        print(f"✅ {message}")
                    else:
                        print(f"❌ {message}")
                
                elif command.startswith('interval'):
                    # 更改生成间隔
                    parts = command.split()
                    if len(parts) == 2 and parts[1].isdigit():
                        new_interval = int(parts[1])
                        if 5 <= new_interval <= 3600:
                            self.generator.stop_auto_generation(self.DEFAULT_MAC)
                            time.sleep(1)
                            success = self.generator.start_auto_generation(self.DEFAULT_MAC, new_interval)
                            if success:
                                print(f"✅ 生成间隔已更改为 {new_interval} 秒")
                            else:
                                print("❌ 更改间隔失败")
                        else:
                            print("❌ 间隔必须在 5-3600 秒之间")
                    else:
                        print("❌ 用法: interval <秒数>")
                
                else:
                    print(f"❓ 未知命令: {command}")
                    print("   输入 'help' 查看可用命令")
                
            except EOFError:
                # Ctrl+D
                print("\n👋 退出演示...")
                self._signal_handler(signal.SIGINT, None)
            except KeyboardInterrupt:
                # Ctrl+C
                self._signal_handler(signal.SIGINT, None)
    
    def run_demo(self, history_hours: int, interval: int, skip_history: bool) -> bool:
        """运行完整演示"""
        try:
            # 打印欢迎横幅
            self._print_banner()
            
            # 步骤1: 设置演示设备
            if not self.setup_demo_device():
                return False
            
            # 步骤2: 生成历史数据
            if not skip_history:
                if not self.generate_demo_history(history_hours):
                    # 历史数据失败不影响继续
                    pass
            
            # 步骤3: 启动自动生成
            if not self.start_demo_auto_generation(interval):
                return False
            
            # 显示使用说明
            self.show_usage_instructions()
            
            # 启动状态监控
            self.start_status_monitor()
            
            # 进入交互式控制
            self.interactive_control()
            
            return True
            
        except Exception as e:
            self._print_error(f"演示运行失败: {str(e)}")
            return False


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Mock传感器数据快速演示脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
演示流程:
  1. 创建默认Mock设备 (MAC: 00:1A:2B:3C:4D:5E)
  2. 生成历史数据用于图表展示
  3. 启动自动数据生成
  4. 提供交互式控制界面

前端验证:
  - 打开传感器监控页面
  - 选择设备: 00:1A:2B:3C:4D:5E
  - 查看实时数据和历史图表

示例用法:
  python start_mock_demo.py                    # 默认配置
  python start_mock_demo.py --hours 4          # 生成4小时历史数据
  python start_mock_demo.py --interval 60      # 60秒间隔
  python start_mock_demo.py --skip-history     # 跳过历史数据
        """
    )
    
    parser.add_argument(
        '--hours', 
        type=int, 
        default=MockDemoRunner.DEFAULT_HISTORY_HOURS,
        help=f'历史数据小时数 (默认: {MockDemoRunner.DEFAULT_HISTORY_HOURS})'
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=MockDemoRunner.DEFAULT_INTERVAL,
        help=f'自动生成间隔秒数 (默认: {MockDemoRunner.DEFAULT_INTERVAL})'
    )
    
    parser.add_argument(
        '--skip-history', 
        action='store_true',
        help='跳过历史数据生成'
    )
    
    return parser


def main():
    """主函数"""
    try:
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # 验证参数
        if args.hours < 0 or args.hours > 168:
            print("❌ 历史数据小时数必须在 0-168 之间")
            return 1
        
        if args.interval < 5 or args.interval > 3600:
            print("❌ 生成间隔必须在 5-3600 秒之间")
            return 1
        
        # 创建并运行演示
        demo = MockDemoRunner()
        success = demo.run_demo(
            history_hours=0 if args.skip_history else args.hours,
            interval=args.interval,
            skip_history=args.skip_history
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🔄 用户中断演示")
        return 130
    except Exception as e:
        print(f"❌ 演示异常: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

