package xiaozhi.modules.sensor.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 传感器数据导出任务实体
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ai_sensor_export_task")
@Schema(description = "传感器数据导出任务")
public class SensorExportTaskEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "任务ID")
    private String id;

    @Schema(description = "用户ID")
    private Long userId;

    @Schema(description = "任务名称")
    private String taskName;

    @Schema(description = "设备ID列表JSON")
    private String deviceIds;

    @Schema(description = "传感器ID列表JSON")
    private String sensorIds;

    @Schema(description = "开始时间")
    private Date startTime;

    @Schema(description = "结束时间")
    private Date endTime;

    @Schema(description = "导出格式(csv/excel/json)")
    private String exportFormat;

    @Schema(description = "状态(pending/processing/completed/failed)")
    private String status;

    @Schema(description = "文件路径")
    private String filePath;

    @Schema(description = "文件大小(字节)")
    private Long fileSize;

    @Schema(description = "数据行数")
    private Integer rowCount;

    @Schema(description = "错误信息")
    private String errorMessage;

    @Schema(description = "创建时间")
    private Date createdAt;

    @Schema(description = "完成时间")
    private Date completedAt;
}
