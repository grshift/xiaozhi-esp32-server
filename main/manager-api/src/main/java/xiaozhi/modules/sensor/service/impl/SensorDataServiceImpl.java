package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.SensorDataDao;
import xiaozhi.modules.sensor.entity.SensorDataEntity;
import xiaozhi.modules.sensor.service.SensorDataService;

/**
 * 传感器数据记录服务实现
 */
@Service
public class SensorDataServiceImpl extends ServiceImpl<SensorDataDao, SensorDataEntity> implements SensorDataService {
    
}
