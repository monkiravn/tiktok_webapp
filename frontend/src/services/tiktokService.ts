import { api } from './api'
import type { LiveStream } from '../types'

export const tiktokService = {
  startRecording: async (username: string, quality: '720p' | '1080p' = '720p') => {
    return api.post('/tiktok/start-recording', { username, quality })
  },

  stopRecording: async (streamId: number) => {
    return api.post(`/tiktok/stop-recording/${streamId}`)
  },

  getActiveStreams: async (): Promise<LiveStream[]> => {
    const response = await api.get('/tiktok/active-streams')
    return response.data
  },

  addUserToMonitor: async (username: string) => {
    return api.post('/tiktok/monitor-user', { username })
  },

  getMonitoredUsers: async () => {
    const response = await api.get('/tiktok/monitored-users')
    return response.data
  }
}
