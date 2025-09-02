package xiaozhi.modules.sensor.entity;

import java.math.BigDecimal;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 设备传感器配置实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_device_sensor")
@Schema(description = "设备传感器配置")
public class DeviceSensorEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "传感器配置ID")
    private String id;

    @Schema(description = "设备ID")
    private String deviceId;

    @Schema(description = "传感器类型ID")
    private String sensorTypeId;

    @Schema(description = "传感器编码(设备内唯一)")
    private String sensorCode;

    @Schema(description = "传感器名称")
    private String sensorName;

    @Schema(description = "GPIO引脚配置")
    private String gpioPin;

    @Schema(description = "传感器配置参数JSON")
    private String configJson;

    @Schema(description = "校准数据JSON")
    private String calibrationData;

    @Schema(description = "是否启用(0-禁用,1-启用)")
    private Integer isEnabled;

    @Schema(description = "传感器位置描述")
    private String location;

    @Schema(description = "最新数值")
    private BigDecimal lastValue;

    @Schema(description = "最新更新时间")
    private Date lastUpdatedAt;

    @Schema(description = "状态(0-离线,1-正常,2-异常)")
    private Integer status;

    @Schema(description = "排序")
    private Integer sort;

    @Schema(description = "创建者")
    @TableField(fill = FieldFill.INSERT)
    private Long creator;

    @Schema(description = "创建时间")
    @TableField(fill = FieldFill.INSERT)
    private Date createDate;

    @Schema(description = "更新者")
    @TableField(fill = FieldFill.UPDATE)
    private Long updater;

    @Schema(description = "更新时间")
    @TableField(fill = FieldFill.UPDATE)
    private Date updateDate;
}
