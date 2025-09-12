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
    }
}

