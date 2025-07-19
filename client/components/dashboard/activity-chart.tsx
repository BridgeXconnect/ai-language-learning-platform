"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Area, AreaChart } from "recharts"
import { cn } from "@/lib/utils"

interface ActivityChartProps {
  title?: string
  description?: string
  data: Array<{ name: string; value: number; [key: string]: any }>
  type?: "bar" | "line" | "area"
  className?: string
  height?: number
  style?: React.CSSProperties
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
        <p className="font-medium">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function ActivityChart({ 
  title = "Platform Activity", 
  description = "Recent activity overview",
  data, 
  type = "area",
  className,
  height = 300,
  style
}: ActivityChartProps) {
  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    }

    switch (type) {
      case "bar":
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="name" 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis className="text-xs" tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="value" 
              fill="hsl(var(--primary))"
              radius={[4, 4, 0, 0]}
              className="animate-fade-in"
            />
          </BarChart>
        )
      
      case "line":
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="name" 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis className="text-xs" tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="hsl(var(--primary))"
              strokeWidth={3}
              dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 4 }}
              className="animate-fade-in"
            />
          </LineChart>
        )
      
      case "area":
      default:
        return (
          <AreaChart {...commonProps}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="name" 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis className="text-xs" tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorValue)"
              className="animate-fade-in"
            />
          </AreaChart>
        )
    }
  }

  return (
    <Card className={cn("card-hover", className)} style={style}>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
        {description && (
          <CardDescription className="text-sm opacity-80">
            {description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="w-full" style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

// Sample data generator for demonstration
export const generateSampleData = (days: number = 7) => {
  const data = []
  const today = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    
    data.push({
      name: date.toLocaleDateString('en-US', { weekday: 'short' }),
      value: Math.floor(Math.random() * 100) + 20,
      date: date.toISOString().split('T')[0]
    })
  }
  
  return data
} 