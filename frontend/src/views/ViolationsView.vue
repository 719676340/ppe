<!-- frontend/src/views/ViolationsView.vue -->
<template>
  <div class="violations-view">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>违规记录</span>
          <div>
            <el-button type="primary" :icon="Download" @click="exportData">导出</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="摄像头">
          <el-select v-model="filters.camera_id" placeholder="全部" clearable style="width: 150px;">
            <el-option v-for="camera in cameras" :key="camera.id" :label="camera.name" :value="camera.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域">
          <el-select v-model="filters.zone_id" placeholder="全部" clearable style="width: 150px;">
            <el-option v-for="zone in zones" :key="zone.id" :label="zone.name" :value="zone.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="filters.is_processed" placeholder="全部" clearable style="width: 120px;">
            <el-option label="未处理" :value="false" />
            <el-option label="已处理" :value="true" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchViolations">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="violations" stripe v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="violation_time" label="违规时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.violation_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="camera_name" label="摄像头" width="120" />
        <el-table-column prop="zone_name" label="区域" width="120" />
        <el-table-column label="截图" width="150">
          <template #default="scope">
            <el-image
              :src="scope.row.image_path"
              fit="cover"
              style="width: 100px; height: 60px; border-radius: 4px; cursor: pointer;"
              @click="previewImage(scope.row.image_path)"
            >
              <template #error>
                <div class="image-slot">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column prop="is_processed" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_processed ? 'success' : 'danger'" size="small">
              {{ scope.row.is_processed ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
            <el-button size="small" type="primary" @click="editRemark(scope.row)">备注</el-button>
            <el-button size="small" type="danger" @click="deleteViolation(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="filters.page"
        v-model:page-size="filters.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />

      <!-- 批量操作 -->
      <div v-if="selectedViolations.length > 0" style="margin-top: 20px;">
        <el-button type="primary" @click="batchMarkProcessed">批量标记已处理</el-button>
        <el-button type="danger" @click="batchDelete">批量删除</el-button>
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="违规详情" width="800px">
      <el-descriptions :column="2" border v-if="currentViolation">
        <el-descriptions-item label="违规时间">{{ currentViolation.violation_time }}</el-descriptions-item>
        <el-descriptions-item label="摄像头">{{ currentViolation.camera_name }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ currentViolation.zone_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentViolation.is_processed ? 'success' : 'danger'">
            {{ currentViolation.is_processed ? '已处理' : '未处理' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentViolation.remark || '无' }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 20px;">
        <el-image
          :src="currentViolation?.image_path"
          fit="contain"
          style="width: 100%; max-height: 500px;"
        />
      </div>
    </el-dialog>

    <!-- 备注对话框 -->
    <el-dialog v-model="remarkVisible" title="添加备注" width="500px">
      <el-input
        v-model="remarkText"
        type="textarea"
        :rows="4"
        placeholder="请输入备注内容"
      />
      <template #footer>
        <el-button @click="remarkVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRemark">保存</el-button>
      </template>
    </el-dialog>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="截图预览"
      width="80%"
      :z-index="9999"
      append-to-body
      class="image-preview-dialog"
    >
      <div style="display: flex; justify-content: center; align-items: center; min-height: 400px;">
        <el-image
          :src="previewImageUrl"
          fit="contain"
          style="max-width: 100%; max-height: 70vh;"
        >
          <template #error>
            <div class="image-slot" style="width: 400px; height: 300px;">
              <span>图片加载失败</span>
            </div>
          </template>
        </el-image>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Download, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useViolationStore } from '../stores/violation'
import { useCameraStore } from '../stores/camera'
import { useZoneStore } from '../stores/zone'

const violationStore = useViolationStore()
const cameraStore = useCameraStore()
const zoneStore = useZoneStore()

const violations = ref([])
const cameras = ref([])
const zones = ref([])
const total = ref(0)
const loading = ref(false)
const dateRange = ref([])
const selectedViolations = ref([])
const detailVisible = ref(false)
const remarkVisible = ref(false)
const remarkText = ref('')
const currentViolation = ref(null)
const previewVisible = ref(false)
const previewImageUrl = ref('')

const filters = ref({
  camera_id: null,
  zone_id: null,
  start_time: null,
  end_time: null,
  is_processed: null,
  page: 1,
  page_size: 20
})

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const fetchViolations = async () => {
  loading.value = true
  try {
    await violationStore.fetchViolations(filters.value)
    violations.value = violationStore.violations
    total.value = violationStore.total
  } finally {
    loading.value = false
  }
}

const fetchCameras = async () => {
  await cameraStore.fetchCameras()
  cameras.value = cameraStore.cameras
}

const fetchZones = async () => {
  await zoneStore.fetchZones()
  zones.value = zoneStore.zones
}

const searchViolations = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    filters.value.start_time = dateRange.value[0]
    filters.value.end_time = dateRange.value[1]
  } else {
    filters.value.start_time = null
    filters.value.end_time = null
  }
  filters.value.page = 1
  fetchViolations()
}

const resetFilters = () => {
  dateRange.value = []
  filters.value = {
    camera_id: null,
    zone_id: null,
    start_time: null,
    end_time: null,
    is_processed: null,
    page: 1,
    page_size: 20
  }
  fetchViolations()
}

const handlePageChange = (page) => {
  filters.value.page = page
  fetchViolations()
}

const handleSizeChange = (size) => {
  filters.value.page_size = size
  filters.value.page = 1
  fetchViolations()
}

const handleSelectionChange = (selection) => {
  selectedViolations.value = selection
}

const viewDetail = (violation) => {
  currentViolation.value = violation
  detailVisible.value = true
}

const editRemark = (violation) => {
  currentViolation.value = violation
  remarkText.value = violation.remark || ''
  remarkVisible.value = true
}

const previewImage = (imageUrl) => {
  previewImageUrl.value = imageUrl
  previewVisible.value = true
}

const saveRemark = async () => {
  try {
    await violationStore.updateRemark(currentViolation.value.id, remarkText.value)
    ElMessage.success('保存成功')
    remarkVisible.value = false
    fetchViolations()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteViolation = async (violation) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗？', '提示', {
      type: 'warning'
    })
    await violationStore.deleteViolation(violation.id)
    ElMessage.success('删除成功')
    fetchViolations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchMarkProcessed = async () => {
  try {
    const ids = selectedViolations.value.map(v => v.id)
    await violationStore.batchMarkProcessed(ids)
    ElMessage.success('操作成功')
    fetchViolations()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedViolations.value.length} 条记录吗？`, '提示', {
      type: 'warning'
    })
    for (const violation of selectedViolations.value) {
      await violationStore.deleteViolation(violation.id)
    }
    ElMessage.success('删除成功')
    fetchViolations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const exportData = async () => {
  try {
    const params = {}
    if (filters.value.camera_id) params.camera_id = filters.value.camera_id
    if (filters.value.zone_id) params.zone_id = filters.value.zone_id
    if (filters.value.is_processed !== null) params.is_processed = filters.value.is_processed
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_time = dateRange.value[0]
      params.end_time = dateRange.value[1]
    }

    const response = await violationStore.exportViolations(params)

    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `violations_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  await fetchCameras()
  await fetchZones()
  await fetchViolations()
})
</script>

<style scoped>
.filter-form {
  margin-bottom: 20px;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}
</style>
