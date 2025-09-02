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
 * 传感器类型定义实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_sensor_type")
@Schema(description = "传感器类型定义")
public class SensorTypeEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "类型ID")
    private String id;

    @Schema(description = "类型编码")
    private String typeCode;

    @Schema(description = "类型名称")
    private String typeName;

    @Schema(description = "数据单位")
    private String unit;

    @Schema(description = "数据类型(number/boolean/string)")
    private String dataType;

    @Schema(description = "图标")
    private String icon;

    @Schema(description = "描述")
    private String description;

    @Schema(description = "数值范围JSON")
    private String valueRange;

    @Schema(description = "数据精度(小数位数)")
    private Integer precision;

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
