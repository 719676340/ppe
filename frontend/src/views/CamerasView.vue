<!-- frontend/src/views/CamerasView.vue -->
<template>
  <div class="cameras-view">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>摄像头管理</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog">添加摄像头</el-button>
        </div>
      </template>

      <el-table :data="cameras" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="source_type" label="源类型" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.source_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_url" label="源地址" show-overflow-tooltip />
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="后台检测" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.enabled"
              @change="toggleDetection(scope.row)"
              :loading="scope.row._toggling"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="testConnection(scope.row)">测试</el-button>
            <el-button size="small" type="primary" @click="editCamera(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCamera(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑摄像头' : '添加摄像头'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入摄像头名称" />
        </el-form-item>
        <el-form-item label="源类型" prop="source_type">
          <el-select v-model="form.source_type" placeholder="请选择源类型">
            <el-option label="RTSP流" value="rtsp" />
            <el-option label="视频文件" value="file" />
            <el-option label="USB摄像头" value="usb" />
          </el-select>
        </el-form-item>
        <el-form-item label="源地址" prop="source_url">
          <el-input v-model="form.source_url" placeholder="请输入视频源地址" />
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入安装位置" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="后台检测" prop="enabled">
          <el-switch v-model="form.enabled" />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">
            开启后将自动对该摄像头进行后台PPE检测
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCameraStore } from '../stores/camera'

const cameraStore = useCameraStore()

const cameras = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const form = ref({
  name: '',
  source_type: 'rtsp',
  source_url: '',
  location: '',
  status: 'active',
  enabled: false
})

const rules = {
  name: [{ required: true, message: '请输入摄像头名称', trigger: 'blur' }],
  source_type: [{ required: true, message: '请选择源类型', trigger: 'change' }],
  source_url: [{ required: true, message: '请输入源地址', trigger: 'blur' }]
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = {
    name: '',
    source_type: 'rtsp',
    source_url: '',
    location: '',
    status: 'active',
    enabled: false
  }
  dialogVisible.value = true
}

const editCamera = (camera) => {
  isEdit.value = true
  form.value = { ...camera }
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await cameraStore.updateCamera(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await cameraStore.createCamera(form.value)
      ElMessage.success('创建成功')

      // 如果启用了后台检测，则启动检测
      if (form.value.enabled) {
        // 重新获取列表以获得新创建的摄像头ID
        await fetchCameras()
        const newCamera = cameras.value.find(c => c.name === form.value.name)
        if (newCamera) {
          try {
            const result = await cameraStore.startDetection(newCamera.id)
            if (result.status === 'started') {
              ElMessage.success(`已自动启动检测: ${result.message}`)
            } else {
              ElMessage.warning(`检测启动状态: ${result.message}`)
            }
          } catch (error) {
            ElMessage.error('自动启动检测失败')
          }
        }
      }
    }
    dialogVisible.value = false
    await fetchCameras()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteCamera = async (camera) => {
  try {
    await ElMessageBox.confirm('确定要删除该摄像头吗？', '提示', {
      type: 'warning'
    })
    await cameraStore.deleteCamera(camera.id)
    ElMessage.success('删除成功')
    await fetchCameras()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const toggleDetection = async (camera) => {
  camera._toggling = true
  try {
    // 先更新数据库中的启用状态
    await cameraStore.updateCamera(camera.id, { enabled: camera.enabled })

    // 然后启动或停止实际的检测进程
    if (camera.enabled) {
      const result = await cameraStore.startDetection(camera.id)
      if (result.status === 'started') {
        ElMessage.success(`已启用后台检测: ${result.message}`)
      } else if (result.status === 'already_running') {
        ElMessage.warning(result.message)
      } else {
        ElMessage.error(`启动检测失败: ${result.message}`)
        // 恢复开关状态
        camera.enabled = false
        await cameraStore.updateCamera(camera.id, { enabled: false })
      }
    } else {
      const result = await cameraStore.stopDetection(camera.id)
      if (result.status === 'stopped') {
        ElMessage.success(`已禁用后台检测: ${result.message}`)
      } else if (result.status === 'not_running') {
        ElMessage.warning(result.message)
      } else {
        ElMessage.error(`停止检测失败: ${result.message}`)
      }
    }

    await fetchCameras()
  } catch (error) {
    ElMessage.error('操作失败')
    // 恢复开关状态
    camera.enabled = !camera.enabled
    await cameraStore.updateCamera(camera.id, { enabled: camera.enabled })
  } finally {
    camera._toggling = false
  }
}

const testConnection = async (camera) => {
  try {
    const result = await cameraStore.testConnection({
      source_type: camera.source_type,
      source_url: camera.source_url
    })
    if (result.success) {
      ElMessage.success(`连接成功: ${result.resolution}, ${result.fps}fps`)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

const fetchCameras = async () => {
  loading.value = true
  try {
    await cameraStore.fetchCameras()
    cameras.value = cameraStore.cameras
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCameras()
})
</script>
