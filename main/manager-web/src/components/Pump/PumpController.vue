<template>
  <el-card class="pump-controller" shadow="never">
    <div slot="header" class="clearfix">
      <span>{{ pump.actuatorName || pump.actuatorCode }} ({{ pump.actuatorCode }})</span>
      <el-tag :type="statusInfo.type" size="mini" class="status-tag">{{ statusInfo.text }}</el-tag>
    </div>

    <div class="control-panel">
      <div class="status-display">
        <div class="status-item">
          <label>最后命令:</label>
          <span>{{ pump.lastCommand || '无' }}</span>
        </div>
        <div class="status-item">
          <label>执行时间:</label>
          <span>{{ formatDate(pump.lastCommandAt) }}</span>
        </div>
        <div class="status-item">
          <label>最后状态:</label>
          <span>{{ pump.lastStatus || '未知' }}</span>
        </div>
      </div>

      <el-divider></el-divider>

      <el-form :model="form" label-width="100px" size="small">
        <el-form-item label="流速 (L/min)">
          <el-slider
            v-model="form.flowRate"
            :min="0"
            :max="100"
            show-input
            :disabled="loading"
          ></el-slider>
        </el-form-item>

        <el-form-item label="持续时间">
          <el-input-number
            v-model="form.duration"
            :min="0"
            :max="3600"
            :step="10"
            controls-position="right"
            :disabled="loading"
          />
          <span class="form-tip">秒 (0表示不限时)</span>
        </el-form-item>
      </el-form>

      <div class="control-buttons">
        <el-button
          type="success"
          icon="el-icon-video-play"
          @click="startPump"
          :loading="loading"
          :disabled="!canControl"
        >
          启动
        </el-button>

        <el-button
          type="danger"
          icon="el-icon-video-pause"
          @click="stopPump"
          :loading="loading"
          :disabled="!canControl"
        >
          停止
        </el-button>

        <el-button
          type="primary"
          icon="el-icon-setting"
          @click="setFlowRate"
          :loading="loading"
          :disabled="!canControl"
        >
          设置流量
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'PumpController',
  props: {
    pump: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      form: {
        flowRate: 50,
        duration: 0
      }
    };
  },
  computed: {
    statusInfo() {
      const status = this.pump.status;
      switch (status) {
        case 1:
          return { type: 'success', text: '正常' };
        case 0:
          return { type: 'info', text: '离线' };
        case -1:
          return { type: 'danger', text: '故障' };
        default:
          return { type: 'warning', text: '未知' };
      }
    },
    canControl() {
      return this.pump.status === 1; // 只有正常状态才能控制
    }
  },
  methods: {
    ...mapActions('pump', ['sendCommand']),

    async startPump() {
      await this.executeCommand({
        deviceId: this.pump.deviceId,
        actuatorCode: this.pump.actuatorCode,
        action: 'start',
        parameters: {
          flowRate: this.form.flowRate,
          duration: this.form.duration
        }
      });
    },

    async stopPump() {
      await this.executeCommand({
        deviceId: this.pump.deviceId,
        actuatorCode: this.pump.actuatorCode,
        action: 'stop'
      });
    },

    async setFlowRate() {
      await this.executeCommand({
        deviceId: this.pump.deviceId,
        actuatorCode: this.pump.actuatorCode,
        action: 'set_flow',
        parameters: {
          flowRate: this.form.flowRate
        }
      });
    },

    async executeCommand(command) {
      this.loading = true;
      try {
        const result = await this.sendCommand(command);
        this.$message.success(result.msg || '命令发送成功');
      } catch (error) {
        this.$message.error(error || '操作失败，请重试');
      } finally {
        this.loading = false;
      }
    },

    formatDate(value) {
      if (!value) return 'N/A';
      try {
        return new Date(value).toLocaleString();
      } catch (e) {
        return 'N/A';
      }
    }
  }
};
</script>

<style scoped>
.pump-controller {
  margin-bottom: 20px;
}

.clearfix {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-tag {
  margin-left: auto;
}

.status-display {
  margin-bottom: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.status-item label {
  font-weight: bold;
  color: #606266;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.form-tip {
  color: #909399;
  margin-left: 10px;
  font-size: 12px;
}

.el-form-item {
  margin-bottom: 15px;
}

.el-divider {
  margin: 20px 0;
}
</style>
