<template>
  <div class="welcome">
    <HeaderBar/>

    <div class="operation-bar">
      <h2 class="page-title">传感器监控</h2>
      <div class="right-operations">
        <el-select v-model="selectedDeviceId" placeholder="选择设备" @change="loadRealtimeData" style="width: 200px;">
          <el-option
            v-for="device in deviceList"
            :key="device.id"
            :label="device.macAddress"
            :value="device.id">
          </el-option>
        </el-select>
        <el-button @click="loadRealtimeData" :loading="realtimeLoading">刷新数据</el-button>
        <el-button @click="showHistoryDialog">查看历史</el-button>
      </div>
    </div>

    <div class="main-wrapper">
      <!-- 实时数据卡片 -->
      <div class="realtime-cards">
        <el-card 
          v-for="sensor in realtimeData" 
          :key="sensor.id" 
          class="sensor-card" 
          shadow="never">
          <div class="sensor-info">
            <div class="sensor-header">
              <h3 class="sensor-name">{{ sensor.sensorName }}</h3>
              <el-tag :type="getSensorStatusType(sensor)" size="mini">
                {{ getSensorStatusText(sensor) }}
              </el-tag>
            </div>
            <div class="sensor-value">
              <span class="value">{{ sensor.lastValue || '--' }}</span>
              <span class="unit">{{ getSensorUnit(sensor.sensorTypeId) }}</span>
            </div>
            <div class="sensor-details">
              <p class="sensor-code">编码: {{ sensor.sensorCode }}</p>
              <p class="update-time">更新时间: {{ sensor.lastUpdatedAt || '暂无数据' }}</p>
            </div>
            <div class="sensor-actions">
              <el-button size="mini" @click="viewSensorHistory(sensor)">历史数据</el-button>
              <el-button size="mini" @click="viewSensorAlerts(sensor)">告警设置</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 无数据提示 -->
      <div v-if="realtimeData.length === 0 && !realtimeLoading" class="no-data">
        <el-empty description="请选择设备查看传感器数据"></el-empty>
      </div>
    </div>

    <!-- 历史数据对话框 -->
    <el-dialog title="历史数据查询" :visible.sync="historyDialogVisible" width="80%" top="5vh">
      <div class="history-controls">
        <el-form :inline="true" :model="historyQuery" class="history-form">
          <el-form-item label="传感器">
            <el-select v-model="historyQuery.sensorId" placeholder="选择传感器" style="width: 200px;">
              <el-option
                v-for="sensor in realtimeData"
                :key="sensor.id"
                :label="sensor.sensorName"
                :value="sensor.id">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="historyQuery.dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="yyyy-MM-dd HH:mm:ss"
              value-format="yyyy-MM-dd HH:mm:ss">
            </el-date-picker>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadHistoryData" :loading="historyLoading">查询</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 历史数据图表 -->
      <div class="chart-container">
        <div ref="historyChart" style="width: 100%; height: 400px;"></div>
      </div>

      <!-- 历史数据表格 -->
      <el-table :data="historyData" class="history-table" v-loading="historyLoading" max-height="300">
        <el-table-column label="时间" prop="collectedAt" align="center" width="180"></el-table-column>
        <el-table-column label="数值" prop="value" align="center" width="120"></el-table-column>
        <el-table-column label="单位" align="center" width="80">
          <template slot-scope="scope">
            {{ getSensorUnit(scope.row.sensorTypeId) }}
          </template>
        </el-table-column>
        <el-table-column label="数据质量" prop="qualityFlag" align="center" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.qualityFlag === 1 ? 'success' : 'warning'" size="mini">
              {{ scope.row.qualityFlag === 1 ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 告警设置对话框 -->
    <el-dialog title="告警设置" :visible.sync="alertDialogVisible" width="600px">
      <div class="alert-rules">
        <div class="alert-header">
          <span>当前告警规则</span>
          <el-button size="mini" type="primary" @click="showCreateAlertRule">新增规则</el-button>
        </div>
        
        <el-table :data="alertRules" class="alert-table">
          <el-table-column label="规则名称" prop="ruleName" align="center"></el-table-column>
          <el-table-column label="条件类型" align="center">
            <template slot-scope="scope">
              {{ getConditionTypeText(scope.row.conditionType) }}
            </template>
          </el-table-column>
          <el-table-column label="告警级别" align="center">
            <template slot-scope="scope">
              <el-tag :type="getAlertLevelType(scope.row.alertLevel)" size="mini">
                {{ getAlertLevelText(scope.row.alertLevel) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" align="center">
            <template slot-scope="scope">
              <el-tag :type="scope.row.isEnabled ? 'success' : 'danger'" size="mini">
                {{ scope.row.isEnabled ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="120">
            <template slot-scope="scope">
              <el-button size="mini" @click="editAlertRule(scope.row)">编辑</el-button>
              <el-button size="mini" type="danger" @click="deleteAlertRule(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 告警规则编辑对话框 -->
    <el-dialog :title="alertRuleDialogTitle" :visible.sync="alertRuleDialogVisible" width="500px">
      <el-form :model="alertRuleForm" :rules="alertRuleRules" ref="alertRuleForm" label-width="120px">
        <el-form-item label="规则名称" prop="ruleName">
          <el-input v-model="alertRuleForm.ruleName" placeholder="请输入规则名称"></el-input>
        </el-form-item>
        <el-form-item label="条件类型" prop="conditionType">
          <el-select v-model="alertRuleForm.conditionType" placeholder="选择条件类型" style="width: 100%">
            <el-option label="阈值告警" value="threshold"></el-option>
            <el-option label="范围告警" value="range"></el-option>
          </el-select>
        </el-form-item>
        <div v-if="alertRuleForm.conditionType === 'threshold'">
          <el-form-item label="操作符" prop="operator">
            <el-select v-model="alertRuleForm.operator" placeholder="选择操作符" style="width: 100%">
              <el-option label="大于" value=">"></el-option>
              <el-option label="大于等于" value=">="></el-option>
              <el-option label="小于" value="<"></el-option>
              <el-option label="小于等于" value="<="></el-option>
              <el-option label="等于" value="=="></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="阈值" prop="threshold">
            <el-input-number v-model="alertRuleForm.threshold" :precision="2" style="width: 100%"></el-input-number>
          </el-form-item>
        </div>
        <div v-if="alertRuleForm.conditionType === 'range'">
          <el-form-item label="最小值" prop="minValue">
            <el-input-number v-model="alertRuleForm.minValue" :precision="2" style="width: 100%"></el-input-number>
          </el-form-item>
          <el-form-item label="最大值" prop="maxValue">
            <el-input-number v-model="alertRuleForm.maxValue" :precision="2" style="width: 100%"></el-input-number>
          </el-form-item>
        </div>
        <el-form-item label="告警级别" prop="alertLevel">
          <el-select v-model="alertRuleForm.alertLevel" placeholder="选择告警级别" style="width: 100%">
            <el-option label="信息" value="info"></el-option>
            <el-option label="警告" value="warning"></el-option>
            <el-option label="错误" value="error"></el-option>
            <el-option label="严重" value="critical"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="冷却时间(分钟)" prop="cooldownMinutes">
          <el-input-number v-model="alertRuleForm.cooldownMinutes" :min="1" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="状态" prop="isEnabled">
          <el-switch v-model="alertRuleForm.isEnabled" :active-value="1" :inactive-value="0"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="alertRuleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAlertRule">确定</el-button>
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
  name: 'SensorMonitor',
  components: {
    HeaderBar,
    VersionFooter
  },
  data() {
    return {
      // 设备和实时数据
      deviceList: [],
      selectedDeviceId: '',
      realtimeData: [],
      realtimeLoading: false,
      sensorTypeList: [],
      
      // 历史数据
      historyDialogVisible: false,
      historyQuery: {
        sensorId: '',
        dateRange: []
      },
      historyData: [],
      historyLoading: false,
      historyChart: null,
      
      // 告警设置
      alertDialogVisible: false,
      alertRules: [],
      currentSensor: null,
      alertRuleDialogVisible: false,
      alertRuleDialogTitle: '新增告警规则',
      alertRuleForm: {
        ruleName: '',
        deviceId: '',
        sensorId: '',
        conditionType: 'threshold',
        operator: '>',
        threshold: 0,
        minValue: 0,
        maxValue: 100,
        alertLevel: 'warning',
        cooldownMinutes: 30,
        isEnabled: 1
      },
      alertRuleRules: {
        ruleName: [
          { required: true, message: '请输入规则名称', trigger: 'blur' }
        ],
        conditionType: [
          { required: true, message: '请选择条件类型', trigger: 'change' }
        ],
        alertLevel: [
          { required: true, message: '请选择告警级别', trigger: 'change' }
        ]
      },
      editingAlertRule: null,
      
      // 定时器
      refreshTimer: null
    }
  },
  mounted() {
    this.loadSensorTypes();
    this.loadDevices();
    // 设置定时刷新
    this.refreshTimer = setInterval(() => {
      if (this.selectedDeviceId) {
        this.loadRealtimeData();
      }
    }, 30000); // 30秒刷新一次
  },
  beforeDestroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
    if (this.historyChart) {
      this.historyChart.dispose();
    }
  },
  methods: {
    // ========== 基础数据加载 ==========
    loadSensorTypes() {
      api.sensor.getSensorTypeList((res) => {
        if (res.data) {
          this.sensorTypeList = res.data.data || res.data;
        }
      });
    },
    
    loadDevices() {
      // 调用设备列表接口
      api.device.getDeviceList((res) => {
        if (res.data) {
          this.deviceList = res.data.data || res.data;
        }
      });
    },
    
    loadRealtimeData() {
      if (!this.selectedDeviceId) {
        this.realtimeData = [];
        return;
      }
      
      this.realtimeLoading = true;
      api.sensor.getRealtimeData(this.selectedDeviceId, (res) => {
        this.realtimeLoading = false;
        if (res.data) {
          this.realtimeData = res.data.data || res.data;
        }
      });
    },
    
    // ========== 历史数据 ==========
    showHistoryDialog() {
      if (!this.selectedDeviceId) {
        this.$message.warning('请先选择设备');
        return;
      }
      this.historyDialogVisible = true;
      // 设置默认时间范围为最近24小时
      const end = new Date();
      const start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
      this.historyQuery.dateRange = [
        this.formatDateTime(start),
        this.formatDateTime(end)
      ];
    },
    
    viewSensorHistory(sensor) {
      this.historyQuery.sensorId = sensor.id;
      this.showHistoryDialog();
      this.loadHistoryData();
    },
    
    loadHistoryData() {
      if (!this.historyQuery.sensorId || !this.historyQuery.dateRange || this.historyQuery.dateRange.length !== 2) {
        this.$message.warning('请选择传感器和时间范围');
        return;
      }
      
      this.historyLoading = true;
      const params = {
        deviceId: this.selectedDeviceId,
        sensorId: this.historyQuery.sensorId,
        start: this.historyQuery.dateRange[0],
        end: this.historyQuery.dateRange[1]
      };
      
      api.sensor.getHistoryData(params, (res) => {
        this.historyLoading = false;
        if (res.data) {
          this.historyData = res.data.data || res.data;
          this.renderHistoryChart();
        }
      });
    },
    
    renderHistoryChart() {
      // 这里可以集成 ECharts 来渲染图表
      // 由于没有引入 ECharts，这里先留空
      console.log('渲染历史数据图表', this.historyData);
    },
    
    // ========== 告警管理 ==========
    viewSensorAlerts(sensor) {
      this.currentSensor = sensor;
      this.alertDialogVisible = true;
      this.loadAlertRules();
    },
    
    loadAlertRules() {
      if (!this.currentSensor) return;
      
      api.sensor.getAlertRuleList(this.selectedDeviceId, (res) => {
        if (res.data) {
          const allRules = res.data.data || res.data;
          this.alertRules = allRules.filter(rule => rule.sensorId === this.currentSensor.id);
        }
      });
    },
    
    showCreateAlertRule() {
      this.alertRuleDialogTitle = '新增告警规则';
      this.alertRuleForm = {
        ruleName: '',
        deviceId: this.selectedDeviceId,
        sensorId: this.currentSensor.id,
        conditionType: 'threshold',
        operator: '>',
        threshold: 0,
        minValue: 0,
        maxValue: 100,
        alertLevel: 'warning',
        cooldownMinutes: 30,
        isEnabled: 1
      };
      this.editingAlertRule = null;
      this.alertRuleDialogVisible = true;
    },
    
    editAlertRule(rule) {
      this.alertRuleDialogTitle = '编辑告警规则';
      this.alertRuleForm = { ...rule };
      // 解析条件配置
      if (rule.conditionConfig) {
        const config = JSON.parse(rule.conditionConfig);
        if (rule.conditionType === 'threshold') {
          this.alertRuleForm.operator = config.operator;
          this.alertRuleForm.threshold = config.threshold;
        } else if (rule.conditionType === 'range') {
          this.alertRuleForm.minValue = config.min;
          this.alertRuleForm.maxValue = config.max;
        }
      }
      this.editingAlertRule = rule;
      this.alertRuleDialogVisible = true;
    },
    
    saveAlertRule() {
      this.$refs.alertRuleForm.validate((valid) => {
        if (valid) {
          // 构建条件配置
          let conditionConfig = {};
          if (this.alertRuleForm.conditionType === 'threshold') {
            conditionConfig = {
              operator: this.alertRuleForm.operator,
              threshold: this.alertRuleForm.threshold
            };
          } else if (this.alertRuleForm.conditionType === 'range') {
            conditionConfig = {
              min: this.alertRuleForm.minValue,
              max: this.alertRuleForm.maxValue
            };
          }
          
          const ruleData = {
            ...this.alertRuleForm,
            conditionConfig: JSON.stringify(conditionConfig)
          };
          
          if (this.editingAlertRule) {
            // 更新
            api.sensor.updateAlertRule(this.editingAlertRule.id, ruleData, (res) => {
              if (res.data.code === 'success' || res.data.code === 0) {
                this.$message.success('更新成功');
                this.alertRuleDialogVisible = false;
                this.loadAlertRules();
              } else {
                this.$message.error(res.data.msg || '更新失败');
              }
            });
          } else {
            // 新增
            api.sensor.createAlertRule(ruleData, (res) => {
              if (res.data.code === 'success' || res.data.code === 0) {
                this.$message.success('创建成功');
                this.alertRuleDialogVisible = false;
                this.loadAlertRules();
              } else {
                this.$message.error(res.data.msg || '创建失败');
              }
            });
          }
        }
      });
    },
    
    deleteAlertRule(rule) {
      this.$confirm('确定要删除这个告警规则吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.sensor.deleteAlertRule(rule.id, (res) => {
          if (res.data.code === 'success' || res.data.code === 0) {
            this.$message.success('删除成功');
            this.loadAlertRules();
          } else {
            this.$message.error(res.data.msg || '删除失败');
          }
        });
      });
    },
    
    // ========== 辅助方法 ==========
    getSensorUnit(typeId) {
      const type = this.sensorTypeList.find(t => t.id === typeId);
      return type ? type.unit : '';
    },
    
    getSensorStatusType(sensor) {
      if (!sensor.lastUpdatedAt) return 'info';
      const updateTime = new Date(sensor.lastUpdatedAt).getTime();
      const now = new Date().getTime();
      const diff = now - updateTime;
      if (diff > 5 * 60 * 1000) return 'danger'; // 5分钟无数据
      if (diff > 2 * 60 * 1000) return 'warning'; // 2分钟无数据
      return 'success';
    },
    
    getSensorStatusText(sensor) {
      if (!sensor.lastUpdatedAt) return '无数据';
      const updateTime = new Date(sensor.lastUpdatedAt).getTime();
      const now = new Date().getTime();
      const diff = now - updateTime;
      if (diff > 5 * 60 * 1000) return '离线';
      if (diff > 2 * 60 * 1000) return '延迟';
      return '正常';
    },
    
    getConditionTypeText(type) {
      const types = {
        'threshold': '阈值告警',
        'range': '范围告警'
      };
      return types[type] || type;
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
    },
    
    formatDateTime(date) {
      return date.getFullYear() + '-' + 
             String(date.getMonth() + 1).padStart(2, '0') + '-' + 
             String(date.getDate()).padStart(2, '0') + ' ' + 
             String(date.getHours()).padStart(2, '0') + ':' + 
             String(date.getMinutes()).padStart(2, '0') + ':' + 
             String(date.getSeconds()).padStart(2, '0');
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

.realtime-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.sensor-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: none;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  transition: transform 0.3s ease;
}

.sensor-card:hover {
  transform: translateY(-5px);
}

.sensor-info {
  padding: 10px;
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.sensor-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.sensor-value {
  text-align: center;
  margin-bottom: 15px;
}

.value {
  font-size: 36px;
  font-weight: 700;
  color: #667eea;
}

.unit {
  font-size: 14px;
  color: #666;
  margin-left: 5px;
}

.sensor-details {
  margin-bottom: 15px;
}

.sensor-details p {
  margin: 5px 0;
  font-size: 12px;
  color: #666;
}

.sensor-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.history-controls {
  margin-bottom: 20px;
}

.history-form {
  display: flex;
  align-items: center;
  gap: 20px;
}

.chart-container {
  margin-bottom: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.history-table {
  margin-top: 20px;
}

.alert-rules {
  margin: 20px 0;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.alert-table {
  margin-top: 15px;
}

.dialog-footer {
  text-align: right;
}

.el-footer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
