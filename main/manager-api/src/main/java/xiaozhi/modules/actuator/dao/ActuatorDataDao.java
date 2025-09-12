package xiaozhi.modules.actuator.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 执行器数据日志DAO
 */
@Mapper
public interface ActuatorDataDao extends BaseMapper<ActuatorDataEntity> {}
