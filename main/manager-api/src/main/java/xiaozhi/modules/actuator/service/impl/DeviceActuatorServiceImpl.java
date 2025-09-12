package xiaozhi.modules.actuator.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import xiaozhi.modules.actuator.dao.DeviceActuatorDao;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;
import xiaozhi.modules.actuator.service.DeviceActuatorService;

/**
 * 设备执行器配置服务实现
 */
@Service
public class DeviceActuatorServiceImpl extends ServiceImpl<DeviceActuatorDao, DeviceActuatorEntity> implements DeviceActuatorService {}
