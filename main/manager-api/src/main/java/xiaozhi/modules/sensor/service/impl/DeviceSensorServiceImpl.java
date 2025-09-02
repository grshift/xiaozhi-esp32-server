package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.DeviceSensorDao;
import xiaozhi.modules.sensor.entity.DeviceSensorEntity;
import xiaozhi.modules.sensor.service.DeviceSensorService;

/**
 * 设备传感器配置服务实现
 */
@Service
public class DeviceSensorServiceImpl extends ServiceImpl<DeviceSensorDao, DeviceSensorEntity> implements DeviceSensorService {
    
}
