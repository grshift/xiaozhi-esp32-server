package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.SensorTypeEntity;

/**
 * 传感器类型DAO
 */
@Mapper
public interface SensorTypeDao extends BaseMapper<SensorTypeEntity> {
    
}
