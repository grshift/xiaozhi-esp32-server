-- 执行器模块核心数据表创建脚本

-- 1. 执行器类型定义表
CREATE TABLE IF NOT EXISTS `ai_actuator_type` (
    `id` VARCHAR(32) NOT NULL COMMENT '执行器类型ID',
    `type_code` VARCHAR(50) NOT NULL COMMENT '类型编码(pump/valve/switch等)',
    `type_name` VARCHAR(100) NOT NULL COMMENT '类型名称',
    `category` VARCHAR(50) COMMENT '分类(water/electric/air等)',
    `icon` VARCHAR(100) COMMENT '图标',
    `description` VARCHAR(500) COMMENT '描述',
    `default_config` JSON COMMENT '默认配置参数',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT '排序',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_type_code` (`type_code`),
    INDEX `idx_category` (`category`),
    INDEX `idx_sort` (`sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='执行器类型定义表';

-- 2. 设备执行器配置表
CREATE TABLE IF NOT EXISTS `ai_device_actuator` (
    `id` VARCHAR(32) NOT NULL COMMENT '主键ID',
    `device_id` VARCHAR(32) NOT NULL COMMENT '设备ID(关联ai_device)',
    `actuator_type_id` VARCHAR(32) NOT NULL COMMENT '执行器类型ID',
    `actuator_code` VARCHAR(50) NOT NULL COMMENT '执行器编码(设备内唯一)',
    `actuator_name` VARCHAR(100) COMMENT '执行器名称',
    `gpio_pin` VARCHAR(20) COMMENT 'GPIO引脚配置',
    `config_json` JSON COMMENT '执行器配置参数',
    `calibration_data` JSON COMMENT '校准数据',
    `last_command` VARCHAR(50) COMMENT '最后执行的命令',
    `last_command_at` DATETIME(3) COMMENT '最后命令执行时间',
    `last_status` VARCHAR(50) COMMENT '最后状态',
    `last_updated_at` DATETIME(3) COMMENT '最后更新时间',
    `is_enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用(0-禁用,1-启用)',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0-离线,1-正常,2-异常)',
    `sort` INT UNSIGNED DEFAULT 0 COMMENT '排序',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_device_actuator` (`device_id`, `actuator_code`),
    INDEX `idx_device_id` (`device_id`),
    INDEX `idx_actuator_type` (`actuator_type_id`),
    INDEX `idx_status` (`status`),
    CONSTRAINT `fk_device_actuator_device` FOREIGN KEY (`device_id`) REFERENCES `ai_device` (`id`),
    CONSTRAINT `fk_device_actuator_type` FOREIGN KEY (`actuator_type_id`) REFERENCES `ai_actuator_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备执行器配置表';

-- 3. 执行器数据日志表
CREATE TABLE IF NOT EXISTS `ai_actuator_data` (
    `id` VARCHAR(32) NOT NULL COMMENT '数据日志ID',
    `device_id` VARCHAR(32) NOT NULL COMMENT '设备ID',
    `actuator_id` VARCHAR(32) NOT NULL COMMENT '执行器ID',
    `actuator_code` VARCHAR(50) NOT NULL COMMENT '执行器编码',
    `command` VARCHAR(50) NOT NULL COMMENT '执行命令',
    `command_params` JSON COMMENT '命令参数',
    `response_status` VARCHAR(20) COMMENT '响应状态',
    `response_message` VARCHAR(500) COMMENT '响应消息',
    `executed_at` DATETIME(3) NOT NULL COMMENT '执行时间',
    `execution_duration` INT COMMENT '执行耗时(毫秒)',
    `creator` BIGINT COMMENT '创建者',
    `create_date` DATETIME COMMENT '创建时间',
    `updater` BIGINT COMMENT '更新者',
    `update_date` DATETIME COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_device_id` (`device_id`),
    INDEX `idx_actuator_id` (`actuator_id`),
    INDEX `idx_executed_at` (`executed_at`),
    INDEX `idx_command` (`command`),
    CONSTRAINT `fk_actuator_data_device` FOREIGN KEY (`device_id`) REFERENCES `ai_device` (`id`),
    CONSTRAINT `fk_actuator_data_actuator` FOREIGN KEY (`actuator_id`) REFERENCES `ai_device_actuator` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='执行器数据日志表';

-- 插入默认的水泵类型数据
INSERT IGNORE INTO `ai_actuator_type` (`id`, `type_code`, `type_name`, `category`, `icon`, `description`, `default_config`, `sort`, `creator`, `create_date`) VALUES
('actuator_type_pump', 'pump', '水泵', 'water', 'pump-icon', '水泵执行器，用于控制水的流动', '{"maxFlowRate": 100.0, "maxDuration": 3600}', 1, 1, NOW());
