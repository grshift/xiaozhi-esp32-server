package xiaozhi.modules.sensor.controller;

import java.util.Date;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.sensor.entity.DeviceSensorEntity;
import xiaozhi.modules.sensor.entity.SensorDataEntity;
import xiaozhi.modules.sensor.entity.SensorDataAggregateEntity;
import xiaozhi.modules.sensor.service.DeviceSensorService;
import xiaozhi.modules.sensor.service.SensorDataService;
import xiaozhi.modules.sensor.service.SensorDataAggregateService;

/**
 * 传感器数据查询控制器
 */
@RestController
@RequestMapping("/xiaozhi/sensor/data")
@Tag(name = "传感器数据查询")
public class SensorDataController {

    @Autowired
    private DeviceSensorService deviceSensorService;

    @Autowired
    private SensorDataService sensorDataService;

    @Autowired
    private SensorDataAggregateService sensorDataAggregateService;

    @GetMapping("/realtime")
    @Operation(summary = "实时数据查询")
    public Result<List<DeviceSensorEntity>> realtime(@RequestParam("deviceId") String deviceId) {
        List<DeviceSensorEntity> sensors = deviceSensorService.lambdaQuery()
                .eq(DeviceSensorEntity::getDeviceId, deviceId)
                .eq(DeviceSensorEntity::getIsEnabled, 1)
                .orderByAsc(DeviceSensorEntity::getSort)
                .list();
        return new Result<List<DeviceSensorEntity>>().ok(sensors);
    }

    @GetMapping("/history")
    @Operation(summary = "历史数据查询")
    public Result<List<SensorDataEntity>> history(
            @RequestParam("deviceId") String deviceId,
            @RequestParam("sensorId") String sensorId,
            @RequestParam("start") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date start,
            @RequestParam("end") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date end) {
        List<SensorDataEntity> data = sensorDataService.lambdaQuery()
                .eq(SensorDataEntity::getDeviceId, deviceId)
                .eq(SensorDataEntity::getSensorId, sensorId)
                .between(SensorDataEntity::getCollectedAt, start, end)
                .orderByDesc(SensorDataEntity::getCollectedAt)
                .last("LIMIT 1000") // 限制返回数量
                .list();
        return new Result<List<SensorDataEntity>>().ok(data);
    }

    @GetMapping("/aggregate")
    @Operation(summary = "聚合数据查询")
    public Result<List<SensorDataAggregateEntity>> aggregate(
            @RequestParam("deviceId") String deviceId,
            @RequestParam("sensorId") String sensorId,
            @RequestParam("type") String type,
            @RequestParam("start") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date start,
            @RequestParam("end") @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") Date end) {
        List<SensorDataAggregateEntity> data = sensorDataAggregateService.lambdaQuery()
                .eq(SensorDataAggregateEntity::getDeviceId, deviceId)
                .eq(SensorDataAggregateEntity::getSensorId, sensorId)
                .eq(SensorDataAggregateEntity::getAggregateType, type)
                .between(SensorDataAggregateEntity::getAggregateTime, start, end)
                .orderByDesc(SensorDataAggregateEntity::getAggregateTime)
                .list();
        return new Result<List<SensorDataAggregateEntity>>().ok(data);
    }

    @PostMapping("/export")
    @Operation(summary = "数据导出(占位)")
    public Result<String> export(@RequestBody Object exportRequest) {
        // TODO: 实现数据导出功能
        return new Result<String>().ok("导出功能开发中");
    }
}
