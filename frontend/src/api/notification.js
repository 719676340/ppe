// frontend/src/api/notification.js
import request from './index'

export const notificationApi = {
  // 获取通知列表
  getList(params) {
    return request.get('/notifications', { params })
  },

  // 获取未读数量
  getUnreadCount() {
    return request.get('/notifications/unread-count')
  },

  // 创建通知
  create(data) {
    return request.post('/notifications', data)
  },

  // 标记为已读
  markRead(id) {
    return request.patch(`/notifications/${id}/read`)
  },

  // 全部标记为已读
  markAllRead() {
    return request.post('/notifications/mark-all-read')
  },

  // 删除通知
  delete(id) {
    return request.delete(`/notifications/${id}`)
  },

  // 清理旧通知
  clearOld(days = 30) {
    return request.delete('/notifications/old', { params: { days } })
  }
}
