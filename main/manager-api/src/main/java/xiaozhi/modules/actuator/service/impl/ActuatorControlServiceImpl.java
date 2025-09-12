package xiaozhi.modules.actuator.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import org.springframework.data.redis.core.RedisTemplate;

import xiaozhi.common.exception.RenException;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.utils.ResultUtils;
import xiaozhi.modules.actuator.dto.ActuatorResponseDTO;
import xiaozhi.modules.actuator.dto.PumpControlDTO;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;
import xiaozhi.modules.actuator.service.ActuatorControlService;
import xiaozhi.modules.actuator.service.ActuatorDataService;
import xiaozhi.modules.actuator.service.DeviceActuatorService;

import java.util.Date;
import java.util.List;
import java.util.Objects;

/**
 * 执行器控制服务实现
 */
@Service
@Slf4j
public class ActuatorControlServiceImpl implements ActuatorControlService {

    @Autowired
    private DeviceActuatorService deviceActuatorService;

    @Autowired
    private ActuatorDataService actuatorDataService;

    @Autowired
    private RedisUtils redisUtils;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    // Redis缓存Key的前缀
    private static final String ACTUATOR_STATUS_CACHE_KEY = "actuator:status:";

    @Override
    @Transactional(rollbackFor = Exception.class)
    @SneakyThrows
    public xiaozhi.common.utils.Result<ActuatorResponseDTO> controlPump(PumpControlDTO request) {
        // 1. 查找设备和执行器配置
        DeviceActuatorEntity actuator = deviceActuatorService.getOne(
            new QueryWrapper<DeviceActuatorEntity>()
                .eq("device_id", request.getDeviceId())
                .eq("actuator_code", request.getActuatorCode())
        );

        if (actuator == null) {
            throw new RenException("指定的执行器不存在");
        }
        if (actuator.getIsEnabled() == 0) {
            throw new RenException("执行器已被禁用");
        }

        // 2. 验证命令参数 (此处可根据action类型做更复杂的校验)
        log.info("接收到水泵控制命令: deviceId={}, actuatorCode={}, action={}, params={}",
            request.getDeviceId(), request.getActuatorCode(), request.getAction(), request.getParameters());

        // 3. 记录操作日志
        ActuatorDataEntity dataLog = new ActuatorDataEntity();
        dataLog.setDeviceId(actuator.getDeviceId());
        dataLog.setActuatorId(actuator.getId());
        dataLog.setActuatorCode(actuator.getActuatorCode());
        dataLog.setCommand(request.getAction());
        if (request.getParameters() != null && !request.getParameters().isEmpty()) {
            dataLog.setCommandParams(objectMapper.writeValueAsString(request.getParameters()));
        }
        dataLog.setExecutedAt(new Date());
        actuatorDataService.save(dataLog);

        // 4. 执行控制逻辑 (核心)
        // **解耦点**: 这里不直接与硬件通信，而是将命令发送到消息队列(如MQTT, RabbitMQ)或Redis Pub/Sub
        // 由专门的设备网关服务监听并执行。这样API可以快速响应。
        sendCommandToDevice(actuator, request);

        // 5. 更新执行器最后状态
        actuator.setLastCommand(request.getAction());
        actuator.setLastCommandAt(new Date());
        actuator.setLastStatus("COMMAND_SENT"); // 设置一个中间状态，等待设备回报
        deviceActuatorService.updateById(actuator);

        // 6. 清除相关缓存，确保下次查询获取最新状态
        redisUtils.delete(ACTUATOR_STATUS_CACHE_KEY + actuator.getDeviceId());

        // 7. 返回响应
        ActuatorResponseDTO response = ActuatorResponseDTO.builder()
            .success(true)
            .message("命令已成功发送至设备")
            .operationId(dataLog.getId())
            .build();

        return ResultUtils.success(response);
    }

    /**
     * 发送命令到设备通信层
     * 通过Redis发布订阅机制将控制命令发送到Python WebSocket服务器
     */
    private void sendCommandToDevice(DeviceActuatorEntity actuator, PumpControlDTO request) {
        try {
            // 构造设备控制命令消息
            String channel = "device:control:" + actuator.getDeviceId();
            String message = objectMapper.writeValueAsString(new DeviceControlMessage(
                actuator.getDeviceId(),
                actuator.getActuatorCode(),
                request.getAction(),
                request.getParameters(),
                System.currentTimeMillis()
            ));

            // 通过Redis发布消息
            redisUtils.set("device_command:" + actuator.getId(), message, 300); // 5分钟过期

            // 发布到Redis频道，让Python服务器接收
            redisTemplate.convertAndSend("device_control_channel", message);

            log.info("控制命令已发布到Redis - 设备: {}, 执行器: {}, 命令: {}",
                actuator.getDeviceId(), actuator.getActuatorCode(), request.getAction());

        } catch (Exception e) {
            log.error("发送设备控制命令失败: {}", e.getMessage(), e);
            throw new RenException("设备通信失败，请稍后重试");
        }
    }

    /**
     * 设备控制消息内部类
     */
    private static class DeviceControlMessage {
        public String deviceId;
        public String actuatorCode;
        public String action;
        public Object parameters;
        public long timestamp;

        public DeviceControlMessage(String deviceId, String actuatorCode, String action, Object parameters, long timestamp) {
            this.deviceId = deviceId;
            this.actuatorCode = actuatorCode;
            this.action = action;
            this.parameters = parameters;
            this.timestamp = timestamp;
        }
    }

    @Override
    public xiaozhi.common.utils.Result<List<DeviceActuatorEntity>> getPumpStatus(String deviceId) {
        // 优先从缓存获取
        String cacheKey = ACTUATOR_STATUS_CACHE_KEY + deviceId;
        @SuppressWarnings("unchecked")
        List<DeviceActuatorEntity> actuators = (List<DeviceActuatorEntity>) redisUtils.get(cacheKey);

        if (actuators == null) {
            log.debug("缓存未命中，从数据库查询设备 {} 的执行器状态", deviceId);
            actuators = deviceActuatorService.list(
                new QueryWrapper<DeviceActuatorEntity>()
                    .eq("device_id", deviceId)
                    // 如果需要，可以进一步筛选 category 为 'pump'
            );
            // 设置缓存，例如1分钟过期
            redisUtils.set(cacheKey, actuators, 60);
        } else {
            log.debug("从缓存获取到设备 {} 的执行器状态", deviceId);
        }

        return ResultUtils.success(actuators);
    }
}
