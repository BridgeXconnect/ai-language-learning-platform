"use client"
import { useAuth } from "@/contexts/auth-context"
import { DashboardCard } from "@/components/dashboard/dashboard-card"
import { ActivityChart, generateSampleData } from "@/components/dashboard/activity-chart"
import { BarChart, BookOpen, Users, TrendingUp, Bot, Sparkles, Target, Award } from "lucide-react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export default function OverviewPage() {
  const { user } = useAuth()
  const activityData = generateSampleData(7)

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Enhanced Hero Section */}
      <div className="relative overflow-hidden rounded-xl gradient-hero text-primary-foreground shadow-2xl">
        <div className="absolute inset-0 bg-black/20" />
        <div className="relative p-8 md:p-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-white/20 backdrop-blur-sm">
              <Sparkles className="h-6 w-6" />
            </div>
            <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
              AI-Powered Learning
            </Badge>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-3">
            Welcome back, {user?.first_name || user?.username || "User"}! 👋
          </h1>
          <p className="text-xl opacity-90 mb-6 max-w-2xl">
            Your AI Language Learning Platform is running smoothly. Here's what's happening today.
          </p>
          <div className="flex flex-wrap gap-4">
            <Button variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
              View Analytics
            </Button>
            <Button variant="outline" className="bg-transparent border-white/30 text-white hover:bg-white/20">
              Create Course
            </Button>
          </div>
        </div>
      </div>

      {/* Enhanced Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <DashboardCard
          title="Total Courses"
          value="12"
          icon={BookOpen}
          description="Active and archived courses"
          variant="default"
          trend={{ value: 8, isPositive: true, label: "vs last month" }}
          className="animate-slide-up"
        />
        <DashboardCard
          title="Active Students"
          value="150"
          icon={Users}
          description="Currently enrolled learners"
          variant="success"
          trend={{ value: 12, isPositive: true, label: "new this week" }}
          className="animate-slide-up"
          style={{ animationDelay: "0.1s" }}
        />
        <DashboardCard
          title="Completion Rate"
          value="72%"
          icon={Target}
          description="Average across all courses"
          variant="warning"
          trend={{ value: 5, isPositive: true, label: "vs last month" }}
          className="animate-slide-up"
          style={{ animationDelay: "0.2s" }}
        />
        <DashboardCard
          title="AI Generations"
          value="3 New"
          icon={Bot}
          description="Courses generated this month"
          variant="ai"
          trend={{ value: 15, isPositive: true, label: "vs last month" }}
          className="animate-slide-up"
          style={{ animationDelay: "0.3s" }}
        />
      </div>

      {/* Enhanced Charts Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ActivityChart
          title="Platform Activity"
          description="Student engagement over the last 7 days"
          data={activityData}
          type="area"
          height={300}
          className="animate-slide-up"
          style={{ animationDelay: "0.4s" }}
        />
        
        <DashboardCard 
          title="Recent Achievements" 
          variant="gradient"
          className="animate-slide-up"
          style={{ animationDelay: "0.5s" }}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-background/50">
              <div className="p-2 rounded-full bg-success/20">
                <Award className="h-4 w-4 text-success" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-sm">Course Creation Master</p>
                <p className="text-xs text-muted-foreground">Created 5 courses this month</p>
              </div>
              <Badge variant="outline" className="text-xs">New</Badge>
            </div>
            
            <div className="flex items-center gap-3 p-3 rounded-lg bg-background/50">
              <div className="p-2 rounded-full bg-primary/20">
                <TrendingUp className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-sm">Engagement Leader</p>
                <p className="text-xs text-muted-foreground">95% student satisfaction rate</p>
              </div>
              <Badge variant="outline" className="text-xs">Achieved</Badge>
            </div>
            
            <div className="flex items-center gap-3 p-3 rounded-lg bg-background/50">
              <div className="p-2 rounded-full bg-[hsl(var(--ai-purple))]/20">
                <Bot className="h-4 w-4 text-[hsl(var(--ai-purple))]" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-sm">AI Pioneer</p>
                <p className="text-xs text-muted-foreground">Generated 10 AI-powered lessons</p>
              </div>
              <Badge variant="outline" className="text-xs">In Progress</Badge>
            </div>
          </div>
        </DashboardCard>
      </div>

      {/* Quick Actions Section */}
      <DashboardCard 
        title="Quick Actions" 
        variant="default"
        className="animate-slide-up"
        style={{ animationDelay: "0.6s" }}
      >
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Button 
            variant="outline" 
            className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-primary/5 transition-colors"
            asChild
          >
            <a href="/sales">
              <BarChart className="h-6 w-6" />
              <span className="font-medium">Sales Pipeline</span>
              <span className="text-xs text-muted-foreground">View opportunities</span>
            </a>
          </Button>
          
          <Button 
            variant="outline" 
            className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-primary/5 transition-colors"
            asChild
          >
            <a href="/course-manager">
              <BookOpen className="h-6 w-6" />
              <span className="font-medium">Manage Courses</span>
              <span className="text-xs text-muted-foreground">Edit & organize</span>
            </a>
          </Button>
          
          <Button 
            variant="outline" 
            className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-primary/5 transition-colors"
            asChild
          >
            <a href="/content-library">
              <Sparkles className="h-6 w-6" />
              <span className="font-medium">Content Library</span>
              <span className="text-xs text-muted-foreground">Browse resources</span>
            </a>
          </Button>
          
          <Button 
            variant="outline" 
            className="h-auto p-4 flex flex-col items-center gap-2 hover:bg-primary/5 transition-colors"
            asChild
          >
            <a href="/settings">
              <Users className="h-6 w-6" />
              <span className="font-medium">Profile Settings</span>
              <span className="text-xs text-muted-foreground">Update preferences</span>
            </a>
          </Button>
        </div>
      </DashboardCard>

      {/* Design Inspiration Section */}
      <DashboardCard 
        title="Design Inspiration" 
        variant="default"
        className="overflow-hidden animate-slide-up"
        style={{ animationDelay: "0.7s" }}
      >
        <p className="text-sm text-muted-foreground px-6 pt-0 pb-4">
          Reference design for future enhancements and improvements.
        </p>
        <div className="relative">
          <Image
            src="/images/dashboard-inspiration.png"
            alt="Dashboard design inspiration"
            width={1200}
            height={800}
            className="w-full h-auto object-cover rounded-lg"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
        </div>
      </DashboardCard>
    </div>
  )
}
