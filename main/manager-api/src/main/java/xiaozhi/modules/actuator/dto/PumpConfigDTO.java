package xiaozhi.modules.actuator.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 水泵配置请求体
 */
@Data
@Schema(description = "水泵配置请求体")
public class PumpConfigDTO {

    @Schema(description = "执行器配置ID(更新时必填)")
    private String id;

    @NotBlank(message = "设备ID不能为空")
    @Schema(description = "设备ID", required = true, example = "device-uuid-123")
    private String deviceId;

    @NotBlank(message = "执行器编码不能为空")
    @Schema(description = "执行器编码(设备内唯一)", required = true, example = "pump_01")
    private String actuatorCode;

    @NotBlank(message = "执行器名称不能为空")
    @Schema(description = "执行器名称", required = true, example = "主水泵")
    private String actuatorName;

    @NotBlank(message = "GPIO引脚不能为空")
    @Schema(description = "GPIO引脚配置", required = true, example = "2")
    private String gpioPin;

    @Schema(description = "执行器配置参数JSON", example = "{\"maxFlowRate\": 100, \"minFlowRate\": 0}")
    private String configJson;

    @Schema(description = "校准数据JSON", example = "{\"calibrationFactor\": 1.0}")
    private String calibrationData;

    @NotNull(message = "启用状态不能为空")
    @Schema(description = "是否启用(0-禁用,1-启用)", required = true, example = "1")
    private Integer isEnabled;

    @Schema(description = "排序", example = "1")
    private Integer sort;
}
