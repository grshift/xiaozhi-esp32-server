package xiaozhi.modules.sensor.entity;

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
 * 传感器告警规则实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_sensor_alert_rule")
@Schema(description = "传感器告警规则")
public class SensorAlertRuleEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "规则ID")
    private String id;

    @Schema(description = "规则名称")
    private String ruleName;

    @Schema(description = "设备ID(null表示全局规则)")
    private String deviceId;

    @Schema(description = "传感器ID(null表示设备所有传感器)")
    private String sensorId;

    @Schema(description = "传感器类型ID(用于全局规则)")
    private String sensorTypeId;

    @Schema(description = "条件类型(threshold/range/change_rate)")
    private String conditionType;

    @Schema(description = "条件配置JSON")
    private String conditionConfig;

    @Schema(description = "告警级别(1-提示,2-警告,3-严重)")
    private Integer alertLevel;

    @Schema(description = "告警消息模板")
    private String alertMessage;

    @Schema(description = "动作类型(notification/voice/plugin)")
    private String actionType;

    @Schema(description = "动作配置JSON")
    private String actionConfig;

    @Schema(description = "冷却时间(分钟)")
    private Integer cooldownMinutes;

    @Schema(description = "是否启用(0-禁用,1-启用)")
    private Integer isEnabled;

    @Schema(description = "最后触发时间")
    private Date lastTriggeredAt;

    @Schema(description = "触发次数")
    private Integer triggerCount;

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
