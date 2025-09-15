package xiaozhi.modules.actuator.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.actuator.dto.ActuatorResponseDTO;
import xiaozhi.modules.actuator.dto.PumpControlDTO;
import xiaozhi.modules.actuator.dto.PumpConfigDTO;
import xiaozhi.modules.actuator.dto.PumpConfigResponseDTO;
import xiaozhi.modules.actuator.dto.PumpHistoryQueryDTO;
import xiaozhi.modules.actuator.dto.PumpSelectDTO;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;

import java.util.List;

/**
 * 执行器控制服务接口
 */
public interface ActuatorControlService {

    /**
     * 控制水泵
     * @param request 控制请求
     * @return 响应结果
     */
    Result<ActuatorResponseDTO> controlPump(PumpControlDTO request);

    /**
     * 获取设备的水泵状态
     * @param deviceId 设备ID
     * @return 水泵状态列表
     */
    Result<List<DeviceActuatorEntity>> getPumpStatus(String deviceId);

    /**
     * 获取指定设备下的水泵列表(用于下拉框)
     * @param deviceId 设备ID
     * @return 水泵选择列表
     */
    Result<List<PumpSelectDTO>> getPumpListForSelect(String deviceId);

    /**
     * 获取支持的水泵命令类型
     * @return 命令类型列表
     */
    Result<List<String>> getSupportedCommandTypes();

    /**
     * 高级历史记录查询
     * @param queryDTO 查询条件
     * @return 分页历史记录
     */
    Result<Page<ActuatorDataEntity>> getAdvancedHistory(PumpHistoryQueryDTO queryDTO);

    /**
     * 导出历史记录
     * @param queryDTO 查询条件
     * @return CSV格式的字节数组
     */
    byte[] exportHistory(PumpHistoryQueryDTO queryDTO);

    // ========== 水泵配置管理接口 ==========

    /**
     * 添加水泵配置
     * @param configDTO 配置信息
     * @return 响应结果
     */
    Result<PumpConfigResponseDTO> addPumpConfig(PumpConfigDTO configDTO);

    /**
     * 更新水泵配置
     * @param configDTO 配置信息
     * @return 响应结果
     */
    Result<PumpConfigResponseDTO> updatePumpConfig(PumpConfigDTO configDTO);

    /**
     * 删除水泵配置
     * @param id 配置ID
     * @return 响应结果
     */
    Result<Void> deletePumpConfig(String id);

    /**
     * 获取水泵配置详情
     * @param id 配置ID
     * @return 配置详情
     */
    Result<PumpConfigResponseDTO> getPumpConfig(String id);

    /**
     * 更新水泵启用状态
     * @param id 配置ID
     * @param isEnabled 启用状态
     * @return 响应结果
     */
    Result<Void> updatePumpStatus(String id, Integer isEnabled);
}
