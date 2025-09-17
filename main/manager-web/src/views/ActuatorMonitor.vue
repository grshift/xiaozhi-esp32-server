<template>
  <div class="app-container">
    <div class="operation-bar">
      <h2 class="page-title">水泵监控</h2>
      <div class="right-operations">
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          inactive-text="手动刷新"
          @change="handleAutoRefreshChange"
        ></el-switch>
        <el-button type="primary" @click="refreshAllStatus" icon="el-icon-refresh">
          刷新状态
        </el-button>
      </div>
    </div>

    <div class="main-wrapper">
      <div class="content-panel">
        <div class="content-area">
          <el-card>
            <div slot="header">设备选择</div>
            <el-select
              v-model="selectedDeviceId"
              placeholder="请选择设备"
              @change="handleDeviceChange"
              filterable
              clearable
              style="width: 300px;"
              :loading="deviceLoading"
              :disabled="deviceList.length === 0"
            >
              <el-option
                v-for="device in deviceList"
                :key="device.id"
                :label="device.alias || device.macAddress"
                :value="device.id"
              >
              </el-option>
            </el-select>
            <div v-if="deviceList.length === 0 && !deviceLoading" class="empty-tip">
              <el-alert
                title="暂无设备"
                description="您还没有绑定任何设备，请先激活设备后再监控水泵"
                type="info"
                :closable="false"
                show-icon>
              </el-alert>
            </div>
          </el-card>

          <el-divider></el-divider>

          <div v-if="selectedDeviceId" v-loading="monitorLoading">
            <div class="monitor-grid">
              <div v-for="pump in pumps" :key="pump.actuatorCode" class="monitor-card">
                <el-card class="pump-card" :class="getStatusClass(pump.status)">
                  <div slot="header" class="card-header">
                    <span class="pump-name">{{ pump.actuatorName }}</span>
                    <el-tag :type="getStatusType(pump.status)" size="mini">
                      {{ getStatusText(pump.status) }}
                    </el-tag>
                  </div>

                  <div class="pump-info">
                    <div class="info-row">
                      <label>编码:</label>
                      <span>{{ pump.actuatorCode }}</span>
                    </div>
                    <div class="info-row">
                      <label>GPIO:</label>
                      <span>{{ pump.gpioPin }}</span>
                    </div>
                    <div class="info-row">
                      <label>最后命令:</label>
                      <span>{{ pump.lastCommand || '无' }}</span>
                    </div>
                    <div class="info-row">
                      <label>执行时间:</label>
                      <span>{{ formatDate(pump.lastCommandAt) }}</span>
                    </div>
                    <div class="info-row">
                      <label>最后状态:</label>
                      <span>{{ pump.lastStatus || '未知' }}</span>
                    </div>
                    <div class="info-row">
                      <label>最后更新:</label>
                      <span>{{ formatDate(pump.lastUpdatedAt) }}</span>
                    </div>
                  </div>

                  <div class="card-actions">
                    <el-button
                      size="mini"
                      type="primary"
                      @click="quickControl(pump, 'start')"
                      :disabled="!canControl(pump)"
                      icon="el-icon-video-play"
                    >
                      启动
                    </el-button>
                    <el-button
                      size="mini"
                      type="danger"
                      @click="quickControl(pump, 'stop')"
                      :disabled="!canControl(pump)"
                      icon="el-icon-video-pause"
                    >
                      停止
                    </el-button>
                    <el-button
                      size="mini"
                      @click="showDetail(pump)"
                      icon="el-icon-info"
                    >
                      详情
                    </el-button>
                  </div>
                </el-card>
              </div>
            </div>

            <el-empty v-if="pumps.length === 0" description="该设备下没有水泵"></el-empty>
          </div>

          <el-empty v-else description="请先选择一个设备"></el-empty>
        </div>
      </div>
    </div>

    <!-- 水泵详情对话框 -->
    <el-dialog
      title="水泵详情"
      :visible.sync="detailDialogVisible"
      width="700px"
    >
      <div v-if="selectedPump">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="水泵ID">
            {{ selectedPump.id }}
          </el-descriptions-item>
          <el-descriptions-item label="设备ID">
            {{ selectedPump.deviceId }}
          </el-descriptions-item>
          <el-descriptions-item label="水泵编码">
            {{ selectedPump.actuatorCode }}
          </el-descriptions-item>
          <el-descriptions-item label="水泵名称">
            {{ selectedPump.actuatorName }}
          </el-descriptions-item>
          <el-descriptions-item label="GPIO引脚">
            {{ selectedPump.gpioPin }}
          </el-descriptions-item>
          <el-descriptions-item label="启用状态">
            <el-tag :type="selectedPump.isEnabled === 1 ? 'success' : 'info'">
              {{ selectedPump.isEnabled === 1 ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="连接状态">
            <el-tag :type="getStatusType(selectedPump.status)">
              {{ getStatusText(selectedPump.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最后命令" :span="2">
            {{ selectedPump.lastCommand || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="最后状态" :span="2">
            {{ selectedPump.lastStatus || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="最后更新时间" :span="2">
            {{ formatDate(selectedPump.lastUpdatedAt) }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedPump.configJson" class="config-section">
          <h4>配置信息:</h4>
          <el-card>
            <pre>{{ formatJson(selectedPump.configJson) }}</pre>
          </el-card>
        </div>

        <div v-if="selectedPump.calibrationData" class="config-section">
          <h4>校准数据:</h4>
          <el-card>
            <pre>{{ selectedPump.calibrationData }}</pre>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import Api from '@/apis/api';

export default {
  name: 'PumpMonitor',
  data() {
    return {
      deviceList: [],
      selectedDeviceId: null,
      pumps: [],
      deviceLoading: false,
      monitorLoading: false,
      autoRefresh: true,
      refreshInterval: null,
      detailDialogVisible: false,
      selectedPump: null
    };
  },
  computed: {
    ...mapGetters('pump', ['isMonitoring'])
  },
  methods: {
    ...mapActions('pump', ['startMonitoring', 'stopMonitoring', 'fetchPumpStatus']),

    async getDeviceList() {
      this.deviceLoading = true;
      try {
        await new Promise((resolve) => {
          Api.device.getDeviceList(({ data }) => {
            if (data.code === 0) {
              this.deviceList = data.data || [];
              if (this.deviceList.length === 0) {
                this.$message.info('您还没有绑定任何设备，请先激活设备');
              }
            } else {
              this.$message.error(data.msg || '获取设备列表失败');
              this.deviceList = [];
            }
            resolve();
          });
        });
      } catch (error) {
        console.error('获取设备列表失败:', error);
        this.$message.error('获取设备列表失败');
        this.deviceList = [];
      } finally {
        this.deviceLoading = false;
      }
    },

    async handleDeviceChange(deviceId) {
      if (!deviceId) {
        this.pumps = [];
        this.stopAutoRefresh();
        return;
      }

      if (this.isMonitoring(deviceId)) {
        this.stopMonitoring(deviceId);
      }

      await this.loadPumpStatus(deviceId);

      if (this.autoRefresh) {
        this.startAutoRefresh(deviceId);
      }
    },

    async loadPumpStatus(deviceId) {
      this.monitorLoading = true;
      try {
        await new Promise((resolve) => {
          Api.pump.getPumpStatus(deviceId, ({ data }) => {
            if (data.code === 0) {
              this.pumps = data.data || [];
            }
            resolve();
          });
        });
      } catch (error) {
        console.error('获取水泵状态失败:', error);
        this.$message.error('获取水泵状态失败');
      } finally {
        this.monitorLoading = false;
      }
    },

    async refreshAllStatus() {
      if (this.selectedDeviceId) {
        await this.loadPumpStatus(this.selectedDeviceId);
        this.$message.success('状态刷新成功');
      }
    },

    handleAutoRefreshChange(value) {
      if (value && this.selectedDeviceId) {
        this.startAutoRefresh(this.selectedDeviceId);
      } else {
        this.stopAutoRefresh();
      }
    },

    startAutoRefresh(deviceId) {
      this.stopAutoRefresh(); // 先停止之前的定时器
      this.refreshInterval = setInterval(() => {
        this.loadPumpStatus(deviceId);
      }, 10000); // 10秒刷新一次
    },

    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }
    },

    async quickControl(pump, action) {
      try {
        const commandData = {
          deviceId: pump.deviceId,
          actuatorCode: pump.actuatorCode,
          action: action,
          parameters: action === 'start' ? { duration: 300 } : {} // 默认5分钟
        };

        const result = await new Promise((resolve, reject) => {
          Api.pump.sendPumpCommand(commandData, ({ data }) => {
            if (data.code === 0) {
              resolve(data);
            } else {
              reject(data.msg || '操作失败');
            }
          });
        });

        this.$message.success(`${action === 'start' ? '启动' : '停止'}命令发送成功`);

        // 延迟刷新状态
        setTimeout(() => {
          this.loadPumpStatus(this.selectedDeviceId);
        }, 2000);

      } catch (error) {
        this.$message.error(error || '操作失败');
      }
    },

    showDetail(pump) {
      this.selectedPump = pump;
      this.detailDialogVisible = true;
    },

    canControl(pump) {
      return pump.status === 1 && pump.isEnabled === 1;
    },

    getStatusType(status) {
      switch (status) {
        case 1: return 'success';
        case 0: return 'info';
        case -1: return 'danger';
        default: return 'warning';
      }
    },

    getStatusText(status) {
      switch (status) {
        case 1: return '正常';
        case 0: return '离线';
        case -1: return '故障';
        default: return '未知';
      }
    },

    getStatusClass(status) {
      switch (status) {
        case 1: return 'status-normal';
        case 0: return 'status-offline';
        case -1: return 'status-error';
        default: return 'status-unknown';
      }
    },


    formatDate(value) {
      if (!value) return 'N/A';
      try {
        return new Date(value).toLocaleString();
      } catch (e) {
        return 'N/A';
      }
    },

    formatJson(jsonString) {
      try {
        return JSON.stringify(JSON.parse(jsonString), null, 2);
      } catch (e) {
        return jsonString;
      }
    }
  },

  async created() {
    await this.getDeviceList();
  },

  beforeDestroy() {
    this.stopAutoRefresh();
    if (this.selectedDeviceId && this.isMonitoring(this.selectedDeviceId)) {
      this.stopMonitoring(this.selectedDeviceId);
    }
  }
};
</script>

<style scoped>
.app-container {
  min-width: 900px;
  min-height: 506px;
  height: 100vh;
  display: flex;
  position: relative;
  flex-direction: column;
  background: linear-gradient(to bottom right, #dce8ff, #e4eeff, #e6cbfd);
  background-size: cover;
}

.operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.page-title {
  font-size: 24px;
  margin: 0;
  color: #2c3e50;
}

.right-operations {
  display: flex;
  gap: 15px;
  align-items: center;
}

.main-wrapper {
  margin: 5px 22px;
  border-radius: 15px;
  min-height: calc(100vh - 24vh);
  height: auto;
  max-height: 80vh;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  background: rgba(237, 242, 255, 0.5);
  display: flex;
  flex-direction: column;
}

.content-panel {
  flex: 1;
  display: flex;
  overflow: hidden;
  height: 100%;
  border-radius: 15px;
  background: transparent;
  border: 1px solid #fff;
}

.content-area {
  flex: 1;
  height: 100%;
  min-width: 600px;
  overflow-y: auto;
  background-color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.monitor-card {
  height: fit-content;
}

.pump-card {
  height: 100%;
  transition: all 0.3s ease;
}

.pump-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pump-name {
  font-weight: 500;
  color: #303133;
}

.pump-info {
  margin-bottom: 15px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 6px 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

.info-row label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}

.el-divider {
  margin: 20px 0;
}

/* 状态样式 */
.status-normal {
  border-left: 4px solid #67c23a;
}

.status-offline {
  border-left: 4px solid #909399;
}

.status-error {
  border-left: 4px solid #f56c6c;
}

.status-unknown {
  border-left: 4px solid #e6a23c;
}

.config-section {
  margin-top: 20px;
}

.config-section h4 {
  margin-bottom: 10px;
  color: #606266;
}

.config-section pre {
  background: #f6f8fa;
  padding: 15px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  margin: 0;
}

.empty-tip {
  margin-top: 10px;
}
</style>
