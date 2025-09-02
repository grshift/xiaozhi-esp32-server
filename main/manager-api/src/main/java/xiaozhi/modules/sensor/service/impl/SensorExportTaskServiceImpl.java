package xiaozhi.modules.sensor.service.impl;

import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import xiaozhi.modules.sensor.dao.SensorExportTaskDao;
import xiaozhi.modules.sensor.entity.SensorExportTaskEntity;
import xiaozhi.modules.sensor.service.SensorExportTaskService;

/**
 * 传感器数据导出任务服务实现
 */
@Service
public class SensorExportTaskServiceImpl extends ServiceImpl<SensorExportTaskDao, SensorExportTaskEntity> implements SensorExportTaskService {
    
}
