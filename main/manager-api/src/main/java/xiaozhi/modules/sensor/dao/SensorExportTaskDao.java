package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.SensorExportTaskEntity;

/**
 * 传感器数据导出任务DAO
 */
@Mapper
public interface SensorExportTaskDao extends BaseMapper<SensorExportTaskEntity> {
    
}
