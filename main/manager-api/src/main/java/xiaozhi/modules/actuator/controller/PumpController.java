package xiaozhi.modules.actuator.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import xiaozhi.common.utils.ResultUtils;
import xiaozhi.modules.actuator.dto.ActuatorResponseDTO;
import xiaozhi.modules.actuator.dto.PumpControlDTO;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;
import xiaozhi.modules.actuator.service.ActuatorControlService;
import xiaozhi.modules.actuator.service.ActuatorDataService;

import java.util.List;

/**
 * 水泵控制与查询控制器
 */
@RestController
@RequestMapping("/xiaozhi/pump")
@Tag(name = "水泵控制与查询")
public class PumpController {

    @Autowired
    private ActuatorControlService actuatorControlService;

    @Autowired
    private ActuatorDataService actuatorDataService;

    @PostMapping("/control")
    @Operation(summary = "发送水泵控制命令")
    public xiaozhi.common.utils.Result<ActuatorResponseDTO> control(@Validated @RequestBody PumpControlDTO request) {
        return actuatorControlService.controlPump(request);
    }

    @GetMapping("/status/{deviceId}")
    @Operation(summary = "获取指定设备下所有水泵的状态")
    public xiaozhi.common.utils.Result<List<DeviceActuatorEntity>> getStatus(@PathVariable String deviceId) {
        return actuatorControlService.getPumpStatus(deviceId);
    }

    @GetMapping("/history/{deviceId}")
    @Operation(summary = "获取指定设备下水泵的操作历史")
    public xiaozhi.common.utils.Result<Page<ActuatorDataEntity>> getHistory(
            @PathVariable String deviceId,
            @RequestParam(defaultValue = "1") long current,
            @RequestParam(defaultValue = "10") long size) {

        Page<ActuatorDataEntity> page = new Page<>(current, size);
        QueryWrapper<ActuatorDataEntity> queryWrapper = new QueryWrapper<ActuatorDataEntity>()
            .eq("device_id", deviceId)
            // .like("actuator_code", "pump") // 如果需要，可以模糊匹配编码
            .orderByDesc("executed_at");

        return ResultUtils.success(actuatorDataService.page(page, queryWrapper));
    }
}
