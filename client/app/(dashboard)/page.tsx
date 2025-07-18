"use client"
import { useAuth } from "@/contexts/auth-context"
import { DashboardCard } from "@/components/dashboard/dashboard-card"
import { BarChart, BookOpen, Users, TrendingUp } from "lucide-react"
import Image from "next/image"

export default function OverviewPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="p-8 rounded-lg bg-gradient-to-br from-primary/80 via-primary to-indigo-700 text-primary-foreground shadow-lg">
        <h1 className="text-4xl font-bold">Welcome back, {user?.first_name || user?.username || "User"}!</h1>
        <p className="text-lg mt-2 opacity-90">Here&apos;s what&apos;s happening with your English courses today.</p>
      </div>

      {/* Inspired by screenshot's layout */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <DashboardCard
          title="Total Courses"
          value="12"
          icon={BookOpen}
          description="Active and archived"
          className="xl:col-span-1"
        />
        <DashboardCard
          title="Active Students"
          value="150"
          icon={Users}
          description="+5 new this week"
          className="xl:col-span-1"
        />
        <DashboardCard
          title="Completion Rate"
          value="72%"
          icon={TrendingUp}
          description="Across all courses"
          className="xl:col-span-1"
        />
        <DashboardCard
          title="AI Generations"
          value="3 New"
          icon={BarChart} // Using BarChart as a placeholder for AI/Bot icon
          description="Courses generated this month"
          className="xl:col-span-1"
        />

        <DashboardCard title="Platform Activity Overview" className="lg:col-span-2 xl:col-span-2">
          <div className="h-64 flex items-center justify-center text-muted-foreground bg-slate-50 dark:bg-slate-800 rounded-md">
            Platform Activity Chart Area
          </div>
        </DashboardCard>

        <DashboardCard title="Quick Links" className="lg:col-span-1 xl:col-span-2">
          <ul className="space-y-2 text-primary underline">
            <li>
              <a href="/sales">View Sales Pipeline</a>
            </li>
            <li>
              <a href="/course-manager">Manage Courses</a>
            </li>
            <li>
              <a href="/content-library">Browse Content Library</a>
            </li>
            <li>
              <a href="/settings">Update Your Profile</a>
            </li>
          </ul>
        </DashboardCard>
      </div>

      {/* Example of using the uploaded image for inspiration */}
      <DashboardCard title="Design Inspiration (Screenshot)" className="overflow-hidden">
        <p className="text-sm text-muted-foreground px-6 pt-0 pb-2">
          This is how the provided screenshot could inspire card layouts.
        </p>
        <Image
          src="/images/dashboard-inspiration.png"
          alt="Dashboard design inspiration"
          width={1200}
          height={800}
          className="w-full h-auto object-cover"
        />
      </DashboardCard>
    </div>
  )
}
