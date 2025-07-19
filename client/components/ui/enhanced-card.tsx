/**
 * Enhanced Card Component
 * Production-ready card with comprehensive styling and interaction states
 */

import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const cardVariants = cva(
  [
    'rounded-lg border bg-card text-card-foreground',
    'transition-all duration-200',
  ],
  {
    variants: {
      variant: {
        default: [
          'border-border shadow-sm',
        ],
        elevated: [
          'border-border shadow-lg',
        ],
        interactive: [
          'border-border shadow-sm cursor-pointer',
          'hover:shadow-md hover:border-primary/20 hover:-translate-y-1',
          'active:translate-y-0 active:shadow-sm',
        ],
        outline: [
          'border-2 border-dashed border-border/50',
          'hover:border-border hover:bg-accent/5',
        ],
        glass: [
          'border-border/20 bg-background/80 backdrop-blur-sm',
          'shadow-xl',
        ],
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
      rounded: {
        none: 'rounded-none',
        sm: 'rounded-sm',
        md: 'rounded-md',
        lg: 'rounded-lg',
        xl: 'rounded-xl',
        '2xl': 'rounded-2xl',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'md',
      rounded: 'lg',
    },
  }
)

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, padding, rounded, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, padding, rounded }), className)}
      {...props}
    />
  )
)
Card.displayName = 'Card'

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { 
    spacing?: 'sm' | 'md' | 'lg'
  }
>(({ className, spacing = 'md', ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex flex-col space-y-1.5',
      {
        'p-3': spacing === 'sm',
        'p-6': spacing === 'md',
        'p-8': spacing === 'lg',
      },
      className
    )}
    {...props}
  />
))
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement> & {
    level?: 1 | 2 | 3 | 4 | 5 | 6
  }
>(({ className, level = 3, ...props }, ref) => {
  const Heading = `h${level}` as const
  
  const sizeClasses = {
    1: 'text-3xl font-bold',
    2: 'text-2xl font-semibold', 
    3: 'text-xl font-semibold',
    4: 'text-lg font-semibold',
    5: 'text-base font-semibold',
    6: 'text-sm font-semibold',
  }
  
  return (
    <Heading
      ref={ref}
      className={cn(
        'leading-none tracking-tight',
        sizeClasses[level],
        className
      )}
      {...props}
    />
  )
})
CardTitle.displayName = 'CardTitle'

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement> & {
    size?: 'sm' | 'md' | 'lg'
  }
>(({ className, size = 'sm', ...props }, ref) => (
  <p
    ref={ref}
    className={cn(
      'text-muted-foreground',
      {
        'text-sm': size === 'sm',
        'text-base': size === 'md', 
        'text-lg': size === 'lg',
      },
      className
    )}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    spacing?: 'sm' | 'md' | 'lg'
  }
>(({ className, spacing = 'md', ...props }, ref) => (
  <div 
    ref={ref} 
    className={cn(
      {
        'p-3 pt-0': spacing === 'sm',
        'p-6 pt-0': spacing === 'md',
        'p-8 pt-0': spacing === 'lg',
      },
      className
    )} 
    {...props} 
  />
))
CardContent.displayName = 'CardContent'

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    spacing?: 'sm' | 'md' | 'lg'
  }
>(({ className, spacing = 'md', ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center',
      {
        'p-3 pt-0': spacing === 'sm',
        'p-6 pt-0': spacing === 'md', 
        'p-8 pt-0': spacing === 'lg',
      },
      className
    )}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent,
  cardVariants
}