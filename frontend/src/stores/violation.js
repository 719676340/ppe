// frontend/src/stores/violation.js
import { defineStore } from 'pinia'
import { violationApi } from '../api/violation'

export const useViolationStore = defineStore('violation', {
  state: () => ({
    violations: [],
    total: 0,
    currentViolation: null,
    loading: false,
    filters: {
      camera_id: null,
      zone_id: null,
      start_time: null,
      end_time: null,
      is_processed: null,
      page: 1,
      page_size: 20
    }
  }),

  actions: {
    async fetchViolations(filters = {}) {
      this.loading = true
      try {
        const params = { ...this.filters, ...filters }
        const result = await violationApi.getList(params)
        this.violations = result.items
        this.total = result.total
        this.filters = params
      } finally {
        this.loading = false
      }
    },

    async fetchViolation(id) {
      this.loading = true
      try {
        this.currentViolation = await violationApi.getDetail(id)
      } finally {
        this.loading = false
      }
    },

    async updateRemark(id, remark) {
      await violationApi.updateRemark(id, remark)
      await this.fetchViolations()
    },

    async markProcessed(id) {
      await violationApi.markProcessed(id)
      await this.fetchViolations()
    },

    async batchMarkProcessed(ids) {
      await violationApi.batchMarkProcessed(ids)
      await this.fetchViolations()
    },

    async deleteViolation(id) {
      await violationApi.delete(id)
      await this.fetchViolations()
    },

    async exportViolations(params = {}) {
      return await violationApi.export(params)
    }
  }
})
