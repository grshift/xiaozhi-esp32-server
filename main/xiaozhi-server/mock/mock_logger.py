"""
Mock传感器数据生成器专用日志配置

提供专门的日志配置和工具类，用于Mock传感器系统的详细日志记录：
- 结构化日志记录
- 性能监控日志
- 错误追踪日志
- 状态变化日志
- 数据统计日志
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger
from dataclasses import dataclass

@dataclass
class MockLogConfig:
    """Mock日志配置"""
    log_level: str = "INFO"
    log_dir: str = "tmp/mock_logs"
    console_output: bool = True
    file_output: bool = True
    max_file_size: str = "10 MB"
    retention_days: int = 7
    
class MockLogger:
    """Mock传感器专用日志器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, config: Optional[MockLogConfig] = None):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[MockLogConfig] = None):
        if not self._initialized:
            self.config = config or MockLogConfig()
            self._setup_logger()
            self._initialized = True
    
    def _setup_logger(self):
        """设置Mock专用日志器"""
        # 创建日志目录
        os.makedirs(self.config.log_dir, exist_ok=True)
        
        # 移除默认处理器
        logger.remove()
        
        # 控制台输出格式
        console_format = (
            "<green>{time:MM-DD HH:mm:ss}</green> "
            "[<cyan>MOCK</cyan>] "
            "<level>{level: <8}</level> "
            "<light-blue>{extra[component]: <12}</light-blue> "
            "<level>{message}</level>"
        )
        
        # 文件输出格式
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "MOCK | {level: <8} | "
            "{extra[component]: <12} | "
            "{extra[device_mac]:<17} | "
            "{extra[operation]: <15} | "
            "{message}"
        )
        
        # 添加控制台处理器
        if self.config.console_output:
            logger.add(
                sys.stdout,
                format=console_format,
                level=self.config.log_level,
                filter=self._console_filter
            )
        
        # 添加文件处理器
        if self.config.file_output:
            # 主日志文件
            main_log_file = os.path.join(self.config.log_dir, "mock_sensor.log")
            logger.add(
                main_log_file,
                format=file_format,
                level="DEBUG",
                rotation=self.config.max_file_size,
                retention=f"{self.config.retention_days} days",
                compression="zip",
                encoding="utf-8",
                enqueue=True,
                filter=self._file_filter
            )
            
            # 错误日志文件
            error_log_file = os.path.join(self.config.log_dir, "mock_errors.log")
            logger.add(
                error_log_file,
                format=file_format,
                level="ERROR",
                rotation=self.config.max_file_size,
                retention=f"{self.config.retention_days} days",
                compression="zip",
                encoding="utf-8",
                enqueue=True,
                filter=self._error_filter
            )
            
            # 性能日志文件
            perf_log_file = os.path.join(self.config.log_dir, "mock_performance.log")
            logger.add(
                perf_log_file,
                format=file_format,
                level="INFO",
                rotation=self.config.max_file_size,
                retention=f"{self.config.retention_days} days",
                compression="zip",
                encoding="utf-8",
                enqueue=True,
                filter=self._performance_filter
            )
    
    def _console_filter(self, record):
        """控制台输出过滤器"""
        # 设置默认值
        record["extra"].setdefault("component", "UNKNOWN")
        record["extra"].setdefault("device_mac", "")
        record["extra"].setdefault("operation", "")
        return True
    
    def _file_filter(self, record):
        """文件输出过滤器"""
        # 设置默认值
        record["extra"].setdefault("component", "UNKNOWN")
        record["extra"].setdefault("device_mac", "")
        record["extra"].setdefault("operation", "")
        return True
    
    def _error_filter(self, record):
        """错误日志过滤器"""
        self._file_filter(record)
        return record["level"].name in ["ERROR", "CRITICAL"]
    
    def _performance_filter(self, record):
        """性能日志过滤器"""
        self._file_filter(record)
        return record["extra"].get("log_type") == "PERFORMANCE"
    
    def get_logger(self, component: str, device_mac: str = "", operation: str = ""):
        """获取绑定了上下文的日志器"""
        return logger.bind(
            component=component,
            device_mac=device_mac,
            operation=operation
        )
    
    def get_performance_logger(self, component: str, device_mac: str = "", operation: str = ""):
        """获取性能日志器"""
        return logger.bind(
            component=component,
            device_mac=device_mac,
            operation=operation,
            log_type="PERFORMANCE"
        )


class MockLoggerHelper:
    """Mock日志记录辅助类"""
    
    def __init__(self, component: str, device_mac: str = ""):
        self.component = component
        self.device_mac = device_mac
        self.mock_logger = MockLogger()
        self._operation_start_times = {}
    
    def get_logger(self, operation: str = ""):
        """获取日志器"""
        return self.mock_logger.get_logger(
            self.component, 
            self.device_mac, 
            operation
        )
    
    def info(self, message: str, operation: str = "", **kwargs):
        """记录信息日志"""
        log = self.get_logger(operation)
        log.info(message, **kwargs)
    
    def debug(self, message: str, operation: str = "", **kwargs):
        """记录调试日志"""
        log = self.get_logger(operation)
        log.debug(message, **kwargs)
    
    def warning(self, message: str, operation: str = "", **kwargs):
        """记录警告日志"""
        log = self.get_logger(operation)
        log.warning(message, **kwargs)
    
    def error(self, message: str, operation: str = "", **kwargs):
        """记录错误日志"""
        log = self.get_logger(operation)
        log.error(message, **kwargs)
    
    def critical(self, message: str, operation: str = "", **kwargs):
        """记录严重错误日志"""
        log = self.get_logger(operation)
        log.critical(message, **kwargs)
    
    def start_operation(self, operation: str, details: str = ""):
        """开始操作记录"""
        start_time = datetime.now()
        self._operation_start_times[operation] = start_time
        
        log = self.get_logger(operation)
        log.info(f"开始操作: {operation} {details}")
        
        return start_time
    
    def end_operation(self, operation: str, success: bool = True, details: str = ""):
        """结束操作记录"""
        end_time = datetime.now()
        start_time = self._operation_start_times.get(operation)
        
        duration = None
        if start_time:
            duration = (end_time - start_time).total_seconds()
            del self._operation_start_times[operation]
        
        log = self.get_logger(operation)
        status = "成功" if success else "失败"
        
        if duration is not None:
            log.info(f"操作{status}: {operation} (耗时: {duration:.3f}s) {details}")
            
            # 记录性能日志
            perf_log = self.mock_logger.get_performance_logger(
                self.component, 
                self.device_mac, 
                operation
            )
            perf_log.info(f"操作耗时: {duration:.3f}s, 状态: {status}, 详情: {details}")
        else:
            log.info(f"操作{status}: {operation} {details}")
    
    def log_data_generation(self, sensor_type: str, value: Any, success: bool = True):
        """记录数据生成日志"""
        operation = "DATA_GENERATION"
        log = self.get_logger(operation)
        
        if success:
            log.debug(f"生成传感器数据: {sensor_type}={value}")
        else:
            log.error(f"生成传感器数据失败: {sensor_type}")
    
    def log_data_sending(self, sensor_count: int, success: bool = True, message: str = ""):
        """记录数据发送日志"""
        operation = "DATA_SENDING"
        log = self.get_logger(operation)
        
        if success:
            log.info(f"数据发送成功: {sensor_count} 个传感器, {message}")
        else:
            log.error(f"数据发送失败: {sensor_count} 个传感器, {message}")
    
    def log_device_operation(self, action: str, device_name: str = "", success: bool = True, details: str = ""):
        """记录设备操作日志"""
        operation = "DEVICE_MGMT"
        log = self.get_logger(operation)
        
        device_info = f"设备: {device_name}" if device_name else f"MAC: {self.device_mac}"
        status = "成功" if success else "失败"
        
        log.info(f"设备{action}{status}: {device_info} {details}")
    
    def log_auto_generation_status(self, action: str, interval: int = 0, success: bool = True):
        """记录自动生成状态日志"""
        operation = "AUTO_GENERATION"
        log = self.get_logger(operation)
        
        status = "成功" if success else "失败"
        interval_info = f"间隔: {interval}s" if interval > 0 else ""
        
        log.info(f"自动生成{action}{status}: MAC: {self.device_mac} {interval_info}")
    
    def log_statistics(self, stats: Dict[str, Any]):
        """记录统计信息日志"""
        operation = "STATISTICS"
        log = self.get_logger(operation)
        
        stats_info = []
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                stats_info.append(f"{key}={value}")
            else:
                stats_info.append(f"{key}={str(value)}")
        
        log.info(f"统计信息: {', '.join(stats_info)}")


# 全局日志器实例
_mock_logger_instance = None

def get_mock_logger(config: Optional[MockLogConfig] = None) -> MockLogger:
    """获取全局Mock日志器实例"""
    global _mock_logger_instance
    if _mock_logger_instance is None:
        _mock_logger_instance = MockLogger(config)
    return _mock_logger_instance

def create_mock_logger_helper(component: str, device_mac: str = "") -> MockLoggerHelper:
    """创建Mock日志辅助器"""
    return MockLoggerHelper(component, device_mac)

# 便捷函数
def setup_mock_logging(log_level: str = "INFO", log_dir: str = "tmp/mock_logs", console_output: bool = True):
    """快速设置Mock日志"""
    config = MockLogConfig(
        log_level=log_level,
        log_dir=log_dir,
        console_output=console_output
    )
    return get_mock_logger(config)

