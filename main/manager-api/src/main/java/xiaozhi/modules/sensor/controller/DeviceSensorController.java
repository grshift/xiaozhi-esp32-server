package xiaozhi.modules.sensor.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.sensor.entity.DeviceSensorEntity;
import xiaozhi.modules.sensor.service.DeviceSensorService;

/**
 * 设备传感器配置控制器
 */
@RestController
@RequestMapping("/xiaozhi/sensor/device")
@Tag(name = "设备传感器配置管理")
public class DeviceSensorController {

    @Autowired
    private DeviceSensorService deviceSensorService;

    @PostMapping
    @Operation(summary = "配置设备传感器")
    public Result<String> create(@Validated @RequestBody DeviceSensorEntity entity) {
        deviceSensorService.save(entity);
        return new Result<String>().ok(entity.getId());
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新传感器配置")
    public Result<Boolean> update(@PathVariable("id") String id, @RequestBody DeviceSensorEntity entity) {
        entity.setId(id);
        return new Result<Boolean>().ok(deviceSensorService.updateById(entity));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除传感器配置")
    public Result<Boolean> delete(@PathVariable("id") String id) {
        return new Result<Boolean>().ok(deviceSensorService.removeById(id));
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取传感器配置详情")
    public Result<DeviceSensorEntity> get(@PathVariable("id") String id) {
        return new Result<DeviceSensorEntity>().ok(deviceSensorService.getById(id));
    }

    @GetMapping("/device/{deviceId}")
    @Operation(summary = "获取设备的传感器配置列表")
    public Result<List<DeviceSensorEntity>> listByDevice(@PathVariable("deviceId") String deviceId) {
        return new Result<List<DeviceSensorEntity>>().ok(deviceSensorService.lambdaQuery()
                .eq(DeviceSensorEntity::getDeviceId, deviceId)
                .list());
    }
}
