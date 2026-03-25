// frontend/src/stores/notification.js
import { defineStore } from 'pinia'
import { notificationApi } from '../api/notification'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [],
    total: 0,
    unreadCount: 0,
    loading: false
  }),

  actions: {
    async fetchNotifications({ unreadOnly = false, skip = 0, limit = 20 } = {}) {
      this.loading = true
      try {
        const result = await notificationApi.getList({
          unread_only: unreadOnly,
          skip,
          limit
        })
        this.notifications = result.items
        this.total = result.total
        this.unreadCount = result.unread_count
      } finally {
        this.loading = false
      }
    },

    async fetchUnreadCount() {
      try {
        const result = await notificationApi.getUnreadCount()
        this.unreadCount = result.count
      } catch (error) {
        console.error('Failed to fetch unread count:', error)
      }
    },

    async markRead(id) {
      await notificationApi.markRead(id)
      await this.fetchNotifications({})
    },

    async markAllRead() {
      await notificationApi.markAllRead()
      await this.fetchNotifications({})
    },

    async deleteNotification(id) {
      await notificationApi.delete(id)
      await this.fetchNotifications({})
    },

    async clearOld(days = 30) {
      await notificationApi.clearOld(days)
      await this.fetchNotifications({})
    }
  }
})
