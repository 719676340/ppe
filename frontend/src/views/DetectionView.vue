<!-- frontend/src/views/DetectionView.vue -->
<template>
  <div class="detection-view">
    <el-row :gutter="20">
      <!-- 视频显示区 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>实时检测</span>
              <div>
                <el-select v-model="selectedCamera" placeholder="选择摄像头" style="width: 200px; margin-right: 10px;">
                  <el-option
                    v-for="camera in cameras"
                    :key="camera.id"
                    :label="camera.name"
                    :value="camera.id"
                  />
                </el-select>
                <el-button type="primary" :icon="VideoPlay" @click="startDetection">开始检测</el-button>
                <el-button :icon="VideoPause" @click="stopDetection">停止检测</el-button>
              </div>
            </div>
          </template>

          <div class="video-container">
            <!-- MJPEG流使用img标签显示 -->
            <img
              ref="videoRef"
              style="width: 100%; height: 100%; object-fit: contain; background: #000;"
              alt="检测画面"
            />
            <canvas
              ref="canvasRef"
              style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"
            ></canvas>
          </div>

          <div style="margin-top: 20px;">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="检测状态">{{ detectionStatus }}</el-descriptions-item>
              <el-descriptions-item label="检测人数">{{ personCount }}</el-descriptions-item>
              <el-descriptions-item label="违规人数">{{ violationCount }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧信息区 -->
      <el-col :span="8">
        <!-- 检测配置 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>检测配置</span>
          </template>
          <el-form label-width="100px">
            <el-form-item label="置信度阈值">
              <el-slider v-model="confidenceThreshold" :min="0.1" :max="1" :step="0.05" :show-tooltip="true" />
              <span>{{ confidenceThreshold }}</span>
            </el-form-item>
            <el-form-item label="IOU阈值">
              <el-slider v-model="iouThreshold" :min="0.1" :max="1" :step="0.05" :show-tooltip="true" />
              <span>{{ iouThreshold }}</span>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 实时统计 -->
        <el-card>
          <template #header>
            <span>实时统计</span>
          </template>
          <div id="realtime-chart" style="width: 100%; height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 违规记录 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>最近违规记录</span>
      </template>
      <el-table :data="recentViolations" stripe>
        <el-table-column prop="violation_time" label="时间" width="180" />
        <el-table-column prop="camera_name" label="摄像头" width="120" />
        <el-table-column prop="zone_name" label="区域" width="120" />
        <el-table-column label="截图" width="150">
          <template #default="scope">
            <el-image
              :src="scope.row.image_path"
              :preview-src-list="[scope.row.image_path]"
              fit="cover"
              style="width: 100px; height: 60px;"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="viewViolation(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCameraStore } from '../stores/camera'
import { useViolationStore } from '../stores/violation'
import { detectionApi } from '../api/detection'
import * as echarts from 'echarts'

const cameraStore = useCameraStore()
const violationStore = useViolationStore()

const videoRef = ref(null)
const canvasRef = ref(null)
const selectedCamera = ref(null)
const detectionStatus = ref('未启动')
const personCount = ref(0)
const violationCount = ref(0)
const confidenceThreshold = ref(0.5)
const iouThreshold = ref(0.45)
const cameras = ref([])
const recentViolations = ref([])
let chart = null
let ws = null
let currentCameraId = null
let violationRefreshInterval = null  // 违规记录定时刷新

const initChart = () => {
  const chartDom = document.getElementById('realtime-chart')
  chart = echarts.init(chartDom)
  chart.setOption({
    title: { text: '违规趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [{ name: '违规数', type: 'line', data: [] }]
  })
}

const startDetection = async () => {
  if (!selectedCamera.value) {
    ElMessage.warning('请先选择摄像头')
    return
  }

  try {
    detectionStatus.value = '正在启动...'
    currentCameraId = selectedCamera.value

    // 调用后端API启动检测
    await detectionApi.start(selectedCamera.value)
    ElMessage.success('检测已启动')

    detectionStatus.value = '检测中'

    // 设置视频流源（MJPEG流）
    if (videoRef.value) {
      videoRef.value.src = detectionApi.getStreamUrl(selectedCamera.value)
    }

    // 连接WebSocket
    ws = new WebSocket(`ws://localhost:8000/ws/detection`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      // 启动定时刷新违规记录（每5秒刷新一次）
      violationRefreshInterval = setInterval(() => {
        loadRecentViolations()
      }, 5000)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('收到WebSocket消息:', data)

      if (data.type === 'detection') {
        personCount.value = data.person_count || 0
        violationCount.value = data.violation_count || 0
        console.log('检测数据 - 人数:', personCount.value, '违规数:', violationCount.value)
        updateChart(data.timestamp, data.violation_count)
      } else if (data.type === 'violation') {
        // 收到新的违规记录
        ElMessage.warning(`检测到违规: 摄像头${data.data.camera_id}`)
        // 刷新违规记录列表
        loadRecentViolations()
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      ElMessage.error('WebSocket连接失败')
    }

    ws.onclose = () => {
      console.log('WebSocket closed')
      if (currentCameraId) {
        detectionStatus.value = '已停止'
      }
      // 清除定时刷新
      if (violationRefreshInterval) {
        clearInterval(violationRefreshInterval)
        violationRefreshInterval = null
      }
    }

  } catch (error) {
    console.error('启动检测失败:', error)
    ElMessage.error(`启动检测失败: ${error.message || '未知错误'}`)
    detectionStatus.value = '启动失败'
  }
}

const stopDetection = async () => {
  try {
    // 清除定时刷新
    if (violationRefreshInterval) {
      clearInterval(violationRefreshInterval)
      violationRefreshInterval = null
    }

    // 停止视频流
    if (videoRef.value) {
      videoRef.value.src = ''
    }

    // 关闭WebSocket
    if (ws) {
      ws.close()
      ws = null
    }

    // 调用后端API停止检测
    if (currentCameraId) {
      await detectionApi.stop(currentCameraId)
      ElMessage.success('检测已停止')
    }

    currentCameraId = null
    detectionStatus.value = '已停止'
  } catch (error) {
    console.error('停止检测失败:', error)
    ElMessage.error(`停止检测失败: ${error.message || '未知错误'}`)
  }
}

const updateChart = (timestamp, count) => {
  if (!chart) return

  const option = chart.getOption()
  const xAxisData = option.xAxis[0].data
  const seriesData = option.series[0].data

  xAxisData.push(new Date(timestamp).toLocaleTimeString())
  seriesData.push(count)

  if (xAxisData.length > 20) {
    xAxisData.shift()
    seriesData.shift()
  }

  chart.setOption({
    xAxis: { data: xAxisData },
    series: [{ data: seriesData }]
  })
}

const viewViolation = (violation) => {
  ElMessageBox.alert(
    `<img src="${violation.image_path}" style="width: 100%;" />`,
    '违规详情',
    { dangerouslyUseHTMLString: true }
  )
}

const loadRecentViolations = async () => {
  try {
    await violationStore.fetchViolations({ page: 1, page_size: 10 })
    recentViolations.value = violationStore.violations
  } catch (error) {
    console.error('加载违规记录失败:', error)
  }
}

onMounted(async () => {
  await cameraStore.fetchCameras()
  cameras.value = cameraStore.cameras

  await violationStore.fetchViolations({ page: 1, page_size: 10 })
  recentViolations.value = violationStore.violations

  initChart()

  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

onUnmounted(() => {
  stopDetection()
  chart?.dispose()
})
</script>

<style scoped>
.video-container {
  position: relative;
  width: 100%;
  /* 移除固定比例，让视频自适应 */
  background: #000;
  aspect-ratio: auto;
  min-height: 400px;
}

.video-container img {
  width: 100%;
  height: auto;
  display: block;
}

.video-container canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
