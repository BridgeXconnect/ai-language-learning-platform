"use client"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { PlusCircle, ListFilter, Download } from "lucide-react"
import { NewCourseRequestWizard } from "@/components/dashboard/sales/new-course-request-wizard"
import type { CourseRequest, ColumnDefinition } from "@/lib/types"
import { CourseRequestStatus } from "@/lib/types"
import { useAuth } from "@/contexts/auth-context"
import { DataTable } from "@/components/shared/data-table" // We'll create this next
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { format } from "date-fns"

// Mock data for now
const mockCourseRequests: CourseRequest[] = [
  {
    id: "req_1",
    clientDetails: { companyName: "Acme Corp", contactPerson: "John Doe", email: "john@acme.com" },
    sopFiles: [{ id: "sop_1", name: "Acme_SOP_v1.pdf", url: "/sops/Acme_SOP_v1.pdf" }],
    status: CourseRequestStatus.SUBMITTED,
    requestedBy: "user_sales_1",
    requestedByName: "Alice Smith",
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: "req_2",
    clientDetails: { companyName: "Globex Inc.", contactPerson: "Jane Roe", email: "jane@globex.com" },
    sopFiles: [
      { id: "sop_2a", name: "Globex_Onboarding.docx", url: "/sops/Globex_Onboarding.docx" },
      { id: "sop_2b", name: "Globex_Sales_Playbook.pdf", url: "/sops/Globex_Sales_Playbook.pdf" },
    ],
    status: CourseRequestStatus.UNDER_REVIEW,
    requestedBy: "user_sales_2",
    requestedByName: "Bob Johnson",
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
  },
  {
    id: "req_3",
    clientDetails: { companyName: "Initech", contactPerson: "Peter Gibbons", email: "peter@initech.com" },
    sopFiles: [{ id: "sop_3", name: "TPS_Reports_Guide.pdf", url: "/sops/TPS_Reports_Guide.pdf" }],
    status: CourseRequestStatus.APPROVED,
    requestedBy: "user_sales_1",
    requestedByName: "Alice Smith",
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
]

const getStatusBadgeVariant = (status: CourseRequestStatus) => {
  switch (status) {
    case CourseRequestStatus.SUBMITTED:
    case CourseRequestStatus.UNDER_REVIEW:
      return "secondary"
    case CourseRequestStatus.APPROVED:
    case CourseRequestStatus.COMPLETED:
      return "success"
    case CourseRequestStatus.REJECTED:
      return "destructive"
    case CourseRequestStatus.GENERATION_IN_PROGRESS:
      return "default" // Or a specific "info" or "primary" variant
    case CourseRequestStatus.DRAFT:
      return "outline"
    default:
      return "secondary"
  }
}

const columns: ColumnDefinition<CourseRequest>[] = [
  {
    accessorKey: "clientDetails.companyName",
    header: "Company",
    cell: ({ row }) => row.clientDetails.companyName,
  },
  {
    accessorKey: "clientDetails.contactPerson",
    header: "Contact",
    cell: ({ row }) => row.clientDetails.contactPerson,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <Badge variant={getStatusBadgeVariant(row.status)} className="capitalize">
        {row.status.replace(/_/g, " ")}
      </Badge>
    ),
    enableSorting: true,
  },
  {
    accessorKey: "sopFiles",
    header: "SOPs",
    cell: ({ row }) => row.sopFiles.length,
  },
  {
    accessorKey: "requestedByName",
    header: "Requested By",
    cell: ({ row }) => row.requestedByName || row.requestedBy,
  },
  {
    accessorKey: "createdAt",
    header: "Date Submitted",
    cell: ({ row }) => format(new Date(row.createdAt), "MMM d, yyyy"),
    enableSorting: true,
  },
  {
    accessorKey: "actions",
    header: "Actions",
    cell: ({ row }) => (
      <Button variant="outline" size="sm" onClick={() => alert(`View details for ${row.id}`)}>
        View
      </Button>
    ),
  },
]

export default function SalesRequestsPage() {
  const [isWizardOpen, setIsWizardOpen] = useState(false)
  const [courseRequests, setCourseRequests] = useState<CourseRequest[]>(mockCourseRequests) // Initialize with mock
  const [isLoading, setIsLoading] = useState(true) // Set to true initially
  const { fetchWithAuth } = useAuth()

  const fetchCourseRequests = async () => {
    setIsLoading(true)
    try {
      // const response = await fetchWithAuth(`${API_BASE_URL}/sales/course-requests`);
      // if (!response.ok) throw new Error("Failed to fetch course requests");
      // const data = await response.json();
      // setCourseRequests(data);

      // Simulate API call with mock data
      await new Promise((resolve) => setTimeout(resolve, 500))
      setCourseRequests(mockCourseRequests)
    } catch (error) {
      console.error("Error fetching course requests:", error)
      // Handle error (e.g., show toast)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCourseRequests()
  }, [])

  const handleNewRequestSuccess = (newRequest: CourseRequest) => {
    // setCourseRequests((prev) => [newRequest, ...prev]); // Add to top
    fetchCourseRequests() // Or refetch the list
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Course Requests</h1>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <ListFilter className="mr-2 h-4 w-4" /> Filter Status
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Filter by Status</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {Object.values(CourseRequestStatus).map((status) => (
                <DropdownMenuCheckboxItem key={status} /* checked={...} onCheckedChange={...} */>
                  {status.replace(/_/g, " ")}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
          <Button onClick={() => setIsWizardOpen(true)}>
            <PlusCircle className="mr-2 h-4 w-4" /> New Request
          </Button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={courseRequests}
        isLoading={isLoading}
        searchColumn="clientDetails.companyName" // Example: search by company name
        searchPlaceholder="Search by company..."
      />

      <NewCourseRequestWizard
        isOpen={isWizardOpen}
        onOpenChange={setIsWizardOpen}
        onSuccess={handleNewRequestSuccess}
      />
    </div>
  )
}
