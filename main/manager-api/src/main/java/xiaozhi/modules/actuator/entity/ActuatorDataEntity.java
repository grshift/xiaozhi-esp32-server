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
 * 执行器数据日志实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_actuator_data")
@Schema(description = "执行器数据日志")
public class ActuatorDataEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "数据日志ID")
    private String id;

    @Schema(description = "设备ID")
    private String deviceId;

    @Schema(description = "执行器ID")
    private String actuatorId;

    @Schema(description = "执行器编码")
    private String actuatorCode;

    @Schema(description = "执行命令")
    private String command;

    @Schema(description = "命令参数JSON")
    private String commandParams;

    @Schema(description = "响应状态")
    private String responseStatus;

    @Schema(description = "响应消息")
    private String responseMessage;

    @Schema(description = "执行时间")
    private Date executedAt;

    @Schema(description = "执行耗时(毫秒)")
    private Integer executionDuration;

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
