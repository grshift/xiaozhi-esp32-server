<template>
  <div class="welcome">
    <HeaderBar/>

    <div class="operation-bar">
      <h2 class="page-title">传感器告警</h2>
      <div class="right-operations">
        <el-select v-model="filterParams.deviceId" placeholder="选择设备" clearable @change="loadAlertLogs">
          <el-option
            v-for="device in deviceList"
            :key="device.id"
            :label="device.macAddress"
            :value="device.id">
          </el-option>
        </el-select>
        <el-select v-model="filterParams.isResolved" placeholder="处理状态" clearable @change="loadAlertLogs">
          <el-option label="未处理" :value="0"></el-option>
          <el-option label="已处理" :value="1"></el-option>
        </el-select>
        <el-button @click="loadAlertLogs" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="main-wrapper">
      <!-- 告警统计卡片 -->
      <div class="stats-cards">
        <el-card class="stats-card" shadow="never">
          <div class="stats-content">
            <div class="stats-icon critical">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stats-info">
              <h3>{{ alertStats.critical || 0 }}</h3>
              <p>严重告警</p>
            </div>
          </div>
        </el-card>
        
        <el-card class="stats-card" shadow="never">
          <div class="stats-content">
            <div class="stats-icon error">
              <i class="el-icon-warning-outline"></i>
            </div>
            <div class="stats-info">
              <h3>{{ alertStats.error || 0 }}</h3>
              <p>错误告警</p>
            </div>
          </div>
        </el-card>
        
        <el-card class="stats-card" shadow="never">
          <div class="stats-content">
            <div class="stats-icon warning">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stats-info">
              <h3>{{ alertStats.warning || 0 }}</h3>
              <p>警告告警</p>
            </div>
          </div>
        </el-card>
        
        <el-card class="stats-card" shadow="never">
          <div class="stats-content">
            <div class="stats-icon info">
              <i class="el-icon-info"></i>
            </div>
            <div class="stats-info">
              <h3>{{ alertStats.info || 0 }}</h3>
              <p>信息告警</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 告警日志表格 -->
      <div class="content-panel">
        <el-card class="alert-card" shadow="never">
          <div slot="header" class="card-header">
            <span class="card-title">告警日志</span>
          </div>
          
          <el-table :data="alertLogs" class="transparent-table"
                    :header-cell-class-name="headerCellClassName" v-loading="loading"
                    @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" align="center"></el-table-column>
            <el-table-column label="告警时间" prop="createdAt" align="center" width="160"></el-table-column>
            <el-table-column label="设备" align="center" width="150">
              <template slot-scope="scope">
                {{ getDeviceName(scope.row.deviceId) }}
              </template>
            </el-table-column>
            <el-table-column label="传感器" align="center" width="120">
              <template slot-scope="scope">
                {{ getSensorName(scope.row.sensorId) }}
              </template>
            </el-table-column>
            <el-table-column label="规则名称" prop="ruleName" align="center" width="150"></el-table-column>
            <el-table-column label="告警级别" align="center" width="100">
              <template slot-scope="scope">
                <el-tag :type="getAlertLevelType(scope.row.alertLevel)" size="mini">
                  {{ getAlertLevelText(scope.row.alertLevel) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="触发值" prop="triggerValue" align="center" width="100"></el-table-column>
            <el-table-column label="告警消息" prop="alertMessage" align="center" show-overflow-tooltip></el-table-column>
            <el-table-column label="处理状态" align="center" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.isResolved ? 'success' : 'danger'" size="mini">
                  {{ scope.row.isResolved ? '已处理' : '未处理' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="处理时间" prop="resolvedAt" align="center" width="160">
              <template slot-scope="scope">
                {{ scope.row.resolvedAt || '--' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="120" fixed="right">
              <template slot-scope="scope">
                <el-button 
                  v-if="!scope.row.isResolved" 
                  size="mini" 
                  type="success" 
                  @click="resolveAlert(scope.row)">
                  处理
                </el-button>
                <el-button size="mini" @click="viewAlertDetail(scope.row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 批量操作 -->
          <div class="batch-operations" v-if="selectedAlerts.length > 0">
            <span>已选择 {{ selectedAlerts.length }} 条告警</span>
            <el-button size="mini" type="success" @click="batchResolveAlerts">批量处理</el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 告警详情对话框 -->
    <el-dialog title="告警详情" :visible.sync="detailDialogVisible" width="600px">
      <div v-if="currentAlert" class="alert-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="告警时间">
            {{ currentAlert.createdAt }}
          </el-descriptions-item>
          <el-descriptions-item label="设备">
            {{ getDeviceName(currentAlert.deviceId) }}
          </el-descriptions-item>
          <el-descriptions-item label="传感器">
            {{ getSensorName(currentAlert.sensorId) }}
          </el-descriptions-item>
          <el-descriptions-item label="规则名称">
            {{ currentAlert.ruleName }}
          </el-descriptions-item>
          <el-descriptions-item label="告警级别">
            <el-tag :type="getAlertLevelType(currentAlert.alertLevel)" size="mini">
              {{ getAlertLevelText(currentAlert.alertLevel) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="触发值">
            {{ currentAlert.triggerValue }}
          </el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <el-tag :type="currentAlert.isResolved ? 'success' : 'danger'" size="mini">
              {{ currentAlert.isResolved ? '已处理' : '未处理' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="处理时间">
            {{ currentAlert.resolvedAt || '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="告警消息" :span="2">
            {{ currentAlert.alertMessage }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 处理操作 -->
        <div v-if="!currentAlert.isResolved" class="resolve-section">
          <h4>处理告警</h4>
          <el-form :model="resolveForm" label-width="100px">
            <el-form-item label="处理备注">
              <el-input 
                type="textarea" 
                v-model="resolveForm.remark" 
                placeholder="请输入处理备注"
                :rows="3">
              </el-input>
            </el-form-item>
          </el-form>
          <div class="resolve-actions">
            <el-button type="success" @click="confirmResolveAlert">确认处理</el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <el-footer style="flex-shrink:unset;">
      <version-footer />
    </el-footer>
  </div>
</template>

<script>
import HeaderBar from '../components/HeaderBar.vue'
import VersionFooter from '../components/VersionFooter.vue'
import api from '../apis/api'

export default {
  name: 'SensorAlerts',
  components: {
    HeaderBar,
    VersionFooter
  },
  data() {
    return {
      // 过滤参数
      filterParams: {
        deviceId: '',
        isResolved: ''
      },
      
      // 数据
      alertLogs: [],
      deviceList: [],
      sensorList: [],
      loading: false,
      
      // 统计数据
      alertStats: {
        critical: 0,
        error: 0,
        warning: 0,
        info: 0
      },
      
      // 选择的告警
      selectedAlerts: [],
      
      // 详情对话框
      detailDialogVisible: false,
      currentAlert: null,
      resolveForm: {
        remark: ''
      },
      
      // 定时器
      refreshTimer: null
    }
  },
  mounted() {
    this.loadDevices();
    this.loadSensorList();
    this.loadAlertLogs();
    this.calculateStats();
    
    // 设置定时刷新
    this.refreshTimer = setInterval(() => {
      this.loadAlertLogs();
      this.calculateStats();
    }, 60000); // 1分钟刷新一次
  },
  beforeDestroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },
  methods: {
    headerCellClassName() {
      return 'table-header-cell';
    },
    
    // ========== 数据加载 ==========
    loadDevices() {
      // 调用设备列表接口
      api.device.getDeviceList((res) => {
        if (res.data) {
          this.deviceList = res.data.data || res.data;
        }
      });
    },
    
    loadSensorList() {
      // 加载所有传感器列表用于显示名称
      this.sensorList = [];
    },
    
    loadAlertLogs() {
      this.loading = true;
      const params = {};
      if (this.filterParams.deviceId) {
        params.deviceId = this.filterParams.deviceId;
      }
      if (this.filterParams.isResolved !== '') {
        params.isResolved = this.filterParams.isResolved;
      }
      
      api.sensor.getAlertLogList(params, (res) => {
        this.loading = false;
        if (res.data) {
          this.alertLogs = res.data.data || res.data;
          this.calculateStats();
        }
      });
    },
    
    calculateStats() {
      // 计算各级别告警统计
      this.alertStats = {
        critical: 0,
        error: 0,
        warning: 0,
        info: 0
      };
      
      this.alertLogs.forEach(alert => {
        if (!alert.isResolved) {
          this.alertStats[alert.alertLevel] = (this.alertStats[alert.alertLevel] || 0) + 1;
        }
      });
    },
    
    // ========== 告警处理 ==========
    resolveAlert(alert) {
      this.$confirm('确定要处理这条告警吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.sensor.resolveAlert(alert.id, (res) => {
          if (res.data.code === 'success' || res.data.code === 0) {
            this.$message.success('处理成功');
            this.loadAlertLogs();
          } else {
            this.$message.error(res.data.msg || '处理失败');
          }
        });
      });
    },
    
    batchResolveAlerts() {
      if (this.selectedAlerts.length === 0) {
        this.$message.warning('请先选择要处理的告警');
        return;
      }
      
      this.$confirm(`确定要批量处理 ${this.selectedAlerts.length} 条告警吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        let processed = 0;
        const total = this.selectedAlerts.length;
        
        this.selectedAlerts.forEach(alert => {
          api.sensor.resolveAlert(alert.id, (res) => {
            processed++;
            if (processed === total) {
              this.$message.success(`成功处理 ${total} 条告警`);
              this.loadAlertLogs();
              this.selectedAlerts = [];
            }
          });
        });
      });
    },
    
    handleSelectionChange(selection) {
      this.selectedAlerts = selection.filter(alert => !alert.isResolved);
    },
    
    // ========== 详情查看 ==========
    viewAlertDetail(alert) {
      this.currentAlert = alert;
      this.resolveForm.remark = '';
      this.detailDialogVisible = true;
    },
    
    confirmResolveAlert() {
      if (!this.currentAlert) return;
      
      api.sensor.resolveAlert(this.currentAlert.id, (res) => {
        if (res.data.code === 'success' || res.data.code === 0) {
          this.$message.success('处理成功');
          this.detailDialogVisible = false;
          this.loadAlertLogs();
        } else {
          this.$message.error(res.data.msg || '处理失败');
        }
      });
    },
    
    // ========== 辅助方法 ==========
    getDeviceName(deviceId) {
      const device = this.deviceList.find(d => d.id === deviceId);
      return device ? device.macAddress : deviceId;
    },
    
    getSensorName(sensorId) {
      const sensor = this.sensorList.find(s => s.id === sensorId);
      return sensor ? sensor.sensorName : sensorId;
    },
    
    getAlertLevelType(level) {
      const types = {
        'info': 'info',
        'warning': 'warning',
        'error': 'danger',
        'critical': 'danger'
      };
      return types[level] || 'info';
    },
    
    getAlertLevelText(level) {
      const texts = {
        'info': '信息',
        'warning': '警告',
        'error': '错误',
        'critical': '严重'
      };
      return texts[level] || level;
    }
  }
}
</script>

<style scoped>
.welcome {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.page-title {
  color: white;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.right-operations {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-wrapper {
  flex: 1;
  padding: 20px 40px;
  overflow-y: auto;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}

.stats-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stats-icon.critical {
  background: linear-gradient(45deg, #ff4757, #ff3838);
}

.stats-icon.error {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
}

.stats-icon.warning {
  background: linear-gradient(45deg, #ffa726, #ff9800);
}

.stats-icon.info {
  background: linear-gradient(45deg, #42a5f5, #2196f3);
}

.stats-info h3 {
  margin: 0 0 5px 0;
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.stats-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.content-panel {
  margin-bottom: 20px;
}

.alert-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.transparent-table {
  background: transparent;
}

.transparent-table ::v-deep .el-table__header {
  background: rgba(102, 126, 234, 0.1);
}

.transparent-table ::v-deep .el-table__row {
  background: transparent;
}

.transparent-table ::v-deep .el-table__row:hover {
  background: rgba(102, 126, 234, 0.1);
}

.transparent-table ::v-deep .table-header-cell {
  background: rgba(102, 126, 234, 0.2);
  color: #333;
  font-weight: 600;
}

.batch-operations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-top: 1px solid #eee;
  margin-top: 15px;
}

.alert-detail {
  padding: 20px 0;
}

.resolve-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.resolve-section h4 {
  margin: 0 0 20px 0;
  color: #333;
}

.resolve-actions {
  text-align: right;
  margin-top: 20px;
}

.el-footer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
