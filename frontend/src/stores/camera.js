// frontend/src/stores/camera.js
import { defineStore } from 'pinia'
import { cameraApi } from '../api/camera'

export const useCameraStore = defineStore('camera', {
  state: () => ({
    cameras: [],
    currentCamera: null,
    loading: false
  }),

  actions: {
    async fetchCameras() {
      this.loading = true
      try {
        this.cameras = await cameraApi.getList()
      } finally {
        this.loading = false
      }
    },

    async fetchCamera(id) {
      this.loading = true
      try {
        this.currentCamera = await cameraApi.getDetail(id)
      } finally {
        this.loading = false
      }
    },

    async createCamera(data) {
      await cameraApi.create(data)
      await this.fetchCameras()
    },

    async updateCamera(id, data) {
      await cameraApi.update(id, data)
      await this.fetchCameras()
    },

    async deleteCamera(id) {
      await cameraApi.delete(id)
      await this.fetchCameras()
    },

    async testConnection(data) {
      return await cameraApi.testConnection(data)
    }
  }
})
