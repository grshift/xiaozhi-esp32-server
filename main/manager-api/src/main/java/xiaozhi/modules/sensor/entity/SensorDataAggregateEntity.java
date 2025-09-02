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
 * 传感器聚合数据实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_sensor_data_aggregate")
@Schema(description = "传感器聚合数据")
public class SensorDataAggregateEntity {

    @TableId(type = IdType.AUTO)
    @Schema(description = "聚合记录ID")
    private Long id;

    @Schema(description = "设备ID")
    private String deviceId;

    @Schema(description = "传感器ID")
    private String sensorId;

    @Schema(description = "聚合类型(hour/day/month)")
    private String aggregateType;

    @Schema(description = "聚合时间")
    private Date aggregateTime;

    @Schema(description = "平均值")
    private BigDecimal avgValue;

    @Schema(description = "最大值")
    private BigDecimal maxValue;

    @Schema(description = "最小值")
    private BigDecimal minValue;

    @Schema(description = "总和")
    private BigDecimal sumValue;

    @Schema(description = "数据点数")
    private Integer count;

    @Schema(description = "标准差")
    private BigDecimal stdDeviation;

    @Schema(description = "创建时间")
    private Date createdAt;
}
