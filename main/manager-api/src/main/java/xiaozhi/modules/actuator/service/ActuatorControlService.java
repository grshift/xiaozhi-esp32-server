package xiaozhi.modules.actuator.service;

import xiaozhi.common.utils.Result;
import xiaozhi.modules.actuator.dto.ActuatorResponseDTO;
import xiaozhi.modules.actuator.dto.PumpControlDTO;
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
}
