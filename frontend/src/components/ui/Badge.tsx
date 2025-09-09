import { HTMLAttributes } from 'react'
import { cn } from '../../utils/utils'

type Variant = 'default' | 'green' | 'blue' | 'yellow' | 'purple' | 'neutral' | 'red'

interface Props extends HTMLAttributes<HTMLSpanElement> {
  variant?: Variant
}

const styles: Record<Variant, string> = {
  default: 'bg-neutral-700 text-neutral-100',
  green: 'bg-green-600 text-white',
  blue: 'bg-blue-600 text-white',
  yellow: 'bg-yellow-600 text-white',
  purple: 'bg-purple-600 text-white',
  neutral: 'bg-neutral-700 text-neutral-100',
  red: 'bg-red-600 text-white',
}

export default function Badge({ className, variant = 'default', ...props }: Props) {
  return (
    <span
      className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', styles[variant], className)}
      {...props}
    />
  )
}
