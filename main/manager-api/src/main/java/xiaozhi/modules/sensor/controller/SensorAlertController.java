package xiaozhi.modules.sensor.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.sensor.entity.SensorAlertRuleEntity;
import xiaozhi.modules.sensor.entity.SensorAlertLogEntity;
import xiaozhi.modules.sensor.service.SensorAlertRuleService;
import xiaozhi.modules.sensor.service.SensorAlertLogService;

/**
 * 传感器告警管理控制器
 */
@RestController
@RequestMapping("/xiaozhi/sensor/alert")
@Tag(name = "传感器告警管理")
public class SensorAlertController {

    @Autowired
    private SensorAlertRuleService sensorAlertRuleService;

    @Autowired
    private SensorAlertLogService sensorAlertLogService;

    @PostMapping("/rule")
    @Operation(summary = "创建告警规则")
    public Result<String> createRule(@Validated @RequestBody SensorAlertRuleEntity entity) {
        sensorAlertRuleService.save(entity);
        return new Result<String>().ok(entity.getId());
    }

    @PutMapping("/rule/{id}")
    @Operation(summary = "更新告警规则")
    public Result<Boolean> updateRule(@PathVariable("id") String id, @RequestBody SensorAlertRuleEntity entity) {
        entity.setId(id);
        return new Result<Boolean>().ok(sensorAlertRuleService.updateById(entity));
    }

    @DeleteMapping("/rule/{id}")
    @Operation(summary = "删除告警规则")
    public Result<Boolean> deleteRule(@PathVariable("id") String id) {
        return new Result<Boolean>().ok(sensorAlertRuleService.removeById(id));
    }

    @GetMapping("/rule/list")
    @Operation(summary = "获取告警规则列表")
    public Result<List<SensorAlertRuleEntity>> listRules(@RequestParam(value = "deviceId", required = false) String deviceId) {
        if (deviceId != null) {
            return new Result<List<SensorAlertRuleEntity>>().ok(sensorAlertRuleService.lambdaQuery()
                    .eq(SensorAlertRuleEntity::getDeviceId, deviceId)
                    .list());
        }
        return new Result<List<SensorAlertRuleEntity>>().ok(sensorAlertRuleService.list());
    }

    @GetMapping("/log")
    @Operation(summary = "查询告警记录")
    public Result<List<SensorAlertLogEntity>> listLogs(
            @RequestParam(value = "deviceId", required = false) String deviceId,
            @RequestParam(value = "isResolved", required = false) Integer isResolved) {
        return new Result<List<SensorAlertLogEntity>>().ok(sensorAlertLogService.lambdaQuery()
                .eq(deviceId != null, SensorAlertLogEntity::getDeviceId, deviceId)
                .eq(isResolved != null, SensorAlertLogEntity::getIsResolved, isResolved)
                .orderByDesc(SensorAlertLogEntity::getCreatedAt)
                .last("LIMIT 100")
                .list());
    }

    @PutMapping("/resolve/{id}")
    @Operation(summary = "解决告警")
    public Result<Boolean> resolve(@PathVariable("id") Long id) {
        // TODO: 实现告警解决逻辑，包括设置解决人等
        return new Result<Boolean>().ok(sensorAlertLogService.lambdaUpdate()
                .eq(SensorAlertLogEntity::getId, id)
                .set(SensorAlertLogEntity::getIsResolved, 1)
                .update());
    }
}
