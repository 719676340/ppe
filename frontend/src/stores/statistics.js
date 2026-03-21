// frontend/src/stores/statistics.js
import { defineStore } from 'pinia'
import { statisticsApi } from '../api/statistics'

export const useStatisticsStore = defineStore('statistics', {
  state: () => ({
    overview: null,
    zoneStats: [],
    periodStats: [],
    cameraStats: [],
    trendStats: null,
    loading: false
  }),

  actions: {
    async fetchOverview() {
      this.loading = true
      try {
        this.overview = await statisticsApi.getOverview()
      } finally {
        this.loading = false
      }
    },

    async fetchZoneStats(startTime, endTime) {
      this.loading = true
      try {
        this.zoneStats = await statisticsApi.getZoneStats({
          start_time: startTime,
          end_time: endTime
        })
      } finally {
        this.loading = false
      }
    },

    async fetchPeriodStats(startTime, endTime) {
      this.loading = true
      try {
        this.periodStats = await statisticsApi.getPeriodStats({
          start_time: startTime,
          end_time: endTime
        })
      } finally {
        this.loading = false
      }
    },

    async fetchCameraStats(startTime, endTime) {
      this.loading = true
      try {
        this.cameraStats = await statisticsApi.getCameraStats({
          start_time: startTime,
          end_time: endTime
        })
      } finally {
        this.loading = false
      }
    },

    async fetchTrendStats(startTime, endTime, groupBy = 'day') {
      this.loading = true
      try {
        this.trendStats = await statisticsApi.getTrendStats({
          start_time: startTime,
          end_time: endTime,
          group_by: groupBy
        })
      } finally {
        this.loading = false
      }
    }
  }
})
