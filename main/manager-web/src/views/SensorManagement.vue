<template>
  <div class="welcome">
    <HeaderBar/>

    <div class="operation-bar">
      <h2 class="page-title">传感器管理</h2>
      <div class="right-operations">
        <el-button type="primary" @click="showSensorTypeDialog">新增传感器类型</el-button>
        <el-button @click="showDeviceSensorDialog">配置设备传感器</el-button>
      </div>
    </div>

    <div class="main-wrapper">
      <!-- 传感器类型管理 -->
      <div class="content-panel">
        <el-card class="sensor-card" shadow="never">
          <div slot="header" class="card-header">
            <span class="card-title">传感器类型</span>
          </div>
          
          <el-table :data="sensorTypeList" class="transparent-table"
                    :header-cell-class-name="headerCellClassName" v-loading="typeLoading">
            <el-table-column label="类型代码" prop="typeCode" align="center" width="120"></el-table-column>
            <el-table-column label="类型名称" prop="typeName" align="center"></el-table-column>
            <el-table-column label="单位" prop="unit" align="center" width="80"></el-table-column>
            <el-table-column label="量程" align="center" width="150">
              <template slot-scope="scope">
                {{ scope.row.minValue }} ~ {{ scope.row.maxValue }}
              </template>
            </el-table-column>
            <el-table-column label="精度" prop="precision" align="center" width="80"></el-table-column>
            <el-table-column label="描述" prop="description" align="center" show-overflow-tooltip></el-table-column>
            <el-table-column label="操作" align="center" width="180">
              <template slot-scope="scope">
                <el-button size="mini" @click="editSensorType(scope.row)">编辑</el-button>
                <el-button size="mini" type="danger" @click="deleteSensorType(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 设备传感器配置 -->
      <div class="content-panel" style="margin-top: 20px;">
        <el-card class="sensor-card" shadow="never">
          <div slot="header" class="card-header">
            <span class="card-title">设备传感器配置</span>
            <el-select v-model="selectedDeviceId" placeholder="选择设备" @change="loadDeviceSensors" style="width: 200px; margin-left: 20px;">
              <el-option
                v-for="device in deviceList"
                :key="device.id"
                :label="device.macAddress"
                :value="device.id">
              </el-option>
            </el-select>
          </div>
          
          <el-table :data="deviceSensorList" class="transparent-table"
                    :header-cell-class-name="headerCellClassName" v-loading="deviceSensorLoading">
            <el-table-column label="传感器编码" prop="sensorCode" align="center"></el-table-column>
            <el-table-column label="传感器名称" prop="sensorName" align="center"></el-table-column>
            <el-table-column label="传感器类型" align="center">
              <template slot-scope="scope">
                {{ getSensorTypeName(scope.row.sensorTypeId) }}
              </template>
            </el-table-column>
            <el-table-column label="采样间隔(秒)" prop="samplingInterval" align="center" width="120"></el-table-column>
            <el-table-column label="最新值" align="center" width="120">
              <template slot-scope="scope">
                {{ scope.row.lastValue }} {{ getSensorTypeUnit(scope.row.sensorTypeId) }}
              </template>
            </el-table-column>
            <el-table-column label="更新时间" prop="lastUpdatedAt" align="center" width="150"></el-table-column>
            <el-table-column label="状态" align="center" width="80">
              <template slot-scope="scope">
                <el-tag :type="scope.row.isEnabled ? 'success' : 'danger'">
                  {{ scope.row.isEnabled ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="180">
              <template slot-scope="scope">
                <el-button size="mini" @click="editDeviceSensor(scope.row)">编辑</el-button>
                <el-button size="mini" type="danger" @click="deleteDeviceSensor(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- 传感器类型编辑对话框 -->
    <el-dialog :title="sensorTypeDialogTitle" :visible.sync="sensorTypeDialogVisible" width="600px">
      <el-form :model="sensorTypeForm" :rules="sensorTypeRules" ref="sensorTypeForm" label-width="120px">
        <el-form-item label="类型代码" prop="typeCode">
          <el-input v-model="sensorTypeForm.typeCode" placeholder="请输入类型代码"></el-input>
        </el-form-item>
        <el-form-item label="类型名称" prop="typeName">
          <el-input v-model="sensorTypeForm.typeName" placeholder="请输入类型名称"></el-input>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="sensorTypeForm.unit" placeholder="请输入单位"></el-input>
        </el-form-item>
        <el-form-item label="数据类型" prop="dataType">
          <el-select v-model="sensorTypeForm.dataType" placeholder="选择数据类型" style="width: 100%">
            <el-option label="数值型" value="number"></el-option>
            <el-option label="布尔型" value="boolean"></el-option>
            <el-option label="字符串" value="string"></el-option>
          </el-select>
        </el-form-item>
        <el-row>
          <el-col :span="12">
            <el-form-item label="最小值" prop="minValue">
              <el-input-number v-model="sensorTypeForm.minValue" :precision="2" style="width: 100%"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大值" prop="maxValue">
              <el-input-number v-model="sensorTypeForm.maxValue" :precision="2" style="width: 100%"></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="精度" prop="precision">
          <el-input-number v-model="sensorTypeForm.precision" :min="0" :max="10" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="sensorTypeForm.description" placeholder="请输入描述"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="sensorTypeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSensorType">确定</el-button>
      </div>
    </el-dialog>

    <!-- 设备传感器配置对话框 -->
    <el-dialog :title="deviceSensorDialogTitle" :visible.sync="deviceSensorDialogVisible" width="600px">
      <el-form :model="deviceSensorForm" :rules="deviceSensorRules" ref="deviceSensorForm" label-width="120px">
        <el-form-item label="设备" prop="deviceId">
          <el-select v-model="deviceSensorForm.deviceId" placeholder="选择设备" style="width: 100%">
            <el-option
              v-for="device in deviceList"
              :key="device.id"
              :label="device.macAddress"
              :value="device.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="传感器类型" prop="sensorTypeId">
          <el-select v-model="deviceSensorForm.sensorTypeId" placeholder="选择传感器类型" style="width: 100%">
            <el-option
              v-for="type in sensorTypeList"
              :key="type.id"
              :label="type.typeName"
              :value="type.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="传感器编码" prop="sensorCode">
          <el-input v-model="deviceSensorForm.sensorCode" placeholder="请输入传感器编码"></el-input>
        </el-form-item>
        <el-form-item label="传感器名称" prop="sensorName">
          <el-input v-model="deviceSensorForm.sensorName" placeholder="请输入传感器名称"></el-input>
        </el-form-item>
        <el-form-item label="采样间隔(秒)" prop="samplingInterval">
          <el-input-number v-model="deviceSensorForm.samplingInterval" :min="1" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="deviceSensorForm.sort" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="状态" prop="isEnabled">
          <el-switch v-model="deviceSensorForm.isEnabled" :active-value="1" :inactive-value="0"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="deviceSensorDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDeviceSensor">确定</el-button>
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
  name: 'SensorManagement',
  components: {
    HeaderBar,
    VersionFooter
  },
  data() {
    return {
      // 传感器类型相关
      sensorTypeList: [],
      typeLoading: false,
      sensorTypeDialogVisible: false,
      sensorTypeDialogTitle: '新增传感器类型',
      sensorTypeForm: {
        typeCode: '',
        typeName: '',
        unit: '',
        dataType: 'number',
        minValue: 0,
        maxValue: 100,
        precision: 1,
        description: ''
      },
      sensorTypeRules: {
        typeCode: [
          { required: true, message: '请输入类型代码', trigger: 'blur' }
        ],
        typeName: [
          { required: true, message: '请输入类型名称', trigger: 'blur' }
        ],
        unit: [
          { required: true, message: '请输入单位', trigger: 'blur' }
        ],
        dataType: [
          { required: true, message: '请选择数据类型', trigger: 'change' }
        ]
      },
      
      // 设备传感器相关
      deviceList: [],
      selectedDeviceId: '',
      deviceSensorList: [],
      deviceSensorLoading: false,
      deviceSensorDialogVisible: false,
      deviceSensorDialogTitle: '配置设备传感器',
      deviceSensorForm: {
        deviceId: '',
        sensorTypeId: '',
        sensorCode: '',
        sensorName: '',
        samplingInterval: 60,
        sort: 0,
        isEnabled: 1
      },
      deviceSensorRules: {
        deviceId: [
          { required: true, message: '请选择设备', trigger: 'change' }
        ],
        sensorTypeId: [
          { required: true, message: '请选择传感器类型', trigger: 'change' }
        ],
        sensorCode: [
          { required: true, message: '请输入传感器编码', trigger: 'blur' }
        ],
        sensorName: [
          { required: true, message: '请输入传感器名称', trigger: 'blur' }
        ]
      },
      
      editingType: null,
      editingSensor: null
    }
  },
  mounted() {
    this.loadSensorTypes();
    this.loadDevices();
  },
  methods: {
    headerCellClassName() {
      return 'table-header-cell';
    },
    
    // ========== 传感器类型管理 ==========
    loadSensorTypes() {
      this.typeLoading = true;
      api.sensor.getSensorTypeList((res) => {
        this.typeLoading = false;
        if (res.data) {
          this.sensorTypeList = res.data.data || res.data;
        }
      });
    },
    
    showSensorTypeDialog() {
      this.sensorTypeDialogTitle = '新增传感器类型';
      this.sensorTypeForm = {
        typeCode: '',
        typeName: '',
        unit: '',
        dataType: 'number',
        minValue: 0,
        maxValue: 100,
        precision: 1,
        description: ''
      };
      this.editingType = null;
      this.sensorTypeDialogVisible = true;
    },
    
    editSensorType(row) {
      this.sensorTypeDialogTitle = '编辑传感器类型';
      this.sensorTypeForm = { ...row };
      
      // 解析valueRange JSON为minValue和maxValue
      if (row.valueRange) {
        try {
          const range = JSON.parse(row.valueRange);
          this.sensorTypeForm.minValue = range.min || 0;
          this.sensorTypeForm.maxValue = range.max || 100;
        } catch (e) {
          this.sensorTypeForm.minValue = 0;
          this.sensorTypeForm.maxValue = 100;
        }
      } else {
        this.sensorTypeForm.minValue = 0;
        this.sensorTypeForm.maxValue = 100;
      }
      
      this.editingType = row;
      this.sensorTypeDialogVisible = true;
    },
    
    saveSensorType() {
      this.$refs.sensorTypeForm.validate((valid) => {
        if (valid) {
          // 构建提交数据，将minValue和maxValue转换为valueRange JSON
          const submitData = {
            ...this.sensorTypeForm,
            valueRange: JSON.stringify({
              min: this.sensorTypeForm.minValue || 0,
              max: this.sensorTypeForm.maxValue || 100
            })
          };
          // 移除不需要的字段
          delete submitData.minValue;
          delete submitData.maxValue;
          
          if (this.editingType) {
            // 更新
            api.sensor.updateSensorType(this.editingType.id, submitData, (res) => {
              if (res.data.code === 'success' || res.data.code === 0) {
                this.$message.success('更新成功');
                this.sensorTypeDialogVisible = false;
                this.loadSensorTypes();
              } else {
                this.$message.error(res.data.msg || '更新失败');
              }
            });
          } else {
            // 新增
            api.sensor.createSensorType(submitData, (res) => {
              if (res.data.code === 'success' || res.data.code === 0) {
                this.$message.success('创建成功');
                this.sensorTypeDialogVisible = false;
                this.loadSensorTypes();
              } else {
                this.$message.error(res.data.msg || '创建失败');
              }
            });
          }
        }
      });
    },
    
    deleteSensorType(row) {
      this.$confirm('确定要删除这个传感器类型吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.sensor.deleteSensorType(row.id, (res) => {
          if (res.data.code === 'success' || res.data.code === 0) {
            this.$message.success('删除成功');
            this.loadSensorTypes();
          } else {
            this.$message.error(res.data.msg || '删除失败');
          }
        });
      });
    },
    
    // ========== 设备传感器配置管理 ==========
    loadDevices() {
      // 调用设备列表接口
      api.device.getDeviceList((res) => {
        if (res.data) {
          this.deviceList = res.data.data || res.data;
        }
      });
    },
    
    loadDeviceSensors() {
      if (!this.selectedDeviceId) {
        this.deviceSensorList = [];
        return;
      }
      
      this.deviceSensorLoading = true;
      api.sensor.getDeviceSensorList(this.selectedDeviceId, (res) => {
        this.deviceSensorLoading = false;
        if (res.data) {
          this.deviceSensorList = res.data.data || res.data;
        }
      });
    },
    
    showDeviceSensorDialog() {
      this.deviceSensorDialogTitle = '配置设备传感器';
      this.deviceSensorForm = {
        deviceId: this.selectedDeviceId || '',
        sensorTypeId: '',
        sensorCode: '',
        sensorName: '',
        samplingInterval: 60,
        sort: 0,
        isEnabled: 1
      };
      this.editingSensor = null;
      this.deviceSensorDialogVisible = true;
    },
    
    editDeviceSensor(row) {
      this.deviceSensorDialogTitle = '编辑设备传感器';
      this.deviceSensorForm = { ...row };
      this.editingSensor = row;
      this.deviceSensorDialogVisible = true;
    },
    
    saveDeviceSensor() {
      this.$refs.deviceSensorForm.validate((valid) => {
        if (valid) {
          if (this.editingSensor) {
            // 更新
            api.sensor.updateDeviceSensor(this.editingSensor.id, this.deviceSensorForm, (res) => {
              if (res.data.code === 'success' || res.data.code === 0) {
                this.$message.success('更新成功');
                this.deviceSensorDialogVisible = false;
                this.loadDeviceSensors();
              } else {
                this.$message.error(res.data.msg || '更新失败');
              }
            });
          } else {
            // 新增
            api.sensor.createDeviceSensor(this.deviceSensorForm, (res) => {
              if (res.data.code === 'success' || res.data.code === 0) {
                this.$message.success('配置成功');
                this.deviceSensorDialogVisible = false;
                this.loadDeviceSensors();
              } else {
                this.$message.error(res.data.msg || '配置失败');
              }
            });
          }
        }
      });
    },
    
    deleteDeviceSensor(row) {
      this.$confirm('确定要删除这个传感器配置吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.sensor.deleteDeviceSensor(row.id, (res) => {
          if (res.data.code === 'success' || res.data.code === 0) {
            this.$message.success('删除成功');
            this.loadDeviceSensors();
          } else {
            this.$message.error(res.data.msg || '删除失败');
          }
        });
      });
    },
    
    // ========== 辅助方法 ==========
    getSensorTypeName(typeId) {
      const type = this.sensorTypeList.find(t => t.id === typeId);
      return type ? type.typeName : '未知类型';
    },
    
    getSensorTypeUnit(typeId) {
      const type = this.sensorTypeList.find(t => t.id === typeId);
      return type ? type.unit : '';
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

.content-panel {
  margin-bottom: 20px;
}

.sensor-card {
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

.dialog-footer {
  text-align: right;
}

.el-footer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
