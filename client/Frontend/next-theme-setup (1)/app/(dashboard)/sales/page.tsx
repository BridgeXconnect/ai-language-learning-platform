"use client"

import { DashboardCard } from "@/components/dashboard/dashboard-card"
import { Button } from "@/components/ui/button"
import { DollarSign, Users, FileText, TrendingUp, PlusCircle, ListChecks } from "lucide-react"
import Link from "next/link"
// Placeholder for actual components
// import { SalesPipelineMetrics } from "@/components/dashboard/sales/sales-pipeline-metrics";
// import { SalesRequestsTable } from "@/components/dashboard/sales/sales-requests-table";
// import { NewCourseRequestWizard } from "@/components/dashboard/sales/new-course-request-wizard";

export default function SalesDashboardPage() {
  // const [showWizard, setShowWizard] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Sales Dashboard</h1>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link href="/sales/requests">
              <ListChecks className="mr-2 h-4 w-4" /> View All Requests
            </Link>
          </Button>
          <Button onClick={() => alert("Open New Course Request Wizard from main dashboard") /*setShowWizard(true)*/}>
            <PlusCircle className="mr-2 h-4 w-4" /> New Course Request
          </Button>
        </div>
      </div>

      {/* Inspired by screenshot's top row stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <DashboardCard
          title="Active Leads"
          value="78"
          icon={Users}
          description="+15% from last month"
          valueClassName="text-primary"
        />
        <DashboardCard title="Proposals Sent" value="56" icon={FileText} description="+5 from last week" />
        <DashboardCard
          title="Deals Closed (MTD)"
          value="$12,350"
          icon={DollarSign}
          description="Target: $20,000"
          valueClassName="text-success-foreground bg-success p-1 rounded-md inline-block"
          className="bg-success/10"
        />
        <DashboardCard
          title="Conversion Rate"
          value="23%"
          icon={TrendingUp}
          description="Average: 18%"
          valueClassName="text-warning-foreground bg-warning p-1 rounded-md inline-block"
          className="bg-warning/10"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DashboardCard title="Course Request Pipeline">
            {/* Placeholder for SalesPipelineMetrics chart */}
            <div className="h-80 flex items-center justify-center text-muted-foreground bg-slate-50 dark:bg-slate-800 rounded-md">
              Sales Pipeline Chart Area
            </div>
          </DashboardCard>
        </div>
        <div>
          <DashboardCard title="Recent Activity">
            <ul className="space-y-2 text-sm">
              <li>Followed up with Client X</li>
              <li>New SOP uploaded for Acme Corp</li>
              <li>Proposal sent to Globex Inc.</li>
              <li>Demo scheduled with Initech</li>
            </ul>
          </DashboardCard>
        </div>
      </div>

      <DashboardCard title="All Course Requests">
        {/* Placeholder for SalesRequestsTable */}
        <div className="h-96 flex items-center justify-center text-muted-foreground bg-slate-50 dark:bg-slate-800 rounded-md">
          Course Requests Table Area
        </div>
      </DashboardCard>

      {/* {showWizard && <NewCourseRequestWizard onClose={() => setShowWizard(false)} />} */}
    </div>
  )
}
