"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { Button } from "@/components/ui/enhanced-button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { 
  Search,
  Filter,
  Upload,
  Download,
  FileText,
  Video,
  Image,
  Headphones,
  MoreHorizontal,
  Star,
  Eye,
  Edit3,
  Trash2,
  Copy,
  Tag,
  Calendar,
  TrendingUp,
  Archive,
  RefreshCw,
  FolderOpen,
  BookOpen,
  Users,
  BarChart3
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { format } from "date-fns"

interface ContentItem {
  id: string
  title: string
  type: 'sop' | 'template' | 'media' | 'exercise' | 'assessment'
  format: 'pdf' | 'docx' | 'pptx' | 'mp4' | 'mp3' | 'jpg' | 'png' | 'txt'
  size: string
  createdAt: string
  updatedAt: string
  tags: string[]
  usageCount: number
  qualityRating: number
  description: string
  category: string
  industry: string[]
  cefrLevel: string[]
  isPublic: boolean
  createdBy: string
  version: string
  downloadUrl?: string
}

interface ContentAnalytics {
  totalItems: number
  mostUsed: ContentItem[]
  recentUploads: ContentItem[]
  topCategories: { name: string, count: number }[]
  storageUsed: string
  totalDownloads: number
}

interface ContentLibraryProps {
  onItemSelect?: (item: ContentItem) => void
  selectionMode?: boolean
}

export function ContentLibrary({ onItemSelect, selectionMode = false }: ContentLibraryProps) {
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [analytics, setAnalytics] = useState<ContentAnalytics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterType, setFilterType] = useState("all")
  const [filterCategory, setFilterCategory] = useState("all")
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'usage' | 'rating'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [showUploadDialog, setShowUploadDialog] = useState(false)
  const { fetchWithAuth } = useAuth()

  useEffect(() => {
    const loadContentData = async () => {
      try {
        const [itemsResponse, analyticsResponse] = await Promise.all([
          fetchWithAuth('/api/content-library/items'),
          fetchWithAuth('/api/content-library/analytics')
        ])

        if (itemsResponse.ok && analyticsResponse.ok) {
          const itemsData = await itemsResponse.json()
          const analyticsData = await analyticsResponse.json()
          setContentItems(itemsData)
          setAnalytics(analyticsData)
        } else {
          // Mock data for development
          const mockItems: ContentItem[] = [
            {
              id: "1",
              title: "Business Communication SOP Template",
              type: "sop",
              format: "pdf",
              size: "2.3 MB",
              createdAt: "2025-01-10T10:00:00Z",
              updatedAt: "2025-01-12T14:30:00Z",
              tags: ["business", "communication", "template", "b2b"],
              usageCount: 45,
              qualityRating: 4.8,
              description: "Standard operating procedure template for business communication training",
              category: "Templates",
              industry: ["Technology", "Finance", "Manufacturing"],
              cefrLevel: ["B1", "B2"],
              isPublic: true,
              createdBy: "Course Manager",
              version: "2.1",
              downloadUrl: "/api/content/download/1"
            },
            {
              id: "2",
              title: "Technical Vocabulary Exercise Bank",
              type: "exercise",
              format: "docx",
              size: "1.8 MB",
              createdAt: "2025-01-08T16:20:00Z",
              updatedAt: "2025-01-08T16:20:00Z",
              tags: ["technical", "vocabulary", "exercises", "it"],
              usageCount: 32,
              qualityRating: 4.6,
              description: "Comprehensive collection of technical vocabulary exercises for IT professionals",
              category: "Exercises",
              industry: ["Technology"],
              cefrLevel: ["B1", "B2", "C1"],
              isPublic: true,
              createdBy: "Content Creator",
              version: "1.0"
            },
            {
              id: "3",
              title: "Client Presentation Video Guide",
              type: "media",
              format: "mp4",
              size: "45.2 MB",
              createdAt: "2025-01-05T09:15:00Z",
              updatedAt: "2025-01-05T09:15:00Z",
              tags: ["presentation", "client", "video", "sales"],
              usageCount: 28,
              qualityRating: 4.9,
              description: "Video guide demonstrating effective client presentation techniques",
              category: "Media",
              industry: ["Sales", "Consulting"],
              cefrLevel: ["B2", "C1"],
              isPublic: false,
              createdBy: "Training Specialist",
              version: "1.0"
            },
            {
              id: "4",
              title: "Manufacturing Safety Communication Protocols",
              type: "sop",
              format: "pdf",
              size: "3.1 MB",
              createdAt: "2025-01-03T11:45:00Z",
              updatedAt: "2025-01-07T13:20:00Z",
              tags: ["safety", "manufacturing", "communication", "protocols"],
              usageCount: 19,
              qualityRating: 4.7,
              description: "Safety communication protocols specific to manufacturing environments",
              category: "SOPs",
              industry: ["Manufacturing"],
              cefrLevel: ["A2", "B1"],
              isPublic: true,
              createdBy: "Safety Manager",
              version: "1.2"
            },
            {
              id: "5",
              title: "CEFR Assessment Template",
              type: "assessment",
              format: "pptx",
              size: "12.5 MB",
              createdAt: "2024-12-28T14:00:00Z",
              updatedAt: "2025-01-02T10:30:00Z",
              tags: ["assessment", "cefr", "evaluation", "template"],
              usageCount: 67,
              qualityRating: 4.9,
              description: "Comprehensive CEFR assessment template with scoring rubrics",
              category: "Assessments",
              industry: ["All"],
              cefrLevel: ["A1", "A2", "B1", "B2", "C1", "C2"],
              isPublic: true,
              createdBy: "Assessment Team",
              version: "3.0"
            }
          ]

          const mockAnalytics: ContentAnalytics = {
            totalItems: mockItems.length,
            mostUsed: mockItems.sort((a, b) => b.usageCount - a.usageCount).slice(0, 3),
            recentUploads: mockItems.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()).slice(0, 3),
            topCategories: [
              { name: "Templates", count: 15 },
              { name: "SOPs", count: 12 },
              { name: "Exercises", count: 10 },
              { name: "Media", count: 8 },
              { name: "Assessments", count: 6 }
            ],
            storageUsed: "2.8 GB",
            totalDownloads: 1247
          }

          setContentItems(mockItems)
          setAnalytics(mockAnalytics)
        }
      } catch (error) {
        console.error('Failed to load content library data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadContentData()
  }, [])

  const getFileIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case 'pdf':
      case 'docx':
      case 'txt':
        return <FileText className="h-5 w-5" />
      case 'mp4':
        return <Video className="h-5 w-5" />
      case 'mp3':
        return <Headphones className="h-5 w-5" />
      case 'jpg':
      case 'png':
        return <Image className="h-5 w-5" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'sop': return 'bg-blue-100 text-blue-700'
      case 'template': return 'bg-green-100 text-green-700'
      case 'media': return 'bg-purple-100 text-purple-700'
      case 'exercise': return 'bg-orange-100 text-orange-700'
      case 'assessment': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const filteredItems = contentItems
    .filter(item => {
      const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      const matchesType = filterType === "all" || item.type === filterType
      const matchesCategory = filterCategory === "all" || item.category === filterCategory
      return matchesSearch && matchesType && matchesCategory
    })
    .sort((a, b) => {
      let comparison = 0
      switch (sortBy) {
        case 'name':
          comparison = a.title.localeCompare(b.title)
          break
        case 'date':
          comparison = new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime()
          break
        case 'usage':
          comparison = a.usageCount - b.usageCount
          break
        case 'rating':
          comparison = a.qualityRating - b.qualityRating
          break
      }
      return sortOrder === 'desc' ? -comparison : comparison
    })

  const handleBulkAction = async (action: 'delete' | 'archive' | 'download') => {
    if (selectedItems.size === 0) return

    try {
      const response = await fetchWithAuth('/api/content-library/bulk-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          itemIds: Array.from(selectedItems)
        })
      })

      if (response.ok) {
        // Refresh content items
        setSelectedItems(new Set())
      }
    } catch (error) {
      console.error('Failed to perform bulk action:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Card key={i} variant="elevated" className="animate-pulse">
              <CardContent spacing="md">
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card variant="elevated">
            <CardContent spacing="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FolderOpen className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Items</p>
                  <p className="text-2xl font-bold">{analytics.totalItems}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent spacing="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Download className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Downloads</p>
                  <p className="text-2xl font-bold">{analytics.totalDownloads.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent spacing="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Archive className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Storage Used</p>
                  <p className="text-2xl font-bold">{analytics.storageUsed}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent spacing="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg Rating</p>
                  <p className="text-2xl font-bold">
                    {(contentItems.reduce((sum, item) => sum + item.qualityRating, 0) / contentItems.length).toFixed(1)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search content by title, tags, or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="flex gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Type: {filterType === "all" ? "All" : filterType}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setFilterType("all")}>All Types</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterType("sop")}>SOPs</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterType("template")}>Templates</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterType("media")}>Media</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterType("exercise")}>Exercises</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilterType("assessment")}>Assessments</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    Sort: {sortBy}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setSortBy("name")}>Name</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy("date")}>Date</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy("usage")}>Usage</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSortBy("rating")}>Rating</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <Button variant="outline" size="sm" onClick={() => setShowUploadDialog(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Upload
              </Button>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedItems.size > 0 && (
            <div className="flex items-center gap-2 mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <span className="text-sm font-medium text-blue-700">
                {selectedItems.size} item(s) selected
              </span>
              <Button size="xs" variant="outline" onClick={() => handleBulkAction('download')}>
                <Download className="h-3 w-3 mr-1" />
                Download
              </Button>
              <Button size="xs" variant="outline" onClick={() => handleBulkAction('archive')}>
                <Archive className="h-3 w-3 mr-1" />
                Archive
              </Button>
              <Button size="xs" variant="destructive" onClick={() => handleBulkAction('delete')}>
                <Trash2 className="h-3 w-3 mr-1" />
                Delete
              </Button>
              <Button size="xs" variant="ghost" onClick={() => setSelectedItems(new Set())}>
                Clear
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredItems.map((item) => (
          <Card key={item.id} variant="interactive" className="group hover:shadow-lg transition-all duration-200">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {selectionMode && (
                    <Checkbox
                      checked={selectedItems.has(item.id)}
                      onCheckedChange={(checked) => {
                        const newSelected = new Set(selectedItems)
                        if (checked) {
                          newSelected.add(item.id)
                        } else {
                          newSelected.delete(item.id)
                        }
                        setSelectedItems(newSelected)
                      }}
                    />
                  )}
                  <div className="text-blue-600">
                    {getFileIcon(item.format)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg leading-tight truncate">{item.title}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary" className={getTypeColor(item.type)}>
                        {item.type.toUpperCase()}
                      </Badge>
                      <span className="text-xs text-muted-foreground">v{item.version}</span>
                    </div>
                  </div>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="xs">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onItemSelect?.(item)}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Copy className="h-4 w-4 mr-2" />
                      Duplicate
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit3 className="h-4 w-4 mr-2" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-red-600">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>

            <CardContent spacing="md">
              <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{item.description}</p>
              
              <div className="space-y-3">
                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {item.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      <Tag className="h-3 w-3 mr-1" />
                      {tag}
                    </Badge>
                  ))}
                  {item.tags.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{item.tags.length - 3}
                    </Badge>
                  )}
                </div>

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-3 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    <span>{item.usageCount} uses</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                    <span>{item.qualityRating.toFixed(1)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    <span>{format(new Date(item.updatedAt), 'MMM d')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Archive className="h-3 w-3" />
                    <span>{item.size}</span>
                  </div>
                </div>

                {/* CEFR Levels */}
                <div className="flex items-center gap-1">
                  <span className="text-xs text-muted-foreground">CEFR:</span>
                  {item.cefrLevel.slice(0, 3).map((level) => (
                    <Badge key={level} variant="outline" className="text-xs">
                      {level}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredItems.length === 0 && (
        <Card variant="elevated">
          <CardContent spacing="lg" className="text-center py-16">
            <FolderOpen className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No content found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your search criteria or upload new content.
            </p>
            <Button onClick={() => setShowUploadDialog(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Upload Content
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload Content</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">Content upload functionality would be implemented here.</p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}