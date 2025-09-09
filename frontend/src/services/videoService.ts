import { api } from './api'
import type { VideoFile } from '../types'

export const videoService = {
  uploadVideo: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  getAllVideos: async (): Promise<VideoFile[]> => {
    const response = await api.get('/videos/')
    return response.data
  },

  deleteVideo: async (videoId: number) => {
    return api.delete(`/videos/${videoId}`)
  }
}
