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
 * 传感器告警记录实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_sensor_alert_log")
@Schema(description = "传感器告警记录")
public class SensorAlertLogEntity {

    @TableId(type = IdType.AUTO)
    @Schema(description = "告警记录ID")
    private Long id;

    @Schema(description = "规则ID")
    private String ruleId;

    @Schema(description = "设备ID")
    private String deviceId;

    @Schema(description = "传感器ID")
    private String sensorId;

    @Schema(description = "告警级别")
    private Integer alertLevel;

    @Schema(description = "告警消息")
    private String alertMessage;

    @Schema(description = "触发时的传感器值")
    private BigDecimal sensorValue;

    @Schema(description = "阈值配置")
    private String thresholdValue;

    @Schema(description = "是否已解决(0-未解决,1-已解决)")
    private Integer isResolved;

    @Schema(description = "解决时间")
    private Date resolvedAt;

    @Schema(description = "解决人")
    private Long resolvedBy;

    @Schema(description = "创建时间")
    private Date createdAt;
}
