import Api from '@/apis/api';

const pumpModule = {
    namespaced: true,
    state: {
        // 使用对象存储设备的水泵状态，key为deviceId
        pumpStatuses: {},
        // 使用数组存储正在监控的设备ID
        monitoringDeviceIds: [],
        // 定时器实例管理
        _monitorIntervals: {}
    },

    mutations: {
        // 更新设备的水泵状态
        SET_PUMP_STATUS(state, { deviceId, statusList }) {
            this._vm.$set(state.pumpStatuses, deviceId, statusList);
        },

        // 添加监控设备
        ADD_MONITORING_DEVICE(state, deviceId) {
            if (!state.monitoringDeviceIds.includes(deviceId)) {
                state.monitoringDeviceIds.push(deviceId);
            }
        },

        // 移除监控设备
        REMOVE_MONITORING_DEVICE(state, deviceId) {
            const index = state.monitoringDeviceIds.indexOf(deviceId);
            if (index > -1) {
                state.monitoringDeviceIds.splice(index, 1);
            }
        },

        // 设置定时器
        SET_MONITOR_INTERVAL(state, { deviceId, intervalId }) {
            state._monitorIntervals[deviceId] = intervalId;
        },

        // 清除定时器
        CLEAR_MONITOR_INTERVAL(state, deviceId) {
            if (state._monitorIntervals[deviceId]) {
                clearInterval(state._monitorIntervals[deviceId]);
                delete state._monitorIntervals[deviceId];
            }
        }
    },

    actions: {
        // 获取并更新设备的水泵状态
        async fetchPumpStatus({ commit }, deviceId) {
            return new Promise((resolve, reject) => {
                Api.pump.getPumpStatus(deviceId, ({ data }) => {
                    if (data.code === 0) {
                        commit('SET_PUMP_STATUS', { deviceId, statusList: data.data });
                        resolve(data.data);
                    } else {
                        reject(data.msg || '获取水泵状态失败');
                    }
                });
            });
        },

        // 发送控制命令
        async sendCommand({ dispatch }, commandPayload) {
            return new Promise((resolve, reject) => {
                Api.pump.sendPumpCommand(commandPayload, ({ data }) => {
                    if (data.code === 0) {
                        // 命令发送成功后，刷新状态
                        dispatch('fetchPumpStatus', commandPayload.deviceId);
                        resolve(data);
                    } else {
                        reject(data.msg || '发送命令失败');
                    }
                });
            });
        },

        // 开始监控设备状态
        startMonitoring({ commit, dispatch, state }, { deviceId, interval = 10000 }) {
            if (state._monitorIntervals[deviceId]) {
                return; // 已经在监控中
            }

            // 立即执行一次
            dispatch('fetchPumpStatus', deviceId);

            const intervalId = setInterval(() => {
                dispatch('fetchPumpStatus', deviceId);
            }, interval);

            commit('SET_MONITOR_INTERVAL', { deviceId, intervalId });
            commit('ADD_MONITORING_DEVICE', deviceId);
        },

        // 停止监控设备状态
        stopMonitoring({ commit, state }, deviceId) {
            commit('CLEAR_MONITOR_INTERVAL', deviceId);
            commit('REMOVE_MONITORING_DEVICE', deviceId);
        },

        // 获取水泵历史记录
        async fetchPumpHistory({ commit }, params) {
            return new Promise((resolve, reject) => {
                Api.pump.getPumpHistory(params, ({ data }) => {
                    if (data.code === 0) {
                        resolve(data.data);
                    } else {
                        reject(data.msg || '获取历史记录失败');
                    }
                });
            });
        }
    },

    getters: {
        // 获取特定设备的水泵状态列表
        getStatusesByDevice: (state) => (deviceId) => {
            return state.pumpStatuses[deviceId] || [];
        },

        // 检查设备是否正在被监控
        isMonitoring: (state) => (deviceId) => {
            return state.monitoringDeviceIds.includes(deviceId);
        },

        // 获取所有正在监控的设备
        monitoringDevices: (state) => {
            return state.monitoringDeviceIds;
        }
    }
};

export default pumpModule;
