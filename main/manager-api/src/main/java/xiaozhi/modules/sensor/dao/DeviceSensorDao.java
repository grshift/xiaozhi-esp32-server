package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.DeviceSensorEntity;

/**
 * 设备传感器配置DAO
 */
@Mapper
public interface DeviceSensorDao extends BaseMapper<DeviceSensorEntity> {
    
}
