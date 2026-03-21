// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/detection'
  },
  {
    path: '/detection',
    name: 'Detection',
    component: () => import('../views/DetectionView.vue'),
    meta: { title: '检测演示' }
  },
  {
    path: '/cameras',
    name: 'Cameras',
    component: () => import('../views/CamerasView.vue'),
    meta: { title: '摄像头管理' }
  },
  {
    path: '/zones',
    name: 'Zones',
    component: () => import('../views/ZonesView.vue'),
    meta: { title: '区域管理' }
  },
  {
    path: '/violations',
    name: 'Violations',
    component: () => import('../views/ViolationsView.vue'),
    meta: { title: '违规记录' }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/StatisticsView.vue'),
    meta: { title: '统计分析' }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('../views/NotificationsView.vue'),
    meta: { title: '通知中心' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
