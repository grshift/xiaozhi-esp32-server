package xiaozhi.modules.sensor.dao;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import xiaozhi.modules.sensor.entity.SensorAlertRuleEntity;

/**
 * 传感器告警规则DAO
 */
@Mapper
public interface SensorAlertRuleDao extends BaseMapper<SensorAlertRuleEntity> {
    
}
