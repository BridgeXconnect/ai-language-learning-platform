"use client"

import { useState } from "react"
import { DashboardCard } from "@/components/dashboard/dashboard-card"
import { Button } from "@/components/ui/button"
import { DollarSign, Users, FileText, TrendingUp, PlusCircle, ListChecks } from "lucide-react"
import Link from "next/link"
import { CourseRequestWizard } from "@/components/sales/course-request-wizard"
import { useAuth } from "@/contexts/auth-context"
import { useToast } from "@/hooks/use-toast"
import { useToastHelpers } from "@/components/ui/notification-toast"
import { ErrorBoundary } from "@/components/error-boundary"
import { CourseRequestStatus } from "@/components/sales/course-request-status"
import { salesService } from "@/lib/api-services"
import { AppError } from "@/lib/errors"

export default function SalesDashboardPage() {
  const [showWizard, setShowWizard] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSubmittedRequestId, setLastSubmittedRequestId] = useState<number | null>(null)
  const { fetchWithAuth } = useAuth()
  const { toast } = useToast()
  const { success, error, loading } = useToastHelpers()

  const handleWizardSubmit = async (data: any) => {
    if (isSubmitting) return
    
    setIsSubmitting(true)
    const loadingToast = loading("Submitting course request...", "Please wait while we process your request")
    
    try {
      // Extract SOP files from the data
      const { sopFiles, ...courseRequestData } = data
      
      console.log('📤 Submitting course request:', courseRequestData)
      
      // First, create the course request using authenticated API
      const courseRequest = await salesService.createCourseRequestFromWizard(courseRequestData)
      console.log('✅ Course request created successfully:', courseRequest)

      // Update loading toast
      loadingToast.update("Uploading documents...", "Processing SOP files")

      // Then upload SOP files if any exist
      if (sopFiles && sopFiles.length > 0) {
        await uploadSOPFiles(courseRequest.id, sopFiles)
      }

      // Success - dismiss loading and show success
      loadingToast.dismiss()
      success(
        "Course request submitted successfully",
        `Request #${courseRequest.id} has been created and is now under review.`
      )
      
      // Store the request ID for real-time tracking
      setLastSubmittedRequestId(courseRequest.id)
      setShowWizard(false)
      
    } catch (err: any) {
      console.error('❌ Error submitting course request:', err)
      
      loadingToast.dismiss()
      
      // Enhanced error handling based on error type
      if (err instanceof AppError) {
        switch (err.statusCode) {
          case 401:
            error("Authentication failed", "Please log in again and try submitting your request.")
            break
          case 403:
            error("Access denied", "You don't have permission to submit course requests.")
            break
          case 422:
            error("Invalid data", "Please check your form inputs and try again.")
            break
          case 500:
            error("Server error", "Our servers are experiencing issues. Please try again later.")
            break
          default:
            error("Submission failed", err.message || "An unexpected error occurred.")
        }
      } else if (err.name === 'NetworkError' || err.message.includes('fetch')) {
        error("Connection failed", "Please check your internet connection and try again.")
      } else {
        error("Unexpected error", err.message || "Something went wrong. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const uploadSOPFiles = async (requestId: number, files: File[]) => {
    console.log(`📎 Uploading ${files.length} SOP files for request #${requestId}`)
    
    const uploadPromises = files.map(async (file, index) => {
      try {
        console.log(`📎 Uploading file ${index + 1}/${files.length}: ${file.name}`)
        
        // Use the authenticated upload API with progress tracking
        const result = await salesService.uploadSOP(
          requestId.toString(),
          file,
          (progress) => {
            console.log(`📈 Upload progress for ${file.name}: ${progress}%`)
          }
        )
        
        console.log(`✅ SOP file ${file.name} uploaded successfully:`, result)
        return { success: true, file: file.name, result }
      } catch (err: any) {
        console.error(`❌ Error uploading ${file.name}:`, err)
        return { success: false, file: file.name, error: err }
      }
    })

    try {
      const results = await Promise.all(uploadPromises)
      const successful = results.filter(r => r.success)
      const failed = results.filter(r => !r.success)
      
      console.log(`📊 SOP upload results: ${successful.length} successful, ${failed.length} failed`)
      
      // Handle failed uploads
      if (failed.length > 0) {
        failed.forEach(({ file, error }) => {
          error(
            `Failed to upload ${file}`,
            error?.message || "File upload failed"
          )
        })
      }
      
      // Show success summary if any files uploaded
      if (successful.length > 0) {
        success(
          "Documents uploaded",
          `${successful.length} of ${files.length} files uploaded successfully.`
        )
      }
      
      // If all failed, throw error to be caught by parent
      if (failed.length === files.length) {
        throw new Error(`All ${files.length} file uploads failed`)
      }
      
    } catch (err) {
      console.error('❌ Critical error during SOP uploads:', err)
      throw err // Re-throw to be handled by parent
    }
  }

  return (
    <ErrorBoundary>
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Sales Dashboard</h1>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link href="/sales/requests">
              <ListChecks className="mr-2 h-4 w-4" /> View All Requests
            </Link>
          </Button>
          <Button onClick={() => setShowWizard(true)}>
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
        <div className="space-y-6">
          {/* Real-time Status Tracking */}
          {lastSubmittedRequestId && (
            <CourseRequestStatus
              requestId={lastSubmittedRequestId}
              showProgress={true}
              showConnection={true}
            />
          )}
          
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

      <CourseRequestWizard 
        open={showWizard} 
        onClose={() => setShowWizard(false)}
        onSubmit={handleWizardSubmit}
        isSubmitting={isSubmitting}
      />
      </div>
    </ErrorBoundary>
  )
}
