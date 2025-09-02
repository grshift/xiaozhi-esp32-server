package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.SensorAlertLogEntity;

/**
 * 传感器告警记录DAO
 */
@Mapper
public interface SensorAlertLogDao extends BaseMapper<SensorAlertLogEntity> {
    
}
