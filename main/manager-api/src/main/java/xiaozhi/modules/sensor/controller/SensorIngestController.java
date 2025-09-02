package xiaozhi.modules.sensor.controller;

import java.math.BigDecimal;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.sensor.alert.SensorAlertEngine;
import xiaozhi.modules.sensor.dto.SensorReportDTO;
import xiaozhi.modules.sensor.entity.DeviceSensorEntity;
import xiaozhi.modules.sensor.entity.SensorDataEntity;
import xiaozhi.modules.sensor.service.DeviceSensorService;
import xiaozhi.modules.sensor.service.SensorDataService;

/**
 * 传感器数据上报控制器
 */
@Slf4j
@RestController
@RequestMapping("/xiaozhi/sensor")
@Tag(name = "传感器数据上报")
public class SensorIngestController {

    @Autowired
    private DeviceService deviceService;

    @Autowired
    private DeviceSensorService deviceSensorService;

    @Autowired
    private SensorDataService sensorDataService;

    @Autowired
    private RedisUtils redisUtils;

    @Autowired
    private SensorAlertEngine sensorAlertEngine;

    @PostMapping("/data/report")
    @Operation(summary = "ESP32传感器数据上报")
    @Transactional(rollbackFor = Exception.class)
    public Result<Boolean> report(@RequestBody SensorReportDTO payload) {
        if (payload == null || payload.getSensors() == null || payload.getSensors().isEmpty()) {
            log.warn("Empty sensor data payload");
            return new Result<Boolean>().ok(true);
        }

        // 根据MAC地址查找设备
        DeviceEntity device = deviceService.getDeviceByMacAddress(payload.getMacAddress());
        if (device == null) {
            log.warn("Device not found for MAC: {}", payload.getMacAddress());
            return new Result<Boolean>().ok(false);
        }

        Date collectedAt = payload.getTimestamp() != null ? payload.getTimestamp() : new Date();
        
        // 处理每个传感器数据
        for (SensorReportDTO.SensorItem item : payload.getSensors()) {
            try {
                // 查找传感器配置
                DeviceSensorEntity sensor = deviceSensorService.lambdaQuery()
                        .eq(DeviceSensorEntity::getDeviceId, device.getId())
                        .eq(DeviceSensorEntity::getSensorCode, item.getSensorCode())
                        .eq(DeviceSensorEntity::getIsEnabled, 1)
                        .one();

                if (sensor == null) {
                    log.debug("Sensor not found or disabled: deviceId={}, sensorCode={}", 
                            device.getId(), item.getSensorCode());
                    continue;
                }

                // 保存传感器数据记录
                SensorDataEntity data = new SensorDataEntity();
                data.setDeviceId(device.getId());
                data.setSensorId(sensor.getId());
                data.setSensorCode(sensor.getSensorCode());
                data.setValue(item.getValue() != null ? BigDecimal.valueOf(item.getValue()) : null);
                data.setRawValue(item.getValue() != null ? String.valueOf(item.getValue()) : null);
                data.setQuality(1); // 默认质量为正常
                data.setCollectedAt(collectedAt);
                data.setCreatedAt(new Date());
                sensorDataService.save(data);

                // 更新传感器最新值和时间
                deviceSensorService.lambdaUpdate()
                        .eq(DeviceSensorEntity::getId, sensor.getId())
                        .set(DeviceSensorEntity::getLastValue, data.getValue())
                        .set(DeviceSensorEntity::getLastUpdatedAt, collectedAt)
                        .set(DeviceSensorEntity::getStatus, 1) // 设置为正常状态
                        .update();

                // 缓存实时数据到Redis
                String realtimeKey = RedisKeys.getSensorRealtimeKey(device.getId(), sensor.getSensorCode());
                redisUtils.set(realtimeKey, data.getValue(), 60); // 缓存60秒

                // 检查告警条件
                if (data.getValue() != null) {
                    sensorAlertEngine.checkAndTrigger(device.getId(), sensor.getId(), 
                            sensor.getSensorCode(), data.getValue());
                }

                log.debug("Sensor data saved: deviceId={}, sensorCode={}, value={}", 
                        device.getId(), item.getSensorCode(), item.getValue());

            } catch (Exception e) {
                log.error("Error processing sensor data: deviceId={}, sensorCode={}, error={}", 
                        device.getId(), item.getSensorCode(), e.getMessage(), e);
                // 继续处理其他传感器数据
            }
        }

        return new Result<Boolean>().ok(true);
    }
}
