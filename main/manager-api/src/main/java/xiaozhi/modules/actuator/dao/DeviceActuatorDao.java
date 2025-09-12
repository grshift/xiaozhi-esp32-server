package xiaozhi.modules.actuator.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 设备执行器配置DAO
 */
@Mapper
public interface DeviceActuatorDao extends BaseMapper<DeviceActuatorEntity> {}
