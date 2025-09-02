package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.SensorAlertLogDao;
import xiaozhi.modules.sensor.entity.SensorAlertLogEntity;
import xiaozhi.modules.sensor.service.SensorAlertLogService;

/**
 * 传感器告警记录服务实现
 */
@Service
public class SensorAlertLogServiceImpl extends ServiceImpl<SensorAlertLogDao, SensorAlertLogEntity> implements SensorAlertLogService {
    
}
