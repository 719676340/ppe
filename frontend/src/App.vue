<!-- frontend/src/App.vue -->
<template>
  <el-config-provider :locale="locale">
    <div id="app">
      <el-container style="height: 100vh">
        <!-- 侧边栏 -->
        <el-aside width="200px" style="background-color: #304156">
          <div style="height: 60px; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; font-weight: bold;">
            头盔检测系统
          </div>
          <el-menu
            :default-active="activeMenu"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
          >
            <el-menu-item index="/detection">
              <el-icon><VideoCamera /></el-icon>
              <span>检测演示</span>
            </el-menu-item>
            <el-menu-item index="/cameras">
              <el-icon><Camera /></el-icon>
              <span>摄像头管理</span>
            </el-menu-item>
            <el-menu-item index="/zones">
              <el-icon><Location /></el-icon>
              <span>区域管理</span>
            </el-menu-item>
            <el-menu-item index="/violations">
              <el-icon><Document /></el-icon>
              <span>违规记录</span>
            </el-menu-item>
            <el-menu-item index="/statistics">
              <el-icon><DataAnalysis /></el-icon>
              <span>统计分析</span>
            </el-menu-item>
            <el-menu-item index="/notifications">
              <el-icon><Bell /></el-icon>
              <span>通知中心</span>
              <el-badge
                v-if="unreadCount > 0"
                :value="unreadCount"
                class="notification-badge"
              />
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-container>
          <el-header style="background-color: #fff; box-shadow: 0 1px 4px rgba(0,21,41,.08); display: flex; align-items: center; justify-content: space-between;">
            <div style="font-size: 16px; font-weight: 500;">
              {{ pageTitle }}
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
              <el-button @click="fetchNotifications" :icon="Bell" circle />
              <el-dropdown>
                <div style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                  <el-avatar :size="32" icon="User" />
                  <span>管理员</span>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item>个人中心</el-dropdown-item>
                    <el-dropdown-item divided>退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-header>

          <el-main style="background-color: #f0f2f5; padding: 20px;">
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useNotificationStore } from './stores/notification'

const route = useRoute()
const notificationStore = useNotificationStore()

const locale = zhCn
const activeMenu = ref('/')
const unreadCount = ref(0)

const pageTitle = computed(() => {
  const titles = {
    '/detection': '检测演示',
    '/cameras': '摄像头管理',
    '/zones': '区域管理',
    '/violations': '违规记录',
    '/statistics': '统计分析',
    '/notifications': '通知中心'
  }
  return titles[route.path] || '头盔检测系统'
})

watch(() => route.path, (newPath) => {
  activeMenu.value = newPath
}, { immediate: true })

const fetchNotifications = async () => {
  await notificationStore.fetchUnreadCount()
  unreadCount.value = notificationStore.unreadCount
}

onMounted(() => {
  fetchNotifications()
  // 定时刷新未读数
  setInterval(fetchNotifications, 30000)
})
</script>

<style scoped>
.notification-badge {
  margin-left: auto;
}

#app {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

:deep(.el-main) {
  overflow-y: auto;
}
</style>
