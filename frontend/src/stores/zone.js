// frontend/src/stores/zone.js
import { defineStore } from 'pinia'
import { zoneApi } from '../api/zone'

export const useZoneStore = defineStore('zone', {
  state: () => ({
    zones: [],
    currentZone: null,
    loading: false
  }),

  actions: {
    async fetchZones(cameraId) {
      this.loading = true
      try {
        const params = cameraId ? { camera_id: cameraId } : {}
        this.zones = await zoneApi.getList(params)
      } finally {
        this.loading = false
      }
    },

    async fetchZone(id) {
      this.loading = true
      try {
        this.currentZone = await zoneApi.getDetail(id)
      } finally {
        this.loading = false
      }
    },

    async createZone(data) {
      await zoneApi.create(data)
      await this.fetchZones()
    },

    async updateZone(id, data) {
      await zoneApi.update(id, data)
      await this.fetchZones()
    },

    async deleteZone(id) {
      await zoneApi.delete(id)
      await this.fetchZones()
    }
  }
})
