<!-- frontend/src/views/StatisticsView.vue -->
<template>
  <div class="statistics-view">
    <!-- 统计概览 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview?.today_violations || 0 }}</div>
              <div class="stat-label">今日违规</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon :size="24"><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview?.week_violations || 0 }}</div>
              <div class="stat-label">本周违规</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon :size="24"><VideoCamera /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview?.total_cameras || 0 }}</div>
              <div class="stat-label">摄像头总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon :size="24"><Location /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ overview?.total_zones || 0 }}</div>
              <div class="stat-label">检测区域总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选条件 -->
    <el-card style="margin-bottom: 20px;">
      <el-form :inline="true" :model="dateRange">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="统计周期">
          <el-select v-model="groupBy" placeholder="请选择">
            <el-option label="按天" value="day" />
            <el-option label="按周" value="week" />
            <el-option label="按月" value="month" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchStatistics">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>违规趋势</span>
          </template>
          <div id="trend-chart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>时段分布</span>
          </template>
          <div id="period-chart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>区域统计</span>
          </template>
          <div id="zone-chart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>摄像头统计</span>
          </template>
          <div id="camera-chart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Warning, TrendCharts, VideoCamera, Location } from '@element-plus/icons-vue'
import { useStatisticsStore } from '../stores/statistics'
import * as echarts from 'echarts'

const statisticsStore = useStatisticsStore()

const overview = ref(null)
const dateRange = ref([])
const groupBy = ref('day')

let trendChart = null
let periodChart = null
let zoneChart = null
let cameraChart = null

const initTrendChart = () => {
  const chartDom = document.getElementById('trend-chart')
  trendChart = echarts.init(chartDom)
}

const initPeriodChart = () => {
  const chartDom = document.getElementById('period-chart')
  periodChart = echarts.init(chartDom)
}

const initZoneChart = () => {
  const chartDom = document.getElementById('zone-chart')
  zoneChart = echarts.init(chartDom)
}

const initCameraChart = () => {
  const chartDom = document.getElementById('camera-chart')
  cameraChart = echarts.init(chartDom)
}

const fetchStatistics = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    return
  }

  const startTime = `${dateRange.value[0]}T00:00:00`
  const endTime = `${dateRange.value[1]}T23:59:59`

  // 获取趋势数据
  await statisticsStore.fetchTrendStats(startTime, endTime, groupBy.value)
  updateTrendChart()

  // 获取时段数据
  await statisticsStore.fetchPeriodStats(startTime, endTime)
  updatePeriodChart()

  // 获取区域数据
  await statisticsStore.fetchZoneStats(startTime, endTime)
  updateZoneChart()

  // 获取摄像头数据
  await statisticsStore.fetchCameraStats(startTime, endTime)
  updateCameraChart()
}

const updateTrendChart = () => {
  const data = statisticsStore.trendStats?.data || []
  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date)
    },
    yAxis: { type: 'value' },
    series: [{
      name: '违规数',
      type: 'line',
      data: data.map(d => d.count),
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ])
      }
    }]
  })
}

const updatePeriodChart = () => {
  const data = statisticsStore.periodStats || []
  const periodMap = { morning: '上午', afternoon: '下午', night: '晚上' }
  periodChart?.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.map(d => ({
        name: periodMap[d.period],
        value: d.violation_count
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

const updateZoneChart = () => {
  const data = statisticsStore.zoneStats || []
  zoneChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: data.map(d => d.zone_name),
      axisLabel: { interval: 0, rotate: 30 }
    },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: data.map(d => d.violation_count),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      }
    }]
  })
}

const updateCameraChart = () => {
  const data = statisticsStore.cameraStats || []
  cameraChart?.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '70%',
      data: data.map(d => ({
        name: d.camera_name,
        value: d.violation_count
      }))
    }]
  })
}

const fetchOverview = async () => {
  await statisticsStore.fetchOverview()
  overview.value = statisticsStore.overview
}

const resizeCharts = () => {
  trendChart?.resize()
  periodChart?.resize()
  zoneChart?.resize()
  cameraChart?.resize()
}

onMounted(async () => {
  // 设置默认时间范围（最近7天）
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 7)
  dateRange.value = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]

  await fetchOverview()

  initTrendChart()
  initPeriodChart()
  initZoneChart()
  initCameraChart()

  await fetchStatistics()

  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  trendChart?.dispose()
  periodChart?.dispose()
  zoneChart?.dispose()
  cameraChart?.dispose()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>
