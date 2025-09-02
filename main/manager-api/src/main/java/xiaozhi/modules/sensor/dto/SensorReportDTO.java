package xiaozhi.modules.sensor.dto;

import java.util.Date;
import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 传感器数据上报DTO
 */
@Data
@Schema(description = "传感器数据上报")
public class SensorReportDTO {

    @Schema(description = "消息类型")
    private String type;

    @Schema(description = "设备MAC地址")
    private String macAddress;

    @Schema(description = "时间戳")
    private Date timestamp;

    @Schema(description = "传感器数据列表")
    private List<SensorItem> sensors;

    @Data
    @Schema(description = "传感器数据项")
    public static class SensorItem {
        @Schema(description = "传感器编码")
        private String sensorCode;
        
        @Schema(description = "数值")
        private Double value;
        
        @Schema(description = "单位")
        private String unit;
    }
}
