package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.SensorTypeDao;
import xiaozhi.modules.sensor.entity.SensorTypeEntity;
import xiaozhi.modules.sensor.service.SensorTypeService;

/**
 * 传感器类型服务实现
 */
@Service
public class SensorTypeServiceImpl extends ServiceImpl<SensorTypeDao, SensorTypeEntity> implements SensorTypeService {
    
}
