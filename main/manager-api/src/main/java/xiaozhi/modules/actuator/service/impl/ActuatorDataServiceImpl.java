package xiaozhi.modules.actuator.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import xiaozhi.modules.actuator.dao.ActuatorDataDao;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import xiaozhi.modules.actuator.service.ActuatorDataService;

/**
 * 执行器数据日志服务实现
 */
@Service
public class ActuatorDataServiceImpl extends ServiceImpl<ActuatorDataDao, ActuatorDataEntity> implements ActuatorDataService {}
