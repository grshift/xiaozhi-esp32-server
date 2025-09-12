package xiaozhi.modules.actuator.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import xiaozhi.modules.actuator.dao.ActuatorTypeDao;
import xiaozhi.modules.actuator.entity.ActuatorTypeEntity;
import xiaozhi.modules.actuator.service.ActuatorTypeService;

/**
 * 执行器类型服务实现
 */
@Service
public class ActuatorTypeServiceImpl extends ServiceImpl<ActuatorTypeDao, ActuatorTypeEntity> implements ActuatorTypeService {}
