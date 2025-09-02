package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.SensorDataAggregateEntity;

/**
 * 传感器聚合数据DAO
 */
@Mapper
public interface SensorDataAggregateDao extends BaseMapper<SensorDataAggregateEntity> {
    
}
