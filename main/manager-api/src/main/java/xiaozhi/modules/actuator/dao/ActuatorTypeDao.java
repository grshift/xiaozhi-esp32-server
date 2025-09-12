package xiaozhi.modules.actuator.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import xiaozhi.modules.actuator.entity.ActuatorTypeEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 执行器类型DAO
 */
@Mapper
public interface ActuatorTypeDao extends BaseMapper<ActuatorTypeEntity> {}
