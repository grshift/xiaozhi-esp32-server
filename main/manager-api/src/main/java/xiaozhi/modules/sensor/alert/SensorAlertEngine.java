package xiaozhi.modules.sensor.alert;

import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.extern.slf4j.Slf4j;
import xiaozhi.modules.sensor.entity.SensorAlertLogEntity;
import xiaozhi.modules.sensor.entity.SensorAlertRuleEntity;
import xiaozhi.modules.sensor.service.SensorAlertLogService;
import xiaozhi.modules.sensor.service.SensorAlertRuleService;

/**
 * 传感器告警引擎
 */
@Slf4j
@Component
public class SensorAlertEngine {

    @Autowired
    private SensorAlertRuleService sensorAlertRuleService;

    @Autowired
    private SensorAlertLogService sensorAlertLogService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 检查传感器值并触发告警
     */
    public void checkAndTrigger(String deviceId, String sensorId, String sensorCode, BigDecimal value) {
        try {
            // 查询适用的告警规则
            List<SensorAlertRuleEntity> rules = sensorAlertRuleService.lambdaQuery()
                    .eq(SensorAlertRuleEntity::getIsEnabled, 1)
                    .and(wrapper -> wrapper
                            .eq(SensorAlertRuleEntity::getDeviceId, deviceId)
                            .eq(SensorAlertRuleEntity::getSensorId, sensorId)
                            .or()
                            .eq(SensorAlertRuleEntity::getDeviceId, deviceId)
                            .isNull(SensorAlertRuleEntity::getSensorId))
                    .list();

            for (SensorAlertRuleEntity rule : rules) {
                if (shouldTriggerAlert(rule, value)) {
                    triggerAlert(rule, deviceId, sensorId, value);
                }
            }
        } catch (Exception e) {
            log.error("告警检查失败: deviceId={}, sensorId={}, value={}", deviceId, sensorId, value, e);
        }
    }

    /**
     * 判断是否应该触发告警
     */
    private boolean shouldTriggerAlert(SensorAlertRuleEntity rule, BigDecimal value) {
        try {
            // 检查冷却时间
            if (rule.getLastTriggeredAt() != null && rule.getCooldownMinutes() != null) {
                long cooldownMs = rule.getCooldownMinutes() * 60 * 1000L;
                if (System.currentTimeMillis() - rule.getLastTriggeredAt().getTime() < cooldownMs) {
                    return false; // 还在冷却期内
                }
            }

            // 解析条件配置
            JsonNode config = objectMapper.readTree(rule.getConditionConfig());
            String conditionType = rule.getConditionType();

            switch (conditionType) {
                case "threshold":
                    return checkThreshold(config, value);
                case "range":
                    return checkRange(config, value);
                case "change_rate":
                    return checkChangeRate(config, value);
                default:
                    log.warn("未知的告警条件类型: {}", conditionType);
                    return false;
            }
        } catch (Exception e) {
            log.error("告警条件检查失败: ruleId={}", rule.getId(), e);
            return false;
        }
    }

    /**
     * 检查阈值条件
     */
    private boolean checkThreshold(JsonNode config, BigDecimal value) {
        if (config.has("operator") && config.has("threshold")) {
            String operator = config.get("operator").asText();
            BigDecimal threshold = BigDecimal.valueOf(config.get("threshold").asDouble());
            
            switch (operator) {
                case ">":
                    return value.compareTo(threshold) > 0;
                case ">=":
                    return value.compareTo(threshold) >= 0;
                case "<":
                    return value.compareTo(threshold) < 0;
                case "<=":
                    return value.compareTo(threshold) <= 0;
                case "==":
                    return value.compareTo(threshold) == 0;
                case "!=":
                    return value.compareTo(threshold) != 0;
            }
        }
        return false;
    }

    /**
     * 检查范围条件
     */
    private boolean checkRange(JsonNode config, BigDecimal value) {
        if (config.has("min") && config.has("max")) {
            BigDecimal min = BigDecimal.valueOf(config.get("min").asDouble());
            BigDecimal max = BigDecimal.valueOf(config.get("max").asDouble());
            return value.compareTo(min) < 0 || value.compareTo(max) > 0;
        }
        return false;
    }

    /**
     * 检查变化率条件（占位实现）
     */
    private boolean checkChangeRate(JsonNode config, BigDecimal value) {
        // TODO: 实现变化率检查
        // 需要查询历史数据计算变化率
        return false;
    }

    /**
     * 触发告警
     */
    private void triggerAlert(SensorAlertRuleEntity rule, String deviceId, String sensorId, BigDecimal value) {
        try {
            // 创建告警记录
            SensorAlertLogEntity alertLog = new SensorAlertLogEntity();
            alertLog.setRuleId(rule.getId());
            alertLog.setDeviceId(deviceId);
            alertLog.setSensorId(sensorId);
            alertLog.setAlertLevel(rule.getAlertLevel());
            alertLog.setAlertMessage(buildAlertMessage(rule, value));
            alertLog.setSensorValue(value);
            alertLog.setThresholdValue(rule.getConditionConfig());
            alertLog.setIsResolved(0);
            alertLog.setCreatedAt(new Date());
            sensorAlertLogService.save(alertLog);

            // 更新规则的触发信息
            sensorAlertRuleService.lambdaUpdate()
                    .eq(SensorAlertRuleEntity::getId, rule.getId())
                    .set(SensorAlertRuleEntity::getLastTriggeredAt, new Date())
                    .setSql("trigger_count = trigger_count + 1")
                    .update();

            // 执行告警动作
            executeAlertAction(rule, alertLog);

            log.info("告警已触发: ruleId={}, deviceId={}, sensorId={}, value={}", 
                    rule.getId(), deviceId, sensorId, value);
        } catch (Exception e) {
            log.error("触发告警失败: ruleId={}", rule.getId(), e);
        }
    }

    /**
     * 构建告警消息
     */
    private String buildAlertMessage(SensorAlertRuleEntity rule, BigDecimal value) {
        String template = rule.getAlertMessage();
        if (template != null) {
            return template.replace("{value}", value.toString())
                          .replace("{rule_name}", rule.getRuleName());
        }
        return String.format("传感器告警: %s, 当前值: %s", rule.getRuleName(), value);
    }

    /**
     * 执行告警动作
     */
    private void executeAlertAction(SensorAlertRuleEntity rule, SensorAlertLogEntity alertLog) {
        try {
            String actionType = rule.getActionType();
            if (actionType == null) {
                return;
            }

            switch (actionType) {
                case "notification":
                    // TODO: 发送通知
                    log.info("发送通知告警: {}", alertLog.getAlertMessage());
                    break;
                case "voice":
                    // TODO: 语音播报
                    log.info("语音播报告警: {}", alertLog.getAlertMessage());
                    break;
                case "plugin":
                    // TODO: 调用插件
                    log.info("调用插件处理告警: {}", alertLog.getAlertMessage());
                    break;
                default:
                    log.warn("未知的告警动作类型: {}", actionType);
            }
        } catch (Exception e) {
            log.error("执行告警动作失败: ruleId={}", rule.getId(), e);
        }
    }
}
