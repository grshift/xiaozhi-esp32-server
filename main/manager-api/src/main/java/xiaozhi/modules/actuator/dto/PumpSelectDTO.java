package xiaozhi.modules.actuator.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "水泵选择项DTO")
public class PumpSelectDTO {

    @Schema(description = "执行器ID")
    private String id;

    @Schema(description = "执行器编码 (用于查询)")
    private String actuatorCode;

    @Schema(description = "执行器名称 (用于显示)")
    private String actuatorName;
}
