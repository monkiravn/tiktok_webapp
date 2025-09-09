// Common types used across the application

export interface User {
  id: number
  username: string
  role: 'admin' | 'user'
  status: 'pending' | 'approved'
}

export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

export interface SidebarItem {
  id: string
  label: string
  icon: string
  path: string
}

export interface ToastMessage {
  title: string
  description?: string
  variant: 'success' | 'error' | 'warning' | 'info'
}

export interface VideoFile {
  id: number
  filename: string
  size: number
  status: 'processing' | 'processed' | 'failed'
  createdAt: string
}

export interface LiveStream {
  id: number
  username: string
  status: 'recording' | 'stopped'
  duration: number
  quality: '720p' | '1080p'
  fileSize: number
}
