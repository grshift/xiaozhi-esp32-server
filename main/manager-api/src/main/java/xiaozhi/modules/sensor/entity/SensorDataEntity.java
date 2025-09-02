package xiaozhi.modules.sensor.entity;

import java.math.BigDecimal;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 传感器数据记录实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_sensor_data")
@Schema(description = "传感器数据记录")
public class SensorDataEntity {

    @TableId(type = IdType.AUTO)
    @Schema(description = "数据记录ID")
    private Long id;

    @Schema(description = "设备ID")
    private String deviceId;

    @Schema(description = "传感器ID")
    private String sensorId;

    @Schema(description = "传感器编码")
    private String sensorCode;

    @Schema(description = "数据值")
    private BigDecimal value;

    @Schema(description = "原始值")
    private String rawValue;

    @Schema(description = "数据质量(0-差,1-正常,2-优)")
    private Integer quality;

    @Schema(description = "采集时间")
    private Date collectedAt;

    @Schema(description = "创建时间")
    private Date createdAt;
}
