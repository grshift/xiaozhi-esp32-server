<template>
  <div class="app-container">
    <div class="operation-bar">
      <h2 class="page-title">水泵管理</h2>
      <div class="right-operations">
        <el-button type="primary" @click="showAddDialog" icon="el-icon-plus">
          添加水泵
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
            <el-card>
              <div slot="header">
                <span>水泵列表</span>
                <el-button style="float: right; padding: 3px 0" type="text" @click="refreshPumps">
                  <i class="el-icon-refresh"></i> 刷新
                </el-button>
              </div>

              <div v-if="pumps.length > 0">
                <el-table
                  :data="pumps"
                  style="width: 100%"
                  :header-cell-class-name="headerCellClassName"
                >
                  <el-table-column label="水泵编码" prop="actuatorCode" width="150">
                    <template slot-scope="scope">
                      <el-tag>{{ scope.row.actuatorCode }}</el-tag>
                    </template>
                  </el-table-column>

                  <el-table-column label="水泵名称" prop="actuatorName" width="150"></el-table-column>

                  <el-table-column label="GPIO引脚" prop="gpioPin" width="100">
                    <template slot-scope="scope">
                      <el-tag type="info">{{ scope.row.gpioPin }}</el-tag>
                    </template>
                  </el-table-column>

                  <el-table-column label="启用状态" width="100">
                    <template slot-scope="scope">
                      <el-switch
                        v-model="scope.row.isEnabled"
                        :active-value="1"
                        :inactive-value="0"
                        @change="handleEnableChange(scope.row)"
                      ></el-switch>
                    </template>
                  </el-table-column>

                  <el-table-column label="连接状态" width="100">
                    <template slot-scope="scope">
                      <el-tag :type="getStatusType(scope.row.status)">
                        {{ getStatusText(scope.row.status) }}
                      </el-tag>
                    </template>
                  </el-table-column>

                  <el-table-column label="最后命令" prop="lastCommand" width="120">
                    <template slot-scope="scope">
                      {{ scope.row.lastCommand || '无' }}
                    </template>
                  </el-table-column>

                  <el-table-column label="最后更新" prop="lastUpdatedAt" width="160">
                    <template slot-scope="scope">
                      {{ formatDate(scope.row.lastUpdatedAt) }}
                    </template>
                  </el-table-column>

                  <el-table-column label="操作" width="180" fixed="right">
                    <template slot-scope="scope">
                      <el-button
                        size="mini"
                        type="primary"
                        @click="showEditDialog(scope.row)"
                        icon="el-icon-edit"
                      >
                        编辑
                      </el-button>
                      <el-button
                        size="mini"
                        type="danger"
                        @click="handleDelete(scope.row)"
                        icon="el-icon-delete"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <el-empty v-else description="该设备下没有配置水泵"></el-empty>
            </el-card>
          </div>

          <el-empty v-else description="请先选择一个设备"></el-empty>
        </div>
      </div>
    </div>

    <!-- 添加/编辑水泵对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="pumpForm"
        :model="pumpForm"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="水泵编码" prop="actuatorCode">
          <el-input
            v-model="pumpForm.actuatorCode"
            placeholder="请输入水泵编码，如：pump_01"
            :disabled="isEdit"
          ></el-input>
        </el-form-item>

        <el-form-item label="水泵名称" prop="actuatorName">
          <el-input
            v-model="pumpForm.actuatorName"
            placeholder="请输入水泵名称，如：主水泵"
          ></el-input>
        </el-form-item>

        <el-form-item label="GPIO引脚" prop="gpioPin">
          <el-input-number
            v-model="pumpForm.gpioPin"
            :min="0"
            :max="40"
            controls-position="right"
            placeholder="请输入GPIO引脚号"
          ></el-input-number>
        </el-form-item>

        <el-form-item label="配置参数">
          <el-input
            v-model="pumpForm.configJson"
            type="textarea"
            :rows="4"
            placeholder='请输入JSON格式的配置信息，如：{"maxFlowRate": 100, "minFlowRate": 0}'
          ></el-input>
        </el-form-item>

        <el-form-item label="校准数据">
          <el-input
            v-model="pumpForm.calibrationData"
            type="textarea"
            :rows="3"
            placeholder='请输入校准数据，如：{"calibrationFactor": 1.0}'
          ></el-input>
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch
            v-model="pumpForm.isEnabled"
            :active-value="1"
            :inactive-value="0"
          ></el-switch>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitPumpForm"
          :loading="submitLoading"
        >
          确定
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Api from '@/apis/api';

export default {
  name: 'PumpManagement',
  data() {
    return {
      deviceList: [],
      selectedDeviceId: null,
      pumps: [],
      deviceLoading: false,
      pumpLoading: false,
      submitLoading: false,
      dialogVisible: false,
      isEdit: false,
      dialogTitle: '添加水泵',
      pumpForm: {
        actuatorCode: '',
        actuatorName: '',
        gpioPin: 0,
        configJson: '{}',
        calibrationData: '',
        isEnabled: 1
      },
      formRules: {
        actuatorCode: [
          { required: true, message: '请输入水泵编码', trigger: 'blur' }
        ],
        actuatorName: [
          { required: true, message: '请输入水泵名称', trigger: 'blur' }
        ],
        gpioPin: [
          { required: true, message: '请输入GPIO引脚', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    async getDeviceList() {
      this.deviceLoading = true;
      try {
        // 这里应该调用实际的设备列表API
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
        this.pumps = [];
        return;
      }
      await this.loadPumps(deviceId);
    },

    async loadPumps(deviceId) {
      this.pumpLoading = true;
      return new Promise((resolve) => {
        Api.pump.getPumpStatus(deviceId, ({ data }) => {
          this.pumpLoading = false;
          if (data.code === 0) {
            this.pumps = data.data || [];
            resolve();
          } else {
            this.$message.error(data.msg || '获取水泵列表失败');
            resolve();
          }
        });
      });
    },

    async refreshPumps() {
      if (this.selectedDeviceId) {
        await this.loadPumps(this.selectedDeviceId);
        this.$message.success('刷新成功');
      }
    },

    showAddDialog() {
      if (!this.selectedDeviceId) {
        this.$message.warning('请先选择设备');
        return;
      }

      this.isEdit = false;
      this.dialogTitle = '添加水泵';
      this.pumpForm = {
        actuatorCode: '',
        actuatorName: '',
        gpioPin: 0,
        configJson: '{}',
        calibrationData: '',
        isEnabled: 1
      };
      this.dialogVisible = true;
    },

    showEditDialog(pump) {
      this.isEdit = true;
      this.dialogTitle = '编辑水泵';
      this.pumpForm = { ...pump };
      this.dialogVisible = true;
    },

    submitPumpForm() {
      this.$refs.pumpForm.validate(async (valid) => {
        if (!valid) return;

        this.submitLoading = true;
        try {
          // 注意：后端没有提供水泵的CRUD接口，这里只是示例
          // 实际使用时需要后端提供相应的接口
          this.$message.info('水泵配置功能需要后端提供相应的API接口');
          this.dialogVisible = false;
        } catch (error) {
          console.error('提交失败:', error);
        } finally {
          this.submitLoading = false;
        }
      });
    },

    async handleDelete(pump) {
      try {
        await this.$confirm(`确定要删除水泵 "${pump.actuatorName}" 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });

        // 注意：后端没有提供删除接口，这里只是示例
        this.$message.info('水泵删除功能需要后端提供相应的API接口');
      } catch {
        // 用户取消删除
      }
    },

    async handleEnableChange(pump) {
      // 注意：后端没有提供更新接口，这里只是示例
      this.$message.info('水泵状态更新功能需要后端提供相应的API接口');
      // 恢复原值
      pump.isEnabled = pump.isEnabled === 1 ? 0 : 1;
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

    formatDate(value) {
      if (!value) return 'N/A';
      try {
        return new Date(value).toLocaleString();
      } catch (e) {
        return 'N/A';
      }
    },

    headerCellClassName() {
      return 'custom-header';
    }
  },

  async created() {
    await this.getDeviceList();
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

.el-divider {
  margin: 20px 0;
}

:deep(.custom-header) {
  background: rgba(255, 255, 255, 0.8) !important;
  color: #606266 !important;
  font-weight: 500;
}

.dialog-footer {
  text-align: right;
}
</style>
