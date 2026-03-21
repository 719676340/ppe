<!-- frontend/src/views/NotificationsView.vue -->
<template>
  <div class="notifications-view">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>通知中心</span>
          <div>
            <el-button size="small" @click="markAllRead">全部标为已读</el-button>
            <el-button size="small" @click="clearOld">清理旧通知</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选标签 -->
      <el-radio-group v-model="filterType" @change="fetchNotifications" style="margin-bottom: 20px;">
        <el-radio-button label="all">全部 ({{ total }})</el-radio-button>
        <el-radio-button label="unread">未读 ({{ unreadCount }})</el-radio-button>
        <el-radio-button label="violation">违规</el-radio-button>
        <el-radio-button label="warning">警告</el-radio-button>
        <el-radio-button label="info">信息</el-radio-button>
        <el-radio-button label="success">成功</el-radio-button>
      </el-radio-group>

      <!-- 通知列表 -->
      <el-timeline v-loading="loading">
        <el-timeline-item
          v-for="notification in notifications"
          :key="notification.id"
          :timestamp="notification.created_at"
          placement="top"
          :color="getTimelineColor(notification.type)"
        >
          <el-card
            :class="['notification-card', { 'unread': !notification.is_read }]"
            shadow="hover"
          >
            <div class="notification-header">
              <div class="notification-title">
                <el-tag :type="getTagType(notification.type)" size="small">
                  {{ getTypeLabel(notification.type) }}
                </el-tag>
                <span style="margin-left: 10px;">{{ notification.title }}</span>
              </div>
              <div class="notification-actions">
                <el-button
                  v-if="!notification.is_read"
                  size="small"
                  type="primary"
                  link
                  @click="markRead(notification)"
                >
                  标为已读
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  link
                  @click="deleteNotification(notification)"
                >
                  删除
                </el-button>
              </div>
            </div>
            <div class="notification-content">
              {{ notification.message }}
            </div>
            <div v-if="notification.violation_id" class="notification-link">
              <el-button size="small" link @click="viewViolation(notification)">
                查看违规详情
              </el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <!-- 空状态 -->
      <el-empty v-if="notifications.length === 0" description="暂无通知" />

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useNotificationStore } from '../stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()

const notifications = ref([])
const total = ref(0)
const unreadCount = ref(0)
const loading = ref(false)
const filterType = ref('all')
const page = ref(1)
const pageSize = ref(20)

const fetchNotifications = async () => {
  loading.value = true
  try {
    const unreadOnly = filterType.value === 'unread'
    await notificationStore.fetchNotifications(unreadOnly)
    notifications.value = notificationStore.notifications
    total.value = notificationStore.total
    unreadCount.value = notificationStore.unreadCount

    // 按类型过滤
    if (filterType.value !== 'all' && filterType.value !== 'unread') {
      notifications.value = notifications.value.filter(n => n.type === filterType.value)
    }
  } finally {
    loading.value = false
  }
}

const getTagType = (type) => {
  const typeMap = {
    violation: 'danger',
    warning: 'warning',
    info: 'info',
    success: 'success'
  }
  return typeMap[type] || 'info'
}

const getTimelineColor = (type) => {
  const colorMap = {
    violation: '#F56C6C',
    warning: '#E6A23C',
    info: '#909399',
    success: '#67C23A'
  }
  return colorMap[type] || '#409EFF'
}

const getTypeLabel = (type) => {
  const labelMap = {
    violation: '违规',
    warning: '警告',
    info: '信息',
    success: '成功'
  }
  return labelMap[type] || '通知'
}

const markRead = async (notification) => {
  try {
    await notificationStore.markRead(notification.id)
    ElMessage.success('已标记为已读')
    await fetchNotifications()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const markAllRead = async () => {
  try {
    await notificationStore.markAllRead()
    ElMessage.success('全部已标记为已读')
    await fetchNotifications()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const deleteNotification = async (notification) => {
  try {
    await ElMessageBox.confirm('确定要删除该通知吗？', '提示', {
      type: 'warning'
    })
    await notificationStore.deleteNotification(notification.id)
    ElMessage.success('删除成功')
    await fetchNotifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const clearOld = async () => {
  try {
    await ElMessageBox.confirm('确定要清理30天前的已读通知吗？', '提示', {
      type: 'warning'
    })
    await notificationStore.clearOld(30)
    ElMessage.success('清理完成')
    await fetchNotifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const viewViolation = (notification) => {
  router.push({ name: 'Violations' })
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchNotifications()
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  page.value = 1
  fetchNotifications()
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-card {
  margin-bottom: 10px;
  transition: all 0.3s;
}

.notification-card.unread {
  border-left: 4px solid #409EFF;
  background-color: #f0f9ff;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.notification-title {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.notification-content {
  color: #606266;
  line-height: 1.6;
}

.notification-link {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #EBEEF5;
}
</style>
