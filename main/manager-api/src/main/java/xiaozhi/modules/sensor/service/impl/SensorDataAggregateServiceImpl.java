package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.SensorDataAggregateDao;
import xiaozhi.modules.sensor.entity.SensorDataAggregateEntity;
import xiaozhi.modules.sensor.service.SensorDataAggregateService;

/**
 * 传感器聚合数据服务实现
 */
@Service
public class SensorDataAggregateServiceImpl extends ServiceImpl<SensorDataAggregateDao, SensorDataAggregateEntity> implements SensorDataAggregateService {
    
}
