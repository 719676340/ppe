// frontend/src/api/zone.js
import request from './index'

export const zoneApi = {
  // 获取区域列表
  getList(params) {
    return request.get('/zones', { params })
  },

  // 获取单个区域
  getDetail(id) {
    return request.get(`/zones/${id}`)
  },

  // 创建区域
  create(data) {
    return request.post('/zones', data)
  },

  // 更新区域
  update(id, data) {
    return request.put(`/zones/${id}`, data)
  },

  // 删除区域
  delete(id) {
    return request.delete(`/zones/${id}`)
  }
}
