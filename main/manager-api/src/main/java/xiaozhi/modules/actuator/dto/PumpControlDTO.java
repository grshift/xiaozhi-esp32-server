package xiaozhi.modules.actuator.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import java.util.Map;

/**
 * 水泵控制请求体
 */
@Data
@Schema(description = "水泵控制请求体")
public class PumpControlDTO {

    @NotBlank(message = "设备ID不能为空")
    @Schema(description = "目标设备ID", required = true, example = "device-uuid-123")
    private String deviceId;

    @NotBlank(message = "执行器编码不能为空")
    @Schema(description = "水泵的执行器编码", required = true, example = "pump_01")
    private String actuatorCode;

    @NotBlank(message = "执行命令不能为空")
    @Schema(description = "控制命令 (e.g., 'start', 'stop', 'set_flow')", required = true, example = "start")
    private String action;

    @Schema(description = "命令相关参数，如 'duration' (持续时间-秒), 'flowRate' (流速)", example = "{\"duration\": 300, \"flowRate\": 50.0}")
    private Map<String, Object> parameters;
}
