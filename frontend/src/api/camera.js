// frontend/src/api/camera.js
import request from './index'

export const cameraApi = {
  // 获取摄像头列表
  getList(params) {
    return request.get('/cameras', { params })
  },

  // 获取单个摄像头
  getDetail(id) {
    return request.get(`/cameras/${id}`)
  },

  // 创建摄像头
  create(data) {
    return request.post('/cameras', data)
  },

  // 更新摄像头
  update(id, data) {
    return request.put(`/cameras/${id}`, data)
  },

  // 删除摄像头
  delete(id) {
    return request.delete(`/cameras/${id}`)
  },

  // 测试连接
  testConnection(data) {
    return request.post('/cameras/test', data)
  },

  // 启动检测
  startDetection(id) {
    return request.post(`/detection/start/${id}`)
  },

  // 停止检测
  stopDetection(id) {
    return request.post(`/detection/stop/${id}`)
  },

  // 获取检测状态
  getDetectionStatus() {
    return request.get('/detection/status')
  }
}
