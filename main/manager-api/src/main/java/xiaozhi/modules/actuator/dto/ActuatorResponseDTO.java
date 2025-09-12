package xiaozhi.modules.actuator.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 执行器命令响应
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "执行器命令响应")
public class ActuatorResponseDTO {

    @Schema(description = "命令是否成功下发", example = "true")
    private boolean success;

    @Schema(description = "响应消息", example = "命令已成功发送至设备")
    private String message;

    @Schema(description = "本次操作记录的ID", example = "data-log-uuid-456")
    private String operationId;
}
