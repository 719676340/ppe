// frontend/src/api/detection.js
import request from './index'

export const detectionApi = {
  // 启动检测
  start(cameraId) {
    return request.post(`/detection/start/${cameraId}`)
  },

  // 停止检测
  stop(cameraId) {
    return request.post(`/detection/stop/${cameraId}`)
  },

  // 获取检测状态
  getStatus() {
    return request.get('/detection/status')
  },

  // 获取视频流地址（返回MJPEG流URL）
  // 注意：MJPEG流需要直接访问，不通过axios
  getStreamUrl(cameraId) {
    // 在开发环境中，通过Vite代理访问
    return `/api/detection/stream/${cameraId}`
  }
}
