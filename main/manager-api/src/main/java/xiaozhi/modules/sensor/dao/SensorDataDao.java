package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.SensorDataEntity;

/**
 * 传感器数据记录DAO
 */
@Mapper
public interface SensorDataDao extends BaseMapper<SensorDataEntity> {
    
}
