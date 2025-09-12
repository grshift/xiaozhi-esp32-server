<template>
  <div class="app-container">
    <div class="operation-bar">
      <h2 class="page-title">水泵控制</h2>
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
            >
              <el-option
                v-for="device in deviceList"
                :key="device.id"
                :label="device.name || device.macAddress"
                :value="device.id"
              >
              </el-option>
            </el-select>
          </el-card>

          <el-divider></el-divider>

          <div v-if="selectedDeviceId" v-loading="pumpLoading">
            <div v-if="pumps.length > 0">
              <pump-controller
                v-for="pump in pumps"
                :key="pump.actuatorCode"
                :pump="pump"
              />
            </div>
            <el-empty v-else description="该设备下没有配置水泵"></el-empty>
          </div>

          <el-empty v-else description="请先选择一个设备"></el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import PumpController from '@/components/Pump/PumpController.vue';
import Api from '@/apis/api';

export default {
  name: 'PumpControl',
  components: {
    PumpController
  },
  data() {
    return {
      deviceList: [],
      selectedDeviceId: null,
      deviceLoading: false,
      pumpLoading: false
    };
  },
  computed: {
    ...mapGetters('pump', ['getStatusesByDevice', 'isMonitoring']),
    pumps() {
      return this.getStatusesByDevice(this.selectedDeviceId);
    }
  },
  methods: {
    ...mapActions('pump', ['fetchPumpStatus', 'startMonitoring', 'stopMonitoring']),

    async getDeviceList() {
      this.deviceLoading = true;
      try {
        // 这里应该调用实际的设备列表API
        // 暂时使用模拟数据
        this.deviceList = [
          { id: 'esp32-device-001', name: '1号农业大棚', macAddress: 'AA:BB:CC:DD:EE:01' },
          { id: 'esp32-device-002', name: '2号水产养殖场', macAddress: 'AA:BB:CC:DD:EE:02' },
          { id: 'esp32-device-003', name: '3号温室大棚', macAddress: 'AA:BB:CC:DD:EE:03' }
        ];
      } catch (error) {
        console.error('获取设备列表失败:', error);
        this.$message.error('获取设备列表失败');
      } finally {
        this.deviceLoading = false;
      }
    },

    async handleDeviceChange(deviceId) {
      if (!deviceId) {
        // 停止对之前设备的监控
        if (this.selectedDeviceId && this.isMonitoring(this.selectedDeviceId)) {
          this.stopMonitoring(this.selectedDeviceId);
        }
        this.selectedDeviceId = null;
        return;
      }

      // 停止监控旧设备
      if (this.selectedDeviceId && this.isMonitoring(this.selectedDeviceId)) {
        this.stopMonitoring(this.selectedDeviceId);
      }

      this.pumpLoading = true;
      try {
        await this.fetchPumpStatus(deviceId);
        // 开始监控新设备
        this.startMonitoring({ deviceId });
      } catch (error) {
        console.error('获取水泵状态失败:', error);
        this.$message.error('获取水泵状态失败');
      } finally {
        this.pumpLoading = false;
      }
    }
  },

  created() {
    this.getDeviceList();
  },

  beforeDestroy() {
    // 页面销毁时停止所有监控
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

.el-divider {
  margin: 20px 0;
}
</style>
