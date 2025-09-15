-- 确保执行器类型数据存在
-- 如果数据不存在则插入

INSERT IGNORE INTO `ai_actuator_type` (
    `id`, 
    `type_code`, 
    `type_name`, 
    `category`, 
    `icon`, 
    `description`, 
    `default_config`, 
    `sort`, 
    `creator`, 
    `create_date`
) VALUES (
    'actuator_type_pump', 
    'pump', 
    '水泵', 
    'water', 
    'pump-icon', 
    '水泵执行器，用于控制水的流动', 
    '{"maxFlowRate": 100.0, "maxDuration": 3600}', 
    1, 
    1, 
    NOW()
);

-- 验证数据是否插入成功
SELECT COUNT(*) as pump_type_count FROM `ai_actuator_type` WHERE `type_code` = 'pump';
