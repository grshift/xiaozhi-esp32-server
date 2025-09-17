<template>
  <div class="app-container">
    <div class="operation-bar">
      <h2 class="page-title">水泵历史记录</h2>
      <div class="right-operations">
        <el-button type="primary" @click="exportHistory" icon="el-icon-download">
          导出记录
        </el-button>
      </div>
    </div>

    <div class="main-wrapper">
      <div class="content-panel">
        <div class="content-area">
          <!-- 查询条件 -->
          <el-card class="filter-card">
            <el-form :inline="true" :model="queryForm" class="filter-form">
              <el-form-item label="设备">
                <el-select
                  v-model="queryForm.deviceId"
                  placeholder="选择设备"
                  @change="handleDeviceChange"
                  filterable
                  clearable
                  style="width: 200px;"
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
                  description="您还没有绑定任何设备，请先激活设备后再查看历史记录"
                  type="info"
                  :closable="false"
                  show-icon>
                </el-alert>
              </div>
              </el-form-item>

              <el-form-item label="水泵">
                <el-select
                  v-model="queryForm.actuatorCode"
                  placeholder="选择水泵"
                  filterable
                  clearable
                  style="width: 150px;"
                  :disabled="!queryForm.deviceId"
                >
                  <el-option
                    v-for="pump in pumpList"
                    :key="pump.actuatorCode"
                    :label="pump.actuatorName"
                    :value="pump.actuatorCode"
                  >
                </el-option>
              </el-select>
              </el-form-item>

              <el-form-item label="命令类型">
                <el-select
                  v-model="queryForm.command"
                  placeholder="选择命令"
                  clearable
                  style="width: 120px;"
                >
                  <el-option label="启动" value="start"></el-option>
                  <el-option label="停止" value="stop"></el-option>
                  <el-option label="设置流量" value="set_flow"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="dateRange"
                  type="datetimerange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="yyyy-MM-dd HH:mm:ss"
                  value-format="yyyy-MM-dd HH:mm:ss"
                  style="width: 350px;"
                >
                </el-date-picker>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="handleSearch" icon="el-icon-search">
                  查询
                </el-button>
                <el-button @click="handleReset" icon="el-icon-refresh">
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <el-divider></el-divider>

          <!-- 统计信息 -->
          <el-row :gutter="20" class="stats-row">
            <el-col :span="4">
              <el-card class="stats-card">
                <div class="stats-number">{{ stats.total }}</div>
                <div class="stats-label">总操作次数</div>
              </el-card>
            </el-col>
            <el-col :span="4">
              <el-card class="stats-card">
                <div class="stats-number">{{ stats.success }}</div>
                <div class="stats-label">成功操作</div>
              </el-card>
            </el-col>
            <el-col :span="4">
              <el-card class="stats-card">
                <div class="stats-number">{{ stats.failed }}</div>
                <div class="stats-label">失败操作</div>
              </el-card>
            </el-col>
            <el-col :span="4">
              <el-card class="stats-card">
                <div class="stats-number">{{ stats.startCount }}</div>
                <div class="stats-label">启动命令</div>
              </el-card>
            </el-col>
            <el-col :span="4">
              <el-card class="stats-card">
                <div class="stats-number">{{ stats.stopCount }}</div>
                <div class="stats-label">停止命令</div>
              </el-card>
            </el-col>
            <el-col :span="4">
              <el-card class="stats-card">
                <div class="stats-number">{{ formatDuration(stats.avgDuration) }}</div>
                <div class="stats-label">平均耗时</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 历史记录表格 -->
          <el-card v-loading="tableLoading">
            <div slot="header">
              <span>操作历史记录</span>
              <el-button style="float: right; padding: 3px 0" type="text" @click="handleRefresh">
                <i class="el-icon-refresh"></i> 刷新
              </el-button>
            </div>

            <el-table
              :data="historyList"
              style="width: 100%"
              :header-cell-class-name="headerCellClassName"
              stripe
            >
              <el-table-column label="执行时间" width="180" prop="executedAt">
                <template slot-scope="scope">
                  {{ formatDate(scope.row.executedAt) }}
                </template>
              </el-table-column>

              <el-table-column label="设备" width="150" prop="deviceId">
                <template slot-scope="scope">
                  <el-tag size="mini">{{ getDeviceName(scope.row.deviceId) }}</el-tag>
                </template>
              </el-table-column>

              <el-table-column label="水泵" width="120" prop="actuatorCode">
                <template slot-scope="scope">
                  <el-tag type="info" size="mini">{{ scope.row.actuatorCode }}</el-tag>
                </template>
              </el-table-column>

              <el-table-column label="命令" width="100" prop="command">
                <template slot-scope="scope">
                  <el-tag :type="getCommandType(scope.row.command)">
                    {{ getCommandText(scope.row.command) }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="参数" min-width="150" prop="commandParams">
                <template slot-scope="scope">
                  <div class="params-display">
                    {{ formatParams(scope.row.commandParams) }}
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="执行结果" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.responseStatus === 'SUCCESS' ? 'success' : 'danger'">
                    {{ scope.row.responseStatus === 'SUCCESS' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="响应消息" min-width="150" prop="responseMessage">
                <template slot-scope="scope">
                  <span :class="getMessageClass(scope.row.responseStatus)">
                    {{ scope.row.responseMessage || '无' }}
                  </span>
                </template>
              </el-table-column>

              <el-table-column label="执行耗时" width="100" prop="executionDuration">
                <template slot-scope="scope">
                  {{ formatDuration(scope.row.executionDuration) }}
                </template>
              </el-table-column>

              <el-table-column label="操作" width="80" fixed="right">
                <template slot-scope="scope">
                  <el-button
                    size="mini"
                    type="primary"
                    @click="showDetail(scope.row)"
                    icon="el-icon-info"
                  >
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-wrapper">
              <el-pagination
                @current-change="handlePageChange"
                @size-change="handleSizeChange"
                :current-page="queryForm.current"
                :page-sizes="[10, 20, 50, 100]"
                :page-size="queryForm.size"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalCount"
              >
              </el-pagination>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      title="操作详情"
      :visible.sync="detailDialogVisible"
      width="600px"
    >
      <div v-if="selectedRecord">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="记录ID">
            {{ selectedRecord.id }}
          </el-descriptions-item>
          <el-descriptions-item label="设备ID">
            {{ selectedRecord.deviceId }}
          </el-descriptions-item>
          <el-descriptions-item label="执行器ID">
            {{ selectedRecord.actuatorId }}
          </el-descriptions-item>
          <el-descriptions-item label="执行器编码">
            {{ selectedRecord.actuatorCode }}
          </el-descriptions-item>
          <el-descriptions-item label="命令">
            {{ selectedRecord.command }}
          </el-descriptions-item>
          <el-descriptions-item label="命令参数">
            <pre class="params-json">{{ formatParamsJson(selectedRecord.commandParams) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="响应状态">
            <el-tag :type="selectedRecord.responseStatus === 'SUCCESS' ? 'success' : 'danger'">
              {{ selectedRecord.responseStatus }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应消息">
            {{ selectedRecord.responseMessage }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatDate(selectedRecord.executedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="执行耗时">
            {{ formatDuration(selectedRecord.executionDuration) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Api from '@/apis/api';

export default {
  name: 'PumpHistory',
  data() {
    return {
      deviceList: [],
      pumpList: [],
      historyList: [],
      totalCount: 0,
      deviceLoading: false,
      tableLoading: false,
      detailDialogVisible: false,
      selectedRecord: null,
      dateRange: [],
      queryForm: {
        deviceId: '',
        actuatorCode: '',
        command: '',
        current: 1,
        size: 10
      },
      stats: {
        total: 0,
        success: 0,
        failed: 0,
        startCount: 0,
        stopCount: 0,
        avgDuration: 0
      }
    };
  },
  methods: {
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
      this.queryForm.actuatorCode = '';
      if (deviceId) {
        await this.loadPumpList(deviceId);
      } else {
        this.pumpList = [];
      }
    },

    async loadPumpList(deviceId) {
      return new Promise((resolve) => {
        Api.pump.getPumpStatus(deviceId, ({ data }) => {
          if (data.code === 0) {
            this.pumpList = data.data || [];
          }
          resolve();
        });
      });
    },

    async handleSearch() {
      this.queryForm.current = 1;
      await this.loadHistory();
    },

    async handleReset() {
      this.queryForm = {
        deviceId: '',
        actuatorCode: '',
        command: '',
        current: 1,
        size: 10
      };
      this.dateRange = [];
      this.actuatorList = [];
      this.historyList = [];
      this.totalCount = 0;
      this.resetStats();
    },

    async loadHistory() {
      if (!this.queryForm.deviceId) {
        this.$message.warning('请先选择设备');
        return;
      }

      this.tableLoading = true;
      try {
        const params = {
          deviceId: this.queryForm.deviceId,
          current: this.queryForm.current,
          size: this.queryForm.size
        };

        // 添加时间范围参数
        if (this.dateRange && this.dateRange.length === 2) {
          params.start = this.dateRange[0];
          params.end = this.dateRange[1];
        }

        await new Promise((resolve) => {
          Api.pump.getPumpHistory(params, ({ data }) => {
            if (data.code === 0) {
              this.historyList = data.data.records || [];
              this.totalCount = data.data.total || 0;
              this.calculateStats();
            } else {
              this.$message.error(data.msg || '获取历史记录失败');
            }
            resolve();
          });
        });
      } catch (error) {
        console.error('加载历史记录失败:', error);
        this.$message.error('加载历史记录失败');
      } finally {
        this.tableLoading = false;
      }
    },

    calculateStats() {
      const records = this.historyList;
      this.stats = {
        total: records.length,
        success: records.filter(r => r.responseStatus === 'SUCCESS').length,
        failed: records.filter(r => r.responseStatus !== 'SUCCESS').length,
        startCount: records.filter(r => r.command === 'start').length,
        stopCount: records.filter(r => r.command === 'stop').length,
        avgDuration: records.length > 0
          ? records.reduce((sum, r) => sum + (r.executionDuration || 0), 0) / records.length
          : 0
      };
    },

    resetStats() {
      this.stats = {
        total: 0,
        success: 0,
        failed: 0,
        startCount: 0,
        stopCount: 0,
        avgDuration: 0
      };
    },

    async handleRefresh() {
      await this.loadHistory();
    },

    handlePageChange(page) {
      this.queryForm.current = page;
      this.loadHistory();
    },

    handleSizeChange(size) {
      this.queryForm.size = size;
      this.queryForm.current = 1;
      this.loadHistory();
    },

    showDetail(record) {
      this.selectedRecord = record;
      this.detailDialogVisible = true;
    },

    exportHistory() {
      // 检查是否选择了设备
      if (!this.queryForm.deviceId) {
        this.$message.warning('请先选择设备');
        return;
      }

      // 构建导出参数
      const exportParams = {
        deviceId: this.queryForm.deviceId,
        actuatorCode: this.queryForm.actuatorCode,
        commandType: this.queryForm.command
      };

      // 添加时间范围参数
      if (this.dateRange && this.dateRange.length === 2) {
        exportParams.startDate = this.dateRange[0];
        exportParams.endDate = this.dateRange[1];
      }

      // 显示加载提示
      const loading = this.$loading({
        lock: true,
        text: '正在导出数据...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });

      // 设置超时处理
      const timeoutId = setTimeout(() => {
        loading.close();
        this.$message.error('导出超时，请重试');
      }, 30000); // 30秒超时

      // 调用导出API
      Api.pump.exportPumpHistory(exportParams, (response) => {
        clearTimeout(timeoutId); // 清除超时定时器
        loading.close();
        
        try {
      let blob;
      if (response instanceof Blob) {
        blob = response;
      } else if (response.data instanceof Blob) {
        blob = response.data;
      } else {
        // 如果不是Blob，尝试创建Blob，明确指定UTF-8编码
        blob = new Blob([response], { type: 'text/csv;charset=utf-8' }); //
      }

      // 再次确保blob的MIME类型包含UTF-8编码信息
      if (blob.type && !blob.type.includes('charset')) {
        blob = new Blob([blob], { type: 'text/csv;charset=utf-8' }); //
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // 生成一个安全的英文文件名，避免文件名本身乱码
      const now = new Date();
      const timestamp = now.toISOString().slice(0, 19).replace(/[:-]/g, '');
      const deviceName = this.getDeviceName(this.queryForm.deviceId);
      link.download = `pump_history_${deviceName}_${timestamp}.csv`; //

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);

      this.$message.success('导出成功！');
    } catch (error) {
      console.error('导出文件处理失败:', error);
      this.$message.error('导出失败，请重试');
    }
      });
    },

    getDeviceName(deviceId) {
      const device = this.deviceList.find(d => d.id === deviceId);
      return device ? device.name : deviceId;
    },

    getPumpName(actuatorCode) {
      const pump = this.pumpList.find(p => p.actuatorCode === actuatorCode);
      return pump ? pump.actuatorName : actuatorCode;
    },

    getCommandType(command) {
      switch (command) {
        case 'start': return 'success';
        case 'stop': return 'danger';
        case 'set_flow': return 'primary';
        default: return 'info';
      }
    },

    getCommandText(command) {
      switch (command) {
        case 'start': return '启动';
        case 'stop': return '停止';
        case 'set_flow': return '设置流量';
        default: return command;
      }
    },

    formatParams(params) {
      if (!params) return '无';
      try {
        const parsed = JSON.parse(params);
        if (parsed.flowRate !== undefined) {
          return `流量: ${parsed.flowRate} L/min`;
        }
        if (parsed.duration !== undefined) {
          return `持续时间: ${parsed.duration}秒`;
        }
        return '有参数';
      } catch (e) {
        return params;
      }
    },

    formatParamsJson(params) {
      if (!params) return '无';
      try {
        return JSON.stringify(JSON.parse(params), null, 2);
      } catch (e) {
        return params;
      }
    },

    getMessageClass(status) {
      return status === 'SUCCESS' ? 'success-message' : 'error-message';
    },

    formatDate(value) {
      if (!value) return 'N/A';
      try {
        return new Date(value).toLocaleString();
      } catch (e) {
        return 'N/A';
      }
    },

    formatDuration(duration) {
      if (!duration) return '0ms';
      if (duration < 1000) {
        return `${duration}ms`;
      }
      return `${(duration / 1000).toFixed(2)}s`;
    },

    headerCellClassName() {
      return 'custom-header';
    }
  },

  created() {
    this.getDeviceList();
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
  gap: 10px;
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

.filter-card {
  margin-bottom: 0;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.stats-row {
  margin: 20px 0;
}

.stats-card {
  text-align: center;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stats-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
}

.params-display {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  background: #f6f8fa;
  padding: 4px 8px;
  border-radius: 4px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.success-message {
  color: #67c23a;
}

.error-message {
  color: #f56c6c;
}

.params-json {
  background: #f6f8fa;
  padding: 15px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.el-divider {
  margin: 20px 0;
}

:deep(.custom-header) {
  background: rgba(255, 255, 255, 0.8) !important;
  color: #606266 !important;
  font-weight: 500;
}

.empty-tip {
  margin-top: 10px;
}
</style>
