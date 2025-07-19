/**
 * Enhanced Button Component
 * Production-ready button with comprehensive variant system
 */

import React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

const buttonVariants = cva(
  // Base styles
  [
    'inline-flex items-center justify-center gap-2',
    'whitespace-nowrap rounded-md text-sm font-medium',
    'ring-offset-background transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'relative overflow-hidden',
  ],
  {
    variants: {
      variant: {
        default: [
          'bg-primary text-primary-foreground',
          'hover:bg-primary/90 hover:shadow-md hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-sm',
        ],
        destructive: [
          'bg-destructive text-destructive-foreground',
          'hover:bg-destructive/90 hover:shadow-md hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-sm',
        ],
        outline: [
          'border border-input bg-background',
          'hover:bg-accent hover:text-accent-foreground hover:border-primary/20',
          'hover:shadow-sm hover:-translate-y-0.5',
          'active:translate-y-0',
        ],
        secondary: [
          'bg-secondary text-secondary-foreground',
          'hover:bg-secondary/80 hover:shadow-sm hover:-translate-y-0.5',
          'active:translate-y-0',
        ],
        ghost: [
          'hover:bg-accent hover:text-accent-foreground',
          'hover:shadow-sm',
        ],
        link: [
          'text-primary underline-offset-4',
          'hover:underline hover:text-primary/80',
        ],
        success: [
          'bg-green-600 text-white',
          'hover:bg-green-700 hover:shadow-md hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-sm',
        ],
        warning: [
          'bg-yellow-600 text-white',
          'hover:bg-yellow-700 hover:shadow-md hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-sm',
        ],
        info: [
          'bg-blue-600 text-white',
          'hover:bg-blue-700 hover:shadow-md hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-sm',
        ],
      },
      size: {
        default: 'h-10 px-4 py-2',
        xs: 'h-7 rounded px-2 text-xs',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        xl: 'h-12 rounded-lg px-10 text-base',
        icon: 'h-10 w-10',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    fullWidth, 
    asChild = false, 
    loading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props 
  }, ref) => {
    const Comp = asChild ? Slot : 'button'
    
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {!loading && leftIcon && leftIcon}
        {children}
        {!loading && rightIcon && rightIcon}
      </Comp>
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }