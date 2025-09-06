import { getServiceUrl } from '../api';
import RequestService from '../httpRequest';

export default {
    // ========== 传感器类型管理 ==========
    
    // 创建传感器类型
    createSensorType(sensorType, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/type`)
            .method('POST')
            .data(sensorType)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('创建传感器类型失败:', err);
                RequestService.reAjaxFun(() => {
                    this.createSensorType(sensorType, callback);
                });
            }).send();
    },

    // 更新传感器类型
    updateSensorType(id, sensorType, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/type/${id}`)
            .method('PUT')
            .data(sensorType)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('更新传感器类型失败:', err);
                RequestService.reAjaxFun(() => {
                    this.updateSensorType(id, sensorType, callback);
                });
            }).send();
    },

    // 删除传感器类型
    deleteSensorType(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/type/${id}`)
            .method('DELETE')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('删除传感器类型失败:', err);
                RequestService.reAjaxFun(() => {
                    this.deleteSensorType(id, callback);
                });
            }).send();
    },

    // 获取传感器类型详情
    getSensorType(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/type/${id}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取传感器类型详情失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getSensorType(id, callback);
                });
            }).send();
    },

    // 获取传感器类型列表
    getSensorTypeList(callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/type/list`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取传感器类型列表失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getSensorTypeList(callback);
                });
            }).send();
    },

    // ========== 设备传感器配置管理 ==========
    
    // 配置设备传感器
    createDeviceSensor(deviceSensor, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/device`)
            .method('POST')
            .data(deviceSensor)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('配置设备传感器失败:', err);
                RequestService.reAjaxFun(() => {
                    this.createDeviceSensor(deviceSensor, callback);
                });
            }).send();
    },

    // 更新传感器配置
    updateDeviceSensor(id, deviceSensor, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/device/${id}`)
            .method('PUT')
            .data(deviceSensor)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('更新传感器配置失败:', err);
                RequestService.reAjaxFun(() => {
                    this.updateDeviceSensor(id, deviceSensor, callback);
                });
            }).send();
    },

    // 删除传感器配置
    deleteDeviceSensor(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/device/${id}`)
            .method('DELETE')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('删除传感器配置失败:', err);
                RequestService.reAjaxFun(() => {
                    this.deleteDeviceSensor(id, callback);
                });
            }).send();
    },

    // 获取设备的传感器配置列表
    getDeviceSensorList(deviceId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/device/device/${deviceId}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取设备传感器配置列表失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getDeviceSensorList(deviceId, callback);
                });
            }).send();
    },

    // ========== 传感器数据查询 ==========
    
    // 实时数据查询
    getRealtimeData(deviceId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/data/realtime?deviceId=${deviceId}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取实时数据失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getRealtimeData(deviceId, callback);
                });
            }).send();
    },

    // 历史数据查询
    getHistoryData(params, callback) {
        const { deviceId, sensorId, start, end } = params;
        const queryParams = `deviceId=${deviceId}&sensorId=${sensorId}&start=${start}&end=${end}`;
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/data/history?${queryParams}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取历史数据失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getHistoryData(params, callback);
                });
            }).send();
    },

    // 聚合数据查询
    getAggregateData(params, callback) {
        const { deviceId, sensorId, type, start, end } = params;
        const queryParams = `deviceId=${deviceId}&sensorId=${sensorId}&type=${type}&start=${start}&end=${end}`;
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/data/aggregate?${queryParams}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取聚合数据失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getAggregateData(params, callback);
                });
            }).send();
    },

    // ========== 传感器告警管理 ==========
    
    // 创建告警规则
    createAlertRule(alertRule, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/alert/rule`)
            .method('POST')
            .data(alertRule)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('创建告警规则失败:', err);
                RequestService.reAjaxFun(() => {
                    this.createAlertRule(alertRule, callback);
                });
            }).send();
    },

    // 更新告警规则
    updateAlertRule(id, alertRule, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/alert/rule/${id}`)
            .method('PUT')
            .data(alertRule)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('更新告警规则失败:', err);
                RequestService.reAjaxFun(() => {
                    this.updateAlertRule(id, alertRule, callback);
                });
            }).send();
    },

    // 删除告警规则
    deleteAlertRule(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/alert/rule/${id}`)
            .method('DELETE')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('删除告警规则失败:', err);
                RequestService.reAjaxFun(() => {
                    this.deleteAlertRule(id, callback);
                });
            }).send();
    },

    // 获取告警规则列表
    getAlertRuleList(deviceId, callback) {
        const url = deviceId 
            ? `${getServiceUrl()}/xiaozhi/sensor/alert/rule/list?deviceId=${deviceId}`
            : `${getServiceUrl()}/xiaozhi/sensor/alert/rule/list`;
        
        RequestService.sendRequest()
            .url(url)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取告警规则列表失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getAlertRuleList(deviceId, callback);
                });
            }).send();
    },

    // 查询告警记录
    getAlertLogList(params, callback) {
        const { deviceId, isResolved } = params || {};
        let queryParams = [];
        if (deviceId) queryParams.push(`deviceId=${deviceId}`);
        if (isResolved !== undefined) queryParams.push(`isResolved=${isResolved}`);
        
        const url = queryParams.length > 0 
            ? `${getServiceUrl()}/xiaozhi/sensor/alert/log?${queryParams.join('&')}`
            : `${getServiceUrl()}/xiaozhi/sensor/alert/log`;
        
        RequestService.sendRequest()
            .url(url)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取告警记录失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getAlertLogList(params, callback);
                });
            }).send();
    },

    // 解决告警
    resolveAlert(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/sensor/alert/resolve/${id}`)
            .method('PUT')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('解决告警失败:', err);
                RequestService.reAjaxFun(() => {
                    this.resolveAlert(id, callback);
                });
            }).send();
    }
}
