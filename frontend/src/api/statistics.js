// frontend/src/api/statistics.js
import request from './index'

export const statisticsApi = {
  // 获取统计概览
  getOverview() {
    return request.get('/statistics/overview')
  },

  // 获取区域统计
  getZoneStats(params) {
    return request.get('/statistics/zone', { params })
  },

  // 获取时段统计
  getPeriodStats(params) {
    return request.get('/statistics/period', { params })
  },

  // 获取摄像头统计
  getCameraStats(params) {
    return request.get('/statistics/camera', { params })
  },

  // 获取趋势统计
  getTrendStats(params) {
    return request.get('/statistics/trend', { params })
  }
}
