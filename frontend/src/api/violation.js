// frontend/src/api/violation.js
import request from './index'

export const violationApi = {
  // 获取违规记录列表
  getList(params) {
    return request.get('/violations', { params })
  },

  // 获取单个违规记录
  getDetail(id) {
    return request.get(`/violations/${id}`)
  },

  // 更新备注
  updateRemark(id, remark) {
    return request.patch(`/violations/${id}/remark`, null, {
      params: { remark }
    })
  },

  // 标记为已处理
  markProcessed(id) {
    return request.patch(`/violations/${id}/process`)
  },

  // 批量标记为已处理
  batchMarkProcessed(ids) {
    return request.post('/violations/batch-process', ids)
  },

  // 删除违规记录
  delete(id) {
    return request.delete(`/violations/${id}`)
  }
}
