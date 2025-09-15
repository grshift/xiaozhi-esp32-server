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
import xiaozhi.modules.actuator.dto.PumpConfigDTO;
import xiaozhi.modules.actuator.dto.PumpConfigResponseDTO;
import xiaozhi.modules.actuator.dto.PumpHistoryQueryDTO;
import xiaozhi.modules.actuator.dto.PumpSelectDTO;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;
import xiaozhi.modules.actuator.service.ActuatorControlService;
import xiaozhi.modules.actuator.service.ActuatorDataService;

import org.springframework.http.ResponseEntity;

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

    // ========== 新增接口 ==========

    @GetMapping("/list/{deviceId}")
    @Operation(summary = "获取指定设备下的水泵列表(用于下拉框)")
    public xiaozhi.common.utils.Result<List<PumpSelectDTO>> getPumpList(@PathVariable String deviceId) {
        return actuatorControlService.getPumpListForSelect(deviceId);
    }

    @GetMapping("/command-types")
    @Operation(summary = "获取支持的水泵命令类型")
    public xiaozhi.common.utils.Result<List<String>> getSupportedCommandTypes() {
        return actuatorControlService.getSupportedCommandTypes();
    }

    @GetMapping("/history/advanced")
    @Operation(summary = "高级水泵历史记录分页查询")
    public xiaozhi.common.utils.Result<Page<ActuatorDataEntity>> getAdvancedHistory(@ModelAttribute PumpHistoryQueryDTO queryDTO) {
        return actuatorControlService.getAdvancedHistory(queryDTO);
    }

    @GetMapping("/history/export")
    @Operation(summary = "导出水泵历史记录(CSV格式)")
    public ResponseEntity<byte[]> exportHistory(@ModelAttribute PumpHistoryQueryDTO queryDTO) {
        byte[] data = actuatorControlService.exportHistory(queryDTO);
        
        // 设置HTTP头，提示浏览器下载文件
        return ResponseEntity.ok()
                .header("Content-Disposition", "attachment; filename=\"pump_history.csv\"")
                .header("Content-Type", "text/csv; charset=utf-8")
                .body(data);
    }

    // ========== 水泵配置管理接口 ==========

    @PostMapping("/config")
    @Operation(summary = "添加水泵配置")
    public xiaozhi.common.utils.Result<PumpConfigResponseDTO> addPumpConfig(@Validated @RequestBody PumpConfigDTO configDTO) {
        return actuatorControlService.addPumpConfig(configDTO);
    }

    @PutMapping("/config")
    @Operation(summary = "更新水泵配置")
    public xiaozhi.common.utils.Result<PumpConfigResponseDTO> updatePumpConfig(@Validated @RequestBody PumpConfigDTO configDTO) {
        return actuatorControlService.updatePumpConfig(configDTO);
    }

    @DeleteMapping("/config/{id}")
    @Operation(summary = "删除水泵配置")
    public xiaozhi.common.utils.Result<Void> deletePumpConfig(@PathVariable String id) {
        return actuatorControlService.deletePumpConfig(id);
    }

    @GetMapping("/config/{id}")
    @Operation(summary = "获取水泵配置详情")
    public xiaozhi.common.utils.Result<PumpConfigResponseDTO> getPumpConfig(@PathVariable String id) {
        return actuatorControlService.getPumpConfig(id);
    }

    @PutMapping("/config/{id}/status")
    @Operation(summary = "更新水泵启用状态")
    public xiaozhi.common.utils.Result<Void> updatePumpStatus(
            @PathVariable String id,
            @RequestParam Integer isEnabled) {
        return actuatorControlService.updatePumpStatus(id, isEnabled);
    }
}
