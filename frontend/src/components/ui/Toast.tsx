import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { cn } from '../../utils/utils'

type ToastVariant = 'default' | 'success' | 'error' | 'warning' | 'info'

export type ToastItem = {
  id: string
  title?: string
  description?: string
  variant?: ToastVariant
}

type ToastContextType = {
  toasts: ToastItem[]
  addToast: (item: Omit<ToastItem, 'id'> & { timeoutMs?: number }) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((t) => t.filter((x) => x.id !== id))
  }, [])

  const addToast = useCallback(
    ({ title, description, variant = 'default', timeoutMs = 3500 }: Omit<ToastItem, 'id'> & { timeoutMs?: number }) => {
      const id = Math.random().toString(36).slice(2)
      setToasts((t) => [...t, { id, title, description, variant }])
      if (timeoutMs > 0) {
        setTimeout(() => removeToast(id), timeoutMs)
      }
    },
    [removeToast]
  )

  const value = useMemo(() => ({ toasts, addToast, removeToast }), [toasts, addToast, removeToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onClose={removeToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

function ToastViewport({ toasts, onClose }: { toasts: ToastItem[]; onClose: (id: string) => void }) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col items-end gap-2">
      {toasts.map((t) => (
        <Toast key={t.id} item={t} onClose={() => onClose(t.id)} />
      ))}
    </div>
  )
}

function Toast({ item, onClose }: { item: ToastItem; onClose: () => void }) {
  const { title, description, variant = 'default' } = item
  const style = variantStyles[variant]
  return (
    <div className={cn('w-80 rounded-lg border p-3 shadow-lg transition-all', style.container)}>
      <div className="flex items-start gap-2">
        <div className={cn('mt-1 h-2 w-2 shrink-0 rounded-full', style.dot)} />
        <div className="flex-1">
          {title && <div className="text-sm font-semibold leading-5">{title}</div>}
          {description && <div className="mt-0.5 text-sm text-neutral-300 leading-5">{description}</div>}
        </div>
        <button onClick={onClose} className="ml-2 rounded-md p-1 text-neutral-300 hover:text-white hover:bg-neutral-700">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
  )
}

const variantStyles: Record<ToastVariant, { container: string; dot: string }> = {
  default: {
    container: 'bg-neutral-900 border-neutral-800 text-neutral-100',
    dot: 'bg-neutral-500',
  },
  success: {
    container: 'bg-neutral-900 border-green-700 text-neutral-100',
    dot: 'bg-green-500',
  },
  error: {
    container: 'bg-neutral-900 border-red-700 text-neutral-100',
    dot: 'bg-red-500',
  },
  warning: {
    container: 'bg-neutral-900 border-yellow-700 text-neutral-100',
    dot: 'bg-yellow-500',
  },
  info: {
    container: 'bg-neutral-900 border-blue-700 text-neutral-100',
    dot: 'bg-blue-500',
  },
}
