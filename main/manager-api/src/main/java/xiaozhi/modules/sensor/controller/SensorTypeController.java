package xiaozhi.modules.sensor.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.sensor.entity.SensorTypeEntity;
import xiaozhi.modules.sensor.service.SensorTypeService;

/**
 * 传感器类型管理控制器
 */
@RestController
@RequestMapping("/xiaozhi/sensor/type")
@Tag(name = "传感器类型管理")
public class SensorTypeController {

    @Autowired
    private SensorTypeService sensorTypeService;

    @PostMapping
    @Operation(summary = "创建传感器类型")
    public Result<String> create(@Validated @RequestBody SensorTypeEntity entity) {
        sensorTypeService.save(entity);
        return new Result<String>().ok(entity.getId());
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新传感器类型")
    public Result<Boolean> update(@PathVariable("id") String id, @RequestBody SensorTypeEntity entity) {
        entity.setId(id);
        return new Result<Boolean>().ok(sensorTypeService.updateById(entity));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除传感器类型")
    public Result<Boolean> delete(@PathVariable("id") String id) {
        return new Result<Boolean>().ok(sensorTypeService.removeById(id));
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取传感器类型详情")
    public Result<SensorTypeEntity> get(@PathVariable("id") String id) {
        return new Result<SensorTypeEntity>().ok(sensorTypeService.getById(id));
    }

    @GetMapping("/list")
    @Operation(summary = "获取传感器类型列表")
    public Result<List<SensorTypeEntity>> list() {
        return new Result<List<SensorTypeEntity>>().ok(sensorTypeService.list());
    }
}
