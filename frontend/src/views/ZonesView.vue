<!-- frontend/src/views/ZonesView.vue -->
<template>
  <div class="zones-view">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>区域列表</span>
              <el-button type="primary" size="small" :icon="Plus" @click="showCreateDialog">添加区域</el-button>
            </div>
          </template>

          <el-table :data="zones" stripe v-loading="loading" @row-click="selectZone" style="cursor: pointer;">
            <el-table-column prop="name" label="区域名称" />
            <el-table-column prop="camera_name" label="摄像头" width="100" />
            <el-table-column prop="enabled" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.enabled ? 'success' : 'info'" size="small">
                  {{ scope.row.enabled ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <span>{{ isEdit ? '编辑区域' : '区域详情' }}</span>
          </template>

          <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" v-if="currentZone || !isEdit">
            <el-form-item label="区域名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入区域名称" :disabled="!isEdit" />
            </el-form-item>
            <el-form-item label="摄像头" prop="camera_id">
              <el-select v-model="form.camera_id" placeholder="请选择摄像头" :disabled="!isEdit" @change="loadCameraImage">
                <el-option
                  v-for="camera in cameras"
                  :key="camera.id"
                  :label="camera.name"
                  :value="camera.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="区域坐标">
              <div class="coordinate-editor">
                <canvas
                  ref="canvasRef"
                  width="640"
                  height="360"
                  @click="handleCanvasClick"
                  @mousemove="handleCanvasMouseMove"
                  @mouseleave="handleCanvasMouseLeave"
                  style="border: 1px solid #dcdfe6; cursor: crosshair;"
                ></canvas>
                <div class="coordinate-info">
                  <p>点击画布添加顶点，至少需要3个点</p>
                  <p>当前顶点数: {{ coordinates.length }}</p>
                  <el-button size="small" @click="clearCoordinates" :disabled="!isEdit">清空</el-button>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="启用" prop="enabled">
              <el-switch v-model="form.enabled" :disabled="!isEdit" />
            </el-form-item>
            <el-form-item v-if="isEdit">
              <el-button type="primary" @click="submitForm">保存</el-button>
              <el-button @click="cancelEdit">取消</el-button>
            </el-form-item>
            <el-form-item v-else>
              <el-button type="primary" @click="startEdit">编辑</el-button>
              <el-button type="danger" @click="deleteZone" :disabled="!currentZone">删除</el-button>
            </el-form-item>
          </el-form>

          <el-empty v-else description="请选择一个区域或创建新区域" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useZoneStore } from '../stores/zone'
import { useCameraStore } from '../stores/camera'

const zoneStore = useZoneStore()
const cameraStore = useCameraStore()

const zones = ref([])
const cameras = ref([])
const currentZone = ref(null)
const loading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const canvasRef = ref(null)
const coordinates = ref([])
const mousePos = ref({ x: 0, y: 0 })

const form = ref({
  name: '',
  camera_id: null,
  coordinates: '[]',
  enabled: true
})

const rules = {
  name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
  camera_id: [{ required: true, message: '请选择摄像头', trigger: 'change' }]
}

const fetchZones = async () => {
  loading.value = true
  try {
    await zoneStore.fetchZones()
    zones.value = zoneStore.zones
  } finally {
    loading.value = false
  }
}

const fetchCameras = async () => {
  await cameraStore.fetchCameras()
  cameras.value = cameraStore.cameras
}

const selectZone = async (zone) => {
  currentZone.value = zone
  isEdit.value = false
  form.value = {
    name: zone.name,
    camera_id: zone.camera_id,
    coordinates: zone.coordinates,
    enabled: zone.enabled
  }
  coordinates.value = JSON.parse(zone.coordinates)
  await nextTick()
  drawCanvas()
}

const showCreateDialog = () => {
  currentZone.value = null
  isEdit.value = true
  form.value = {
    name: '',
    camera_id: null,
    coordinates: '[]',
    enabled: true
  }
  coordinates.value = []
  clearCanvas()
}

const startEdit = () => {
  isEdit.value = true
}

const cancelEdit = () => {
  isEdit.value = false
  if (currentZone.value) {
    selectZone(currentZone.value)
  }
}

const submitForm = async () => {
  await formRef.value.validate()
  if (coordinates.value.length < 3) {
    ElMessage.warning('至少需要3个顶点')
    return
  }
  form.value.coordinates = JSON.stringify(coordinates.value)
  try {
    if (currentZone.value) {
      await zoneStore.updateZone(currentZone.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await zoneStore.createZone(form.value)
      ElMessage.success('创建成功')
    }
    isEdit.value = false
    await fetchZones()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteZone = async () => {
  if (!currentZone.value) return
  try {
    await ElMessageBox.confirm('确定要删除该区域吗？', '提示', {
      type: 'warning'
    })
    await zoneStore.deleteZone(currentZone.value.id)
    ElMessage.success('删除成功')
    currentZone.value = null
    await fetchZones()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const loadCameraImage = async () => {
  await nextTick()
  drawCanvas()
}

const handleCanvasClick = (event) => {
  if (!isEdit.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 640
  const y = ((event.clientY - rect.top) / rect.height) * 360
  coordinates.value.push([x, y])
  drawCanvas()
}

const handleCanvasMouseMove = (event) => {
  const rect = canvasRef.value.getBoundingClientRect()
  mousePos.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  if (isEdit.value) {
    drawCanvas()
  }
}

const handleCanvasMouseLeave = () => {
  if (isEdit.value) {
    drawCanvas()
  }
}

const drawCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 绘制顶点
  ctx.fillStyle = '#409EFF'
  coordinates.value.forEach(([x, y]) => {
    ctx.beginPath()
    ctx.arc(x, y, 5, 0, Math.PI * 2)
    ctx.fill()
  })

  // 绘制多边形
  if (coordinates.value.length >= 2) {
    ctx.strokeStyle = '#409EFF'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(coordinates.value[0][0], coordinates.value[0][1])
    for (let i = 1; i < coordinates.value.length; i++) {
      ctx.lineTo(coordinates.value[i][0], coordinates.value[i][1])
    }
    if (coordinates.value.length >= 3) {
      ctx.closePath()
      ctx.fillStyle = 'rgba(64, 158, 255, 0.1)'
      ctx.fill()
    }
    ctx.stroke()
  }

  // 绘制鼠标预览线
  if (isEdit.value && coordinates.value.length > 0 && mousePos.value.x > 0) {
    const rect = canvas.getBoundingClientRect()
    const lastPoint = coordinates.value[coordinates.value.length - 1]
    ctx.strokeStyle = 'rgba(64, 158, 255, 0.5)'
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(lastPoint[0], lastPoint[1])
    ctx.lineTo(
      (mousePos.value.x / rect.width) * 640,
      (mousePos.value.y / rect.height) * 360
    )
    ctx.stroke()
    ctx.setLineDash([])
  }
}

const clearCoordinates = () => {
  coordinates.value = []
  drawCanvas()
}

const clearCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
}

onMounted(async () => {
  await fetchZones()
  await fetchCameras()
})
</script>

<style scoped>
.coordinate-editor {
  display: flex;
  gap: 20px;
}

.coordinate-editor canvas {
  flex-shrink: 0;
}

.coordinate-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
