-- 传感器模块核心数据表创建脚本

-- 1. 传感器类型定义表
CREATE TABLE IF NOT EXISTS `ai_sensor_type` (
    `id` VARCHAR(32) NOT NULL COMMENT '传感器类型ID',
    `type_code` VARCHAR(50) NOT NULL COMMENT '类型编码(temperature/humidity/light等)',
    `type_name` VARCHAR(100) NOT NULL COMMENT '类型名称',
    `unit` VARCHAR(20) COMMENT '数据单位(℃/%/lux等)',
    `data_type` VARCHAR(20) NOT NULL COMMENT '数据类型(number/boolean/string)',
    `icon` VARCHAR(100) COMMENT '图标',
    `description` VARCHAR(500) COMMENT '描述',
    `value_range` JSON COMMENT '数值范围配置 {"min": 0, "max": 100}',
    `precision` INT DEFAULT 2 COMMENT '数据精度(小数位数)',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT '排序',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_type_code` (`type_code`),
    INDEX `idx_sort` (`sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器类型定义表';

-- 2. 设备传感器配置表
CREATE TABLE IF NOT EXISTS `ai_device_sensor` (
    `id` VARCHAR(32) NOT NULL COMMENT '主键ID',
    `device_id` VARCHAR(32) NOT NULL COMMENT '设备ID(关联ai_device)',
    `sensor_type_id` VARCHAR(32) NOT NULL COMMENT '传感器类型ID',
    `sensor_code` VARCHAR(50) NOT NULL COMMENT '传感器编码(设备内唯一)',
    `sensor_name` VARCHAR(100) COMMENT '传感器名称',
    `gpio_pin` VARCHAR(20) COMMENT 'GPIO引脚配置',
    `config_json` JSON COMMENT '传感器配置参数',
    `calibration_data` JSON COMMENT '校准数据',
    `is_enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `location` VARCHAR(100) COMMENT '传感器位置(客厅/卧室等)',
    `last_value` DECIMAL(20,6) COMMENT '最新数值',
    `last_updated_at` DATETIME(3) COMMENT '最新更新时间',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0-离线,1-正常,2-异常)',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT '排序',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_device_sensor` (`device_id`, `sensor_code`),
    INDEX `idx_device_id` (`device_id`),
    INDEX `idx_sensor_type` (`sensor_type_id`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_device_sensor_device` FOREIGN KEY (`device_id`) REFERENCES `ai_device` (`id`),
    CONSTRAINT `fk_device_sensor_type` FOREIGN KEY (`sensor_type_id`) REFERENCES `ai_sensor_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备传感器配置表';

-- 3. 传感器数据记录表(时序数据)
CREATE TABLE IF NOT EXISTS `ai_sensor_data` (
    `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
    `device_id` VARCHAR(32) NOT NULL COMMENT '设备ID',
    `sensor_id` VARCHAR(32) NOT NULL COMMENT '传感器ID',
    `sensor_code` VARCHAR(50) NOT NULL COMMENT '传感器编码',
    `value` DECIMAL(20,6) NOT NULL COMMENT '数据值',
    `raw_value` VARCHAR(100) COMMENT '原始值',
    `quality` TINYINT DEFAULT 1 COMMENT '数据质量(0-差,1-正常,2-优)',
    `collected_at` DATETIME(3) NOT NULL COMMENT '采集时间',
    `created_at` DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    PRIMARY KEY (`id`, `collected_at`),
    INDEX `idx_device_sensor_time` (`device_id`, `sensor_id`, `collected_at`),
    INDEX `idx_collected_at` (`collected_at`),
    INDEX `idx_sensor_code` (`sensor_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据记录表'
PARTITION BY RANGE (TO_DAYS(`collected_at`)) (
    PARTITION p202501 VALUES LESS THAN (TO_DAYS('2025-02-01')),
    PARTITION p202502 VALUES LESS THAN (TO_DAYS('2025-03-01')),
    PARTITION p202503 VALUES LESS THAN (TO_DAYS('2025-04-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- 4. 传感器数据聚合表(小时/日/月统计)
CREATE TABLE IF NOT EXISTS `ai_sensor_data_aggregate` (
    `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
    `device_id` VARCHAR(32) NOT NULL COMMENT '设备ID',
    `sensor_id` VARCHAR(32) NOT NULL COMMENT '传感器ID',
    `aggregate_type` VARCHAR(20) NOT NULL COMMENT '聚合类型(hour/day/month)',
    `aggregate_time` DATETIME NOT NULL COMMENT '聚合时间',
    `avg_value` DECIMAL(20,6) COMMENT '平均值',
    `max_value` DECIMAL(20,6) COMMENT '最大值',
    `min_value` DECIMAL(20,6) COMMENT '最小值',
    `sum_value` DECIMAL(20,6) COMMENT '总和',
    `count` INT COMMENT '数据点数',
    `std_deviation` DECIMAL(20,6) COMMENT '标准差',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_aggregate` (`device_id`, `sensor_id`, `aggregate_type`, `aggregate_time`),
    INDEX `idx_aggregate_time` (`aggregate_time`),
    INDEX `idx_device_sensor` (`device_id`, `sensor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据聚合表';

-- 5. 传感器告警规则表
CREATE TABLE IF NOT EXISTS `ai_sensor_alert_rule` (
    `id` VARCHAR(32) NOT NULL COMMENT '规则ID',
    `rule_name` VARCHAR(100) NOT NULL COMMENT '规则名称',
    `device_id` VARCHAR(32) COMMENT '设备ID(null表示全局规则)',
    `sensor_id` VARCHAR(32) COMMENT '传感器ID(null表示设备所有传感器)',
    `sensor_type_id` VARCHAR(32) COMMENT '传感器类型ID(用于全局规则)',
    `condition_type` VARCHAR(20) NOT NULL COMMENT '条件类型(threshold/range/change_rate)',
    `condition_config` JSON NOT NULL COMMENT '条件配置',
    `alert_level` TINYINT NOT NULL COMMENT '告警级别(1-提示,2-警告,3-严重)',
    `alert_message` VARCHAR(500) COMMENT '告警消息模板',
    `action_type` VARCHAR(50) COMMENT '动作类型(notification/voice/plugin)',
    `action_config` JSON COMMENT '动作配置',
    `cooldown_minutes` INT DEFAULT 30 COMMENT '冷却时间(分钟)',
    `is_enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `last_triggered_at` DATETIME COMMENT '最后触发时间',
    `trigger_count` INT DEFAULT 0 COMMENT '触发次数',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_device_sensor` (`device_id`, `sensor_id`),
    INDEX `idx_sensor_type` (`sensor_type_id`),
    INDEX `idx_enabled` (`is_enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器告警规则表';

-- 6. 传感器告警记录表
CREATE TABLE IF NOT EXISTS `ai_sensor_alert_log` (
    `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
    `rule_id` VARCHAR(32) NOT NULL COMMENT '规则ID',
    `device_id` VARCHAR(32) NOT NULL COMMENT '设备ID',
    `sensor_id` VARCHAR(32) NOT NULL COMMENT '传感器ID',
    `alert_level` TINYINT NOT NULL COMMENT '告警级别',
    `alert_message` VARCHAR(500) COMMENT '告警消息',
    `sensor_value` DECIMAL(20,6) COMMENT '触发时的传感器值',
    `threshold_value` VARCHAR(100) COMMENT '阈值配置',
    `is_resolved` TINYINT(1) DEFAULT 0 COMMENT '是否已解决',
    `resolved_at` DATETIME COMMENT '解决时间',
    `resolved_by` BIGINT COMMENT '解决人',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    INDEX `idx_rule_id` (`rule_id`),
    INDEX `idx_device_sensor` (`device_id`, `sensor_id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_resolved` (`is_resolved`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器告警记录表';

-- 7. 传感器数据导出任务表
CREATE TABLE IF NOT EXISTS `ai_sensor_export_task` (
    `id` VARCHAR(32) NOT NULL COMMENT '任务ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `task_name` VARCHAR(100) COMMENT '任务名称',
    `device_ids` JSON COMMENT '设备ID列表',
    `sensor_ids` JSON COMMENT '传感器ID列表',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME NOT NULL COMMENT '结束时间',
    `export_format` VARCHAR(20) NOT NULL COMMENT '导出格式(csv/excel/json)',
    `status` VARCHAR(20) NOT NULL COMMENT '状态(pending/processing/completed/failed)',
    `file_path` VARCHAR(500) COMMENT '文件路径',
    `file_size` BIGINT COMMENT '文件大小(字节)',
    `row_count` INT COMMENT '数据行数',
    `error_message` TEXT COMMENT '错误信息',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `completed_at` DATETIME COMMENT '完成时间',
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据导出任务表';

-- 初始化传感器类型数据
INSERT IGNORE INTO `ai_sensor_type` (`id`, `type_code`, `type_name`, `unit`, `data_type`, `description`, `precision`, `sort`, `creator`, `create_date`) VALUES
('ST001', 'temperature', '温度传感器', '℃', 'number', '检测环境温度', 2, 1, 1, NOW()),
('ST002', 'humidity', '湿度传感器', '%', 'number', '检测环境湿度', 2, 2, 1, NOW()),
('ST003', 'light', '光照传感器', 'lux', 'number', '检测环境光照强度', 0, 3, 1, NOW()),
('ST004', 'motion', '运动传感器', '', 'boolean', '检测是否有运动', 0, 4, 1, NOW()),
('ST005', 'air_quality', '空气质量传感器', 'ppm', 'number', '检测空气质量指数', 0, 5, 1, NOW());
