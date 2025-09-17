import { getServiceUrl } from '../api';
import RequestService from '../httpRequest';

export default {
    // ========== 水泵控制相关API ==========

    // 发送水泵控制命令
    sendPumpCommand(params, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/control`)
            .method('POST')
            .data(params)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('发送水泵控制命令失败:', err);
                RequestService.reAjaxFun(() => {
                    this.sendPumpCommand(params, callback);
                });
            }).send();
    },

    // 获取指定设备下所有水泵的状态
    getPumpStatus(deviceId, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/status/${deviceId}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取水泵状态失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getPumpStatus(deviceId, callback);
                });
            }).send();
    },

    // 获取水泵操作历史
    getPumpHistory(params, callback) {
        const { deviceId, current = 1, size = 10 } = params;
        const queryParams = `current=${current}&size=${size}`;

        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/history/${deviceId}?${queryParams}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取水泵历史失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getPumpHistory(params, callback);
                });
            }).send();
    },

    // ========== 水泵配置管理API ==========

    // 添加水泵配置
    addPumpConfig(params, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/config`)
            .method('POST')
            .data(params)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('添加水泵配置失败:', err);
                RequestService.reAjaxFun(() => {
                    this.addPumpConfig(params, callback);
                });
            }).send();
    },

    // 更新水泵配置
    updatePumpConfig(params, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/config`)
            .method('PUT')
            .data(params)
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('更新水泵配置失败:', err);
                RequestService.reAjaxFun(() => {
                    this.updatePumpConfig(params, callback);
                });
            }).send();
    },

    // 删除水泵配置
    deletePumpConfig(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/config/${id}`)
            .method('DELETE')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('删除水泵配置失败:', err);
                RequestService.reAjaxFun(() => {
                    this.deletePumpConfig(id, callback);
                });
            }).send();
    },

    // 获取水泵配置详情
    getPumpConfig(id, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/config/${id}`)
            .method('GET')
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('获取水泵配置失败:', err);
                RequestService.reAjaxFun(() => {
                    this.getPumpConfig(id, callback);
                });
            }).send();
    },

    // 更新水泵启用状态
    updatePumpStatus(id, isEnabled, callback) {
        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/config/${id}/status`)
            .method('PUT')
            .data({ isEnabled })
            .success((res) => {
                RequestService.clearRequestTime();
                callback(res);
            })
            .networkFail((err) => {
                console.error('更新水泵状态失败:', err);
                RequestService.reAjaxFun(() => {
                    this.updatePumpStatus(id, isEnabled, callback);
                });
            }).send();
    },

    // 导出水泵历史记录
    exportPumpHistory(params, callback) {
        // 构建查询参数
        const queryParams = new URLSearchParams();
        if (params.deviceId) queryParams.append('deviceId', params.deviceId);
        if (params.actuatorCode) queryParams.append('actuatorCode', params.actuatorCode);
        if (params.commandType) queryParams.append('commandType', params.commandType);
        if (params.startDate) queryParams.append('startDate', params.startDate);
        if (params.endDate) queryParams.append('endDate', params.endDate);

        RequestService.sendRequest()
            .url(`${getServiceUrl()}/xiaozhi/pump/history/export?${queryParams.toString()}`)
            .method('GET')
            .type('blob') // 重要：设置响应类型为blob以处理文件下载
            .success((res) => {
                RequestService.clearRequestTime();
                console.log('导出API响应:', res);
                callback(res);
            })
            .networkFail((err) => {
                console.error('导出水泵历史记录失败:', err);
                RequestService.reAjaxFun(() => {
                    this.exportPumpHistory(params, callback);
                });
            }).send();
    }
}

