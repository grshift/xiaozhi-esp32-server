package xiaozhi.modules.actuator.entity;

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
 * 设备执行器配置实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_device_actuator")
@Schema(description = "设备执行器配置")
public class DeviceActuatorEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "执行器配置ID")
    private String id;

    @Schema(description = "设备ID")
    private String deviceId;

    @Schema(description = "执行器类型ID")
    private String actuatorTypeId;

    @Schema(description = "执行器编码(设备内唯一)")
    private String actuatorCode;

    @Schema(description = "执行器名称")
    private String actuatorName;

    @Schema(description = "GPIO引脚配置")
    private String gpioPin;

    @Schema(description = "执行器配置参数JSON")
    private String configJson;

    @Schema(description = "校准数据JSON")
    private String calibrationData;

    @Schema(description = "最后执行的命令")
    private String lastCommand;

    @Schema(description = "最后命令执行时间")
    private Date lastCommandAt;

    @Schema(description = "最后状态")
    private String lastStatus;

    @Schema(description = "最后更新时间")
    private Date lastUpdatedAt;

    @Schema(description = "是否启用(0-禁用,1-启用)")
    private Integer isEnabled;

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
