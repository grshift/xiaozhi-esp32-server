package xiaozhi.modules.device.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "设备选择项DTO")
public class DeviceSelectDTO {

    @Schema(description = "设备ID")
    private String id;

    @Schema(description = "设备名称")
    private String name;

    @Schema(description = "是否在线")
    private Boolean isOnline;
}
