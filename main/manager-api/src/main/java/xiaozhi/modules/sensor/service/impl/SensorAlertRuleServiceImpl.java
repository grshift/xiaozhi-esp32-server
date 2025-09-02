package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.SensorAlertRuleDao;
import xiaozhi.modules.sensor.entity.SensorAlertRuleEntity;
import xiaozhi.modules.sensor.service.SensorAlertRuleService;

/**
 * 传感器告警规则服务实现
 */
@Service
public class SensorAlertRuleServiceImpl extends ServiceImpl<SensorAlertRuleDao, SensorAlertRuleEntity> implements SensorAlertRuleService {
    
}
