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
 * 执行器类型实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_actuator_type")
@Schema(description = "执行器类型")
public class ActuatorTypeEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "执行器类型ID")
    private String id;

    @Schema(description = "类型编码")
    private String typeCode;

    @Schema(description = "类型名称")
    private String typeName;

    @Schema(description = "分类")
    private String category;

    @Schema(description = "图标")
    private String icon;

    @Schema(description = "描述")
    private String description;

    @Schema(description = "默认配置JSON")
    private String defaultConfig;

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
