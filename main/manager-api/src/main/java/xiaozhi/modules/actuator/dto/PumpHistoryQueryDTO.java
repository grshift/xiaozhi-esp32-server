package xiaozhi.modules.actuator.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.util.Date;

@Data
@Schema(description = "水泵历史记录高级查询条件")
public class PumpHistoryQueryDTO {

    @Schema(description = "设备ID", example = "device-uuid-123")
    private String deviceId;

    @Schema(description = "水泵执行器编码", example = "pump_01")
    private String actuatorCode;

    @Schema(description = "命令类型", example = "start")
    private String commandType;

    @Schema(description = "查询开始日期", example = "2025-09-12")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private Date startDate;

    @Schema(description = "查询结束日期", example = "2025-09-13")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private Date endDate;

    @Schema(description = "当前页码", defaultValue = "1")
    private Long current = 1L;

    @Schema(description = "每页记录数", defaultValue = "10")
    private Long size = 10L;
}
