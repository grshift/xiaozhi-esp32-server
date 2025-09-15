package xiaozhi.modules.actuator.service.impl;

import cn.hutool.core.text.csv.CsvUtil;
import cn.hutool.core.text.csv.CsvWriter;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import org.springframework.data.redis.core.RedisTemplate;

import xiaozhi.common.exception.RenException;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.utils.ResultUtils;
import xiaozhi.modules.actuator.dto.ActuatorResponseDTO;
import xiaozhi.modules.actuator.dto.PumpControlDTO;
import xiaozhi.modules.actuator.dto.PumpConfigDTO;
import xiaozhi.modules.actuator.dto.PumpConfigResponseDTO;
import xiaozhi.modules.actuator.dto.PumpHistoryQueryDTO;
import xiaozhi.modules.actuator.dto.PumpSelectDTO;
import xiaozhi.modules.actuator.entity.ActuatorDataEntity;
import xiaozhi.modules.actuator.entity.DeviceActuatorEntity;
import xiaozhi.modules.actuator.service.ActuatorControlService;
import xiaozhi.modules.actuator.service.ActuatorDataService;
import xiaozhi.modules.actuator.service.ActuatorTypeService;
import xiaozhi.modules.actuator.service.DeviceActuatorService;
import xiaozhi.modules.device.service.DeviceService;

import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

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

    @Autowired
    private DeviceService deviceService;

    @Autowired
    private ActuatorTypeService actuatorTypeService;

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

    @Override
    public xiaozhi.common.utils.Result<List<PumpSelectDTO>> getPumpListForSelect(String deviceId) {
        List<DeviceActuatorEntity> actuators = deviceActuatorService.list(
            new QueryWrapper<DeviceActuatorEntity>().eq("device_id", deviceId)
        );
        List<PumpSelectDTO> dtoList = actuators.stream().map(actuator -> {
            PumpSelectDTO dto = new PumpSelectDTO();
            dto.setId(actuator.getId());
            dto.setActuatorCode(actuator.getActuatorCode());
            dto.setActuatorName(actuator.getActuatorName());
            return dto;
        }).collect(Collectors.toList());
        return ResultUtils.success(dtoList);
    }

    @Override
    public xiaozhi.common.utils.Result<List<String>> getSupportedCommandTypes() {
        return ResultUtils.success(Arrays.asList("start", "stop"));
    }

    @Override
    public xiaozhi.common.utils.Result<Page<ActuatorDataEntity>> getAdvancedHistory(PumpHistoryQueryDTO queryDTO) {
        QueryWrapper<ActuatorDataEntity> wrapper = buildHistoryQueryWrapper(queryDTO);
        Page<ActuatorDataEntity> page = new Page<>(queryDTO.getCurrent(), queryDTO.getSize());
        return ResultUtils.success(actuatorDataService.page(page, wrapper));
    }

    @Override
    public byte[] exportHistory(PumpHistoryQueryDTO queryDTO) {
        QueryWrapper<ActuatorDataEntity> wrapper = buildHistoryQueryWrapper(queryDTO);
        List<ActuatorDataEntity> list = actuatorDataService.list(wrapper);

        StringWriter stringWriter = new StringWriter();
        CsvWriter writer = CsvUtil.getWriter(stringWriter);
        writer.write(new String[]{"记录ID", "设备ID", "水泵编码", "命令", "命令参数", "执行时间"});
        
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        for (ActuatorDataEntity entity : list) {
            writer.write(new String[]{
                entity.getId(), entity.getDeviceId(), entity.getActuatorCode(),
                entity.getCommand(), entity.getCommandParams(), sdf.format(entity.getExecutedAt())
            });
        }
        return stringWriter.toString().getBytes(StandardCharsets.UTF_8);
    }
    
    private QueryWrapper<ActuatorDataEntity> buildHistoryQueryWrapper(PumpHistoryQueryDTO dto) {
        QueryWrapper<ActuatorDataEntity> wrapper = new QueryWrapper<>();
        wrapper.eq(StringUtils.isNotBlank(dto.getDeviceId()), "device_id", dto.getDeviceId());
        wrapper.eq(StringUtils.isNotBlank(dto.getActuatorCode()), "actuator_code", dto.getActuatorCode());
        wrapper.eq(StringUtils.isNotBlank(dto.getCommandType()), "command", dto.getCommandType());
        wrapper.ge(dto.getStartDate() != null, "executed_at", dto.getStartDate());
        wrapper.le(dto.getEndDate() != null, "executed_at", dto.getEndDate());
        wrapper.orderByDesc("executed_at");
        return wrapper;
    }

    // ========== 水泵配置管理实现 ==========

    @Override
    @Transactional(rollbackFor = Exception.class)
    public xiaozhi.common.utils.Result<PumpConfigResponseDTO> addPumpConfig(PumpConfigDTO configDTO) {
        try {
            // 检查设备是否存在
            if (deviceService.selectById(configDTO.getDeviceId()) == null) {
                return ResultUtils.error("设备不存在");
            }

            // 检查执行器编码是否重复
            QueryWrapper<DeviceActuatorEntity> checkWrapper = new QueryWrapper<>();
            checkWrapper.eq("device_id", configDTO.getDeviceId())
                       .eq("actuator_code", configDTO.getActuatorCode());
            if (deviceActuatorService.count(checkWrapper) > 0) {
                return ResultUtils.error("该设备下已存在相同编码的执行器");
            }

            // 创建执行器配置实体
            DeviceActuatorEntity entity = new DeviceActuatorEntity();
            entity.setDeviceId(configDTO.getDeviceId());
            entity.setActuatorCode(configDTO.getActuatorCode());
            entity.setActuatorName(configDTO.getActuatorName());
            entity.setGpioPin(configDTO.getGpioPin());
            entity.setConfigJson(StringUtils.isNotBlank(configDTO.getConfigJson()) ? configDTO.getConfigJson() : "{}");
            entity.setCalibrationData(StringUtils.isNotBlank(configDTO.getCalibrationData()) ? configDTO.getCalibrationData() : null);
            entity.setIsEnabled(configDTO.getIsEnabled());
            entity.setSort(configDTO.getSort() != null ? configDTO.getSort() : 0);
            entity.setStatus(0); // 初始状态为离线
            entity.setActuatorTypeId(getPumpActuatorTypeId()); // 获取水泵类型ID

            // 保存到数据库
            deviceActuatorService.save(entity);

            // 清除相关缓存
            clearActuatorCache(configDTO.getDeviceId());

            // 返回响应
            return ResultUtils.success(convertToResponseDTO(entity));

        } catch (Exception e) {
            log.error("添加水泵配置失败", e);
            return ResultUtils.error("添加水泵配置失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public xiaozhi.common.utils.Result<PumpConfigResponseDTO> updatePumpConfig(PumpConfigDTO configDTO) {
        try {
            if (StringUtils.isBlank(configDTO.getId())) {
                return ResultUtils.error("配置ID不能为空");
            }

            // 检查配置是否存在
            DeviceActuatorEntity existingEntity = deviceActuatorService.getById(configDTO.getId());
            if (existingEntity == null) {
                return ResultUtils.error("水泵配置不存在");
            }

            // 检查执行器编码是否重复（排除自己）
            QueryWrapper<DeviceActuatorEntity> checkWrapper = new QueryWrapper<>();
            checkWrapper.eq("device_id", configDTO.getDeviceId())
                       .eq("actuator_code", configDTO.getActuatorCode())
                       .ne("id", configDTO.getId());
            if (deviceActuatorService.count(checkWrapper) > 0) {
                return ResultUtils.error("该设备下已存在相同编码的执行器");
            }

            // 更新实体
            existingEntity.setActuatorCode(configDTO.getActuatorCode());
            existingEntity.setActuatorName(configDTO.getActuatorName());
            existingEntity.setGpioPin(configDTO.getGpioPin());
            existingEntity.setConfigJson(StringUtils.isNotBlank(configDTO.getConfigJson()) ? configDTO.getConfigJson() : "{}");
            existingEntity.setCalibrationData(StringUtils.isNotBlank(configDTO.getCalibrationData()) ? configDTO.getCalibrationData() : null);
            existingEntity.setIsEnabled(configDTO.getIsEnabled());
            existingEntity.setSort(configDTO.getSort() != null ? configDTO.getSort() : 0);

            // 保存更新
            deviceActuatorService.updateById(existingEntity);

            // 清除相关缓存
            clearActuatorCache(configDTO.getDeviceId());

            // 返回响应
            return ResultUtils.success(convertToResponseDTO(existingEntity));

        } catch (Exception e) {
            log.error("更新水泵配置失败", e);
            return ResultUtils.error("更新水泵配置失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public xiaozhi.common.utils.Result<Void> deletePumpConfig(String id) {
        try {
            if (StringUtils.isBlank(id)) {
                return ResultUtils.error("配置ID不能为空");
            }

            // 检查配置是否存在
            DeviceActuatorEntity entity = deviceActuatorService.getById(id);
            if (entity == null) {
                return ResultUtils.error("水泵配置不存在");
            }

            // 删除配置
            deviceActuatorService.removeById(id);

            // 清除相关缓存
            clearActuatorCache(entity.getDeviceId());

            return ResultUtils.empty();

        } catch (Exception e) {
            log.error("删除水泵配置失败", e);
            return ResultUtils.error("删除水泵配置失败: " + e.getMessage());
        }
    }

    @Override
    public xiaozhi.common.utils.Result<PumpConfigResponseDTO> getPumpConfig(String id) {
        try {
            if (StringUtils.isBlank(id)) {
                return ResultUtils.error("配置ID不能为空");
            }

            DeviceActuatorEntity entity = deviceActuatorService.getById(id);
            if (entity == null) {
                return ResultUtils.error("水泵配置不存在");
            }

            return ResultUtils.success(convertToResponseDTO(entity));

        } catch (Exception e) {
            log.error("获取水泵配置失败", e);
            return ResultUtils.error("获取水泵配置失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public xiaozhi.common.utils.Result<Void> updatePumpStatus(String id, Integer isEnabled) {
        try {
            if (StringUtils.isBlank(id)) {
                return ResultUtils.error("配置ID不能为空");
            }

            if (isEnabled == null || (isEnabled != 0 && isEnabled != 1)) {
                return ResultUtils.error("启用状态参数无效");
            }

            // 检查配置是否存在
            DeviceActuatorEntity entity = deviceActuatorService.getById(id);
            if (entity == null) {
                return ResultUtils.error("水泵配置不存在");
            }

            // 更新状态
            entity.setIsEnabled(isEnabled);
            deviceActuatorService.updateById(entity);

            // 清除相关缓存
            clearActuatorCache(entity.getDeviceId());

            return ResultUtils.empty();

        } catch (Exception e) {
            log.error("更新水泵状态失败", e);
            return ResultUtils.error("更新水泵状态失败: " + e.getMessage());
        }
    }

    /**
     * 转换为响应DTO
     */
    private PumpConfigResponseDTO convertToResponseDTO(DeviceActuatorEntity entity) {
        PumpConfigResponseDTO dto = new PumpConfigResponseDTO();
        dto.setId(entity.getId());
        dto.setDeviceId(entity.getDeviceId());
        dto.setActuatorTypeId(entity.getActuatorTypeId());
        dto.setActuatorCode(entity.getActuatorCode());
        dto.setActuatorName(entity.getActuatorName());
        dto.setGpioPin(entity.getGpioPin());
        dto.setConfigJson(entity.getConfigJson());
        dto.setCalibrationData(entity.getCalibrationData());
        dto.setLastCommand(entity.getLastCommand());
        dto.setLastCommandAt(entity.getLastCommandAt());
        dto.setLastStatus(entity.getLastStatus());
        dto.setLastUpdatedAt(entity.getLastUpdatedAt());
        dto.setIsEnabled(entity.getIsEnabled());
        dto.setStatus(entity.getStatus());
        dto.setSort(entity.getSort());
        dto.setCreateDate(entity.getCreateDate());
        dto.setUpdateDate(entity.getUpdateDate());
        return dto;
    }

    /**
     * 清除执行器缓存
     */
    private void clearActuatorCache(String deviceId) {
        String cacheKey = ACTUATOR_STATUS_CACHE_KEY + deviceId;
        redisUtils.delete(cacheKey);
    }

    /**
     * 获取水泵执行器类型ID
     */
    private String getPumpActuatorTypeId() {
        try {
            // 首先尝试通过type_code查找
            QueryWrapper<xiaozhi.modules.actuator.entity.ActuatorTypeEntity> wrapper = new QueryWrapper<>();
            wrapper.eq("type_code", "pump");
            xiaozhi.modules.actuator.entity.ActuatorTypeEntity pumpType = actuatorTypeService.getOne(wrapper);
            
            if (pumpType != null) {
                return pumpType.getId();
            }
            
            // 如果没找到，尝试使用默认ID
            xiaozhi.modules.actuator.entity.ActuatorTypeEntity defaultType = actuatorTypeService.getById("actuator_type_pump");
            if (defaultType != null) {
                return defaultType.getId();
            }
            
            // 如果都没有找到，返回默认值
            log.warn("未找到水泵执行器类型，使用默认值");
            return "actuator_type_pump";
            
        } catch (Exception e) {
            log.error("获取水泵执行器类型ID失败", e);
            return "actuator_type_pump";
        }
    }
}
