"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { Button } from "@/components/ui/enhanced-button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { 
  Building2,
  Users,
  MapPin,
  Globe,
  Phone,
  Mail,
  DollarSign,
  Calendar,
  Save,
  RefreshCw,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  User,
  Briefcase,
  Factory,
  TrendingUp
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface CompanyDetails {
  name: string
  industry: string
  size: 'startup' | 'small' | 'medium' | 'large' | 'enterprise'
  location: string
  country: string
  website?: string
  description?: string
  revenue?: string
  employees?: number
  yearFounded?: number
}

interface ContactInformation {
  primaryContact: {
    name: string
    title: string
    email: string
    phone: string
    department: string
  }
  decisionMaker?: {
    name: string
    title: string
    email: string
    isContactSame: boolean
  }
  billingContact?: {
    name: string
    title: string
    email: string
    isContactSame: boolean
  }
}

interface TrainingBackground {
  currentPrograms: string[]
  previousProviders: string[]
  budget: string
  timeline: string
  successMetrics: string[]
  challenges: string[]
}

interface IndustryData {
  sector: string
  specializations: string[]
  certifications: string[]
  regulations: string[]
  communicationChannels: string[]
}

interface ClientInformation {
  companyDetails: CompanyDetails
  contactInformation: ContactInformation
  industrySpecifics: IndustryData
  trainingHistory: TrainingBackground
}

interface ClientInfoFormProps {
  initialData?: Partial<ClientInformation>
  onSave?: (data: ClientInformation) => void
  onCancel?: () => void
  isEditing?: boolean
  autoSave?: boolean
  autoSaveInterval?: number
}

const INDUSTRIES = [
  'Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail',
  'Education', 'Government', 'Non-profit', 'Energy', 'Transportation',
  'Real Estate', 'Media', 'Consulting', 'Legal', 'Hospitality'
]

const COMPANY_SIZES = [
  { value: 'startup', label: '1-10 employees', range: '1-10' },
  { value: 'small', label: '11-50 employees', range: '11-50' },
  { value: 'medium', label: '51-200 employees', range: '51-200' },
  { value: 'large', label: '201-1000 employees', range: '201-1000' },
  { value: 'enterprise', label: '1000+ employees', range: '1000+' }
]

export function ClientInfoForm({ 
  initialData, 
  onSave, 
  onCancel, 
  isEditing = false,
  autoSave = true,
  autoSaveInterval = 30000
}: ClientInfoFormProps) {
  const [formData, setFormData] = useState<ClientInformation>({
    companyDetails: {
      name: '',
      industry: '',
      size: 'medium',
      location: '',
      country: '',
      website: '',
      description: '',
      revenue: '',
      employees: undefined,
      yearFounded: undefined
    },
    contactInformation: {
      primaryContact: {
        name: '',
        title: '',
        email: '',
        phone: '',
        department: ''
      },
      decisionMaker: {
        name: '',
        title: '',
        email: '',
        isContactSame: true
      },
      billingContact: {
        name: '',
        title: '',
        email: '',
        isContactSame: true
      }
    },
    industrySpecifics: {
      sector: '',
      specializations: [],
      certifications: [],
      regulations: [],
      communicationChannels: []
    },
    trainingHistory: {
      currentPrograms: [],
      previousProviders: [],
      budget: '',
      timeline: '',
      successMetrics: [],
      challenges: []
    }
  })

  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [companyLookupData, setCompanyLookupData] = useState<any>(null)
  const { fetchWithAuth } = useAuth()

  // Initialize form with provided data
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({
        ...prev,
        ...initialData
      }))
    }
  }, [initialData])

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave || !hasChanges) return

    const autoSaveTimer = setTimeout(() => {
      handleAutoSave()
    }, autoSaveInterval)

    return () => clearTimeout(autoSaveTimer)
  }, [formData, hasChanges, autoSave, autoSaveInterval])

  const handleAutoSave = async () => {
    if (!hasChanges) return

    try {
      setIsSaving(true)
      // Save to local storage or API
      localStorage.setItem('clientInfo_draft', JSON.stringify(formData))
      setHasChanges(false)
    } catch (error) {
      console.error('Auto-save failed:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleCompanyLookup = async (companyName: string) => {
    if (!companyName || companyName.length < 3) return

    setIsLoading(true)
    try {
      // In a real implementation, this would call a company data API like Clearbit or ZoomInfo
      const response = await fetchWithAuth(`/api/company-lookup?name=${encodeURIComponent(companyName)}`)
      if (response.ok) {
        const data = await response.json()
        setCompanyLookupData(data)
        
        // Auto-fill form with company data
        if (data.company) {
          setFormData(prev => ({
            ...prev,
            companyDetails: {
              ...prev.companyDetails,
              name: data.company.name || prev.companyDetails.name,
              industry: data.company.industry || prev.companyDetails.industry,
              location: data.company.location || prev.companyDetails.location,
              website: data.company.website || prev.companyDetails.website,
              description: data.company.description || prev.companyDetails.description,
              employees: data.company.employees || prev.companyDetails.employees
            }
          }))
          setHasChanges(true)
        }
      }
    } catch (error) {
      console.error('Company lookup failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    // Required fields validation
    if (!formData.companyDetails.name.trim()) {
      errors.companyName = 'Company name is required'
    }
    if (!formData.companyDetails.industry) {
      errors.industry = 'Industry is required'
    }
    if (!formData.contactInformation.primaryContact.name.trim()) {
      errors.contactName = 'Primary contact name is required'
    }
    if (!formData.contactInformation.primaryContact.email.trim()) {
      errors.contactEmail = 'Primary contact email is required'
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (formData.contactInformation.primaryContact.email && 
        !emailRegex.test(formData.contactInformation.primaryContact.email)) {
      errors.contactEmail = 'Please enter a valid email address'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSaving(true)
    try {
      await onSave?.(formData)
      setHasChanges(false)
      // Clear draft from localStorage
      localStorage.removeItem('clientInfo_draft')
    } catch (error) {
      console.error('Failed to save client information:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const updateFormData = (path: string, value: any) => {
    setFormData(prev => {
      const keys = path.split('.')
      const updated = { ...prev }
      let current = updated as any
      
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] }
        current = current[keys[i]]
      }
      
      current[keys[keys.length - 1]] = value
      return updated
    })
    setHasChanges(true)
  }

  const addArrayItem = (path: string, item: string) => {
    setFormData(prev => {
      const keys = path.split('.')
      const updated = { ...prev }
      let current = updated as any
      
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] }
        current = current[keys[i]]
      }
      
      const currentArray = current[keys[keys.length - 1]] || []
      current[keys[keys.length - 1]] = [...currentArray, item]
      return updated
    })
    setHasChanges(true)
  }

  const removeArrayItem = (path: string, index: number) => {
    setFormData(prev => {
      const keys = path.split('.')
      const updated = { ...prev }
      let current = updated as any
      
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] }
        current = current[keys[i]]
      }
      
      const currentArray = current[keys[keys.length - 1]] || []
      current[keys[keys.length - 1]] = currentArray.filter((_: any, i: number) => i !== index)
      return updated
    })
    setHasChanges(true)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Form Header */}
      <Card variant="elevated">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Client Information</CardTitle>
              <p className="text-muted-foreground">
                Capture comprehensive client details for personalized course generation
              </p>
            </div>
            <div className="flex items-center gap-2">
              {hasChanges && (
                <Badge variant="outline" className="text-orange-600 bg-orange-50">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Unsaved changes
                </Badge>
              )}
              {isSaving && (
                <Badge variant="outline" className="text-blue-600 bg-blue-50">
                  <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                  Auto-saving...
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      <Tabs defaultValue="company" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="company" className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            Company
          </TabsTrigger>
          <TabsTrigger value="contact" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Contacts
          </TabsTrigger>
          <TabsTrigger value="industry" className="flex items-center gap-2">
            <Factory className="h-4 w-4" />
            Industry
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Training History
          </TabsTrigger>
        </TabsList>

        {/* Company Details Tab */}
        <TabsContent value="company">
          <Card variant="elevated">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Company Details
              </CardTitle>
            </CardHeader>
            <CardContent spacing="md">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Company Name *</label>
                  <div className="flex gap-2">
                    <Input
                      value={formData.companyDetails.name}
                      onChange={(e) => updateFormData('companyDetails.name', e.target.value)}
                      onBlur={() => handleCompanyLookup(formData.companyDetails.name)}
                      placeholder="Enter company name"
                      className={validationErrors.companyName ? 'border-red-500' : ''}
                    />
                    {isLoading && <RefreshCw className="h-8 w-8 p-2 animate-spin text-blue-600" />}
                  </div>
                  {validationErrors.companyName && (
                    <p className="text-sm text-red-600">{validationErrors.companyName}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Industry *</label>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="w-full justify-start">
                        {formData.companyDetails.industry || 'Select industry'}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-full">
                      {INDUSTRIES.map((industry) => (
                        <DropdownMenuItem 
                          key={industry} 
                          onClick={() => updateFormData('companyDetails.industry', industry)}
                        >
                          {industry}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                  {validationErrors.industry && (
                    <p className="text-sm text-red-600">{validationErrors.industry}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Company Size</label>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="w-full justify-start">
                        {COMPANY_SIZES.find(s => s.value === formData.companyDetails.size)?.label || 'Select size'}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-full">
                      {COMPANY_SIZES.map((size) => (
                        <DropdownMenuItem 
                          key={size.value} 
                          onClick={() => updateFormData('companyDetails.size', size.value)}
                        >
                          <div>
                            <div className="font-medium">{size.label}</div>
                            <div className="text-xs text-muted-foreground">{size.range} employees</div>
                          </div>
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Location</label>
                  <Input
                    value={formData.companyDetails.location}
                    onChange={(e) => updateFormData('companyDetails.location', e.target.value)}
                    placeholder="City, State/Province"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Country</label>
                  <Input
                    value={formData.companyDetails.country}
                    onChange={(e) => updateFormData('companyDetails.country', e.target.value)}
                    placeholder="Country"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Website</label>
                  <div className="flex gap-2">
                    <Input
                      value={formData.companyDetails.website}
                      onChange={(e) => updateFormData('companyDetails.website', e.target.value)}
                      placeholder="https://company.com"
                    />
                    {formData.companyDetails.website && (
                      <Button variant="outline" size="sm" asChild>
                        <a href={formData.companyDetails.website} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Number of Employees</label>
                  <Input
                    type="number"
                    value={formData.companyDetails.employees || ''}
                    onChange={(e) => updateFormData('companyDetails.employees', parseInt(e.target.value) || undefined)}
                    placeholder="e.g., 150"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Year Founded</label>
                  <Input
                    type="number"
                    value={formData.companyDetails.yearFounded || ''}
                    onChange={(e) => updateFormData('companyDetails.yearFounded', parseInt(e.target.value) || undefined)}
                    placeholder="e.g., 2010"
                  />
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <label className="text-sm font-medium">Company Description</label>
                <Textarea
                  value={formData.companyDetails.description}
                  onChange={(e) => updateFormData('companyDetails.description', e.target.value)}
                  placeholder="Brief description of the company's business, mission, and key activities..."
                  rows={4}
                />
              </div>

              {companyLookupData && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-700">Company data found and auto-filled</span>
                  </div>
                  <p className="text-xs text-green-600">
                    Some fields have been automatically populated. Please review and update as needed.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Contact Information Tab */}
        <TabsContent value="contact">
          <div className="space-y-6">
            {/* Primary Contact */}
            <Card variant="elevated">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Primary Contact
                </CardTitle>
              </CardHeader>
              <CardContent spacing="md">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Full Name *</label>
                    <Input
                      value={formData.contactInformation.primaryContact.name}
                      onChange={(e) => updateFormData('contactInformation.primaryContact.name', e.target.value)}
                      placeholder="John Smith"
                      className={validationErrors.contactName ? 'border-red-500' : ''}
                    />
                    {validationErrors.contactName && (
                      <p className="text-sm text-red-600">{validationErrors.contactName}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Job Title</label>
                    <Input
                      value={formData.contactInformation.primaryContact.title}
                      onChange={(e) => updateFormData('contactInformation.primaryContact.title', e.target.value)}
                      placeholder="HR Director"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Email Address *</label>
                    <Input
                      type="email"
                      value={formData.contactInformation.primaryContact.email}
                      onChange={(e) => updateFormData('contactInformation.primaryContact.email', e.target.value)}
                      placeholder="john.smith@company.com"
                      className={validationErrors.contactEmail ? 'border-red-500' : ''}
                    />
                    {validationErrors.contactEmail && (
                      <p className="text-sm text-red-600">{validationErrors.contactEmail}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Phone Number</label>
                    <Input
                      type="tel"
                      value={formData.contactInformation.primaryContact.phone}
                      onChange={(e) => updateFormData('contactInformation.primaryContact.phone', e.target.value)}
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium">Department</label>
                    <Input
                      value={formData.contactInformation.primaryContact.department}
                      onChange={(e) => updateFormData('contactInformation.primaryContact.department', e.target.value)}
                      placeholder="Human Resources"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Decision Maker */}
            <Card variant="elevated">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  Decision Maker
                </CardTitle>
              </CardHeader>
              <CardContent spacing="md">
                <div className="space-y-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.contactInformation.decisionMaker?.isContactSame}
                      onChange={(e) => updateFormData('contactInformation.decisionMaker.isContactSame', e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-sm">Same as primary contact</span>
                  </label>

                  {!formData.contactInformation.decisionMaker?.isContactSame && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Full Name</label>
                        <Input
                          value={formData.contactInformation.decisionMaker?.name || ''}
                          onChange={(e) => updateFormData('contactInformation.decisionMaker.name', e.target.value)}
                          placeholder="Jane Doe"
                        />
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Job Title</label>
                        <Input
                          value={formData.contactInformation.decisionMaker?.title || ''}
                          onChange={(e) => updateFormData('contactInformation.decisionMaker.title', e.target.value)}
                          placeholder="Chief Learning Officer"
                        />
                      </div>

                      <div className="space-y-2 md:col-span-2">
                        <label className="text-sm font-medium">Email Address</label>
                        <Input
                          type="email"
                          value={formData.contactInformation.decisionMaker?.email || ''}
                          onChange={(e) => updateFormData('contactInformation.decisionMaker.email', e.target.value)}
                          placeholder="jane.doe@company.com"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Industry Specifics Tab */}
        <TabsContent value="industry">
          <Card variant="elevated">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Factory className="h-5 w-5" />
                Industry Specifics
              </CardTitle>
            </CardHeader>
            <CardContent spacing="md">
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Business Sector</label>
                  <Input
                    value={formData.industrySpecifics.sector}
                    onChange={(e) => updateFormData('industrySpecifics.sector', e.target.value)}
                    placeholder="e.g., Software Development, Financial Services, Manufacturing"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Specializations</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.industrySpecifics.specializations.map((spec, index) => (
                      <Badge key={index} variant="secondary">
                        {spec}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('industrySpecifics.specializations', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add specialization and press Enter"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          const value = (e.target as HTMLInputElement).value.trim()
                          if (value) {
                            addArrayItem('industrySpecifics.specializations', value)
                            ;(e.target as HTMLInputElement).value = ''
                          }
                        }
                      }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Required Certifications</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.industrySpecifics.certifications.map((cert, index) => (
                      <Badge key={index} variant="secondary">
                        {cert}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('industrySpecifics.certifications', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add certification and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const value = (e.target as HTMLInputElement).value.trim()
                        if (value) {
                          addArrayItem('industrySpecifics.certifications', value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Compliance Requirements</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.industrySpecifics.regulations.map((reg, index) => (
                      <Badge key={index} variant="secondary">
                        {reg}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('industrySpecifics.regulations', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add regulation/compliance requirement and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const value = (e.target as HTMLInputElement).value.trim()
                        if (value) {
                          addArrayItem('industrySpecifics.regulations', value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }
                    }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Training History Tab */}
        <TabsContent value="history">
          <Card variant="elevated">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Training History & Requirements
              </CardTitle>
            </CardHeader>
            <CardContent spacing="md">
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Budget Range</label>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" className="w-full justify-start">
                          <DollarSign className="h-4 w-4 mr-2" />
                          {formData.trainingHistory.budget || 'Select budget range'}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent className="w-full">
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.budget', 'Under $5,000')}>
                          Under $5,000
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.budget', '$5,000 - $15,000')}>
                          $5,000 - $15,000
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.budget', '$15,000 - $50,000')}>
                          $15,000 - $50,000
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.budget', '$50,000 - $100,000')}>
                          $50,000 - $100,000
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.budget', 'Over $100,000')}>
                          Over $100,000
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Timeline</label>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" className="w-full justify-start">
                          <Calendar className="h-4 w-4 mr-2" />
                          {formData.trainingHistory.timeline || 'Select timeline'}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent className="w-full">
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.timeline', 'Urgent (1-2 weeks)')}>
                          Urgent (1-2 weeks)
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.timeline', 'Soon (1 month)')}>
                          Soon (1 month)
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.timeline', 'Standard (2-3 months)')}>
                          Standard (2-3 months)
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => updateFormData('trainingHistory.timeline', 'Flexible (3+ months)')}>
                          Flexible (3+ months)
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Training Programs</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.trainingHistory.currentPrograms.map((program, index) => (
                      <Badge key={index} variant="secondary">
                        {program}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('trainingHistory.currentPrograms', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add current training program and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const value = (e.target as HTMLInputElement).value.trim()
                        if (value) {
                          addArrayItem('trainingHistory.currentPrograms', value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Previous Training Providers</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.trainingHistory.previousProviders.map((provider, index) => (
                      <Badge key={index} variant="secondary">
                        {provider}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('trainingHistory.previousProviders', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add previous provider and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const value = (e.target as HTMLInputElement).value.trim()
                        if (value) {
                          addArrayItem('trainingHistory.previousProviders', value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Success Metrics</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.trainingHistory.successMetrics.map((metric, index) => (
                      <Badge key={index} variant="secondary">
                        {metric}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('trainingHistory.successMetrics', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add success metric and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const value = (e.target as HTMLInputElement).value.trim()
                        if (value) {
                          addArrayItem('trainingHistory.successMetrics', value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Training Challenges</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.trainingHistory.challenges.map((challenge, index) => (
                      <Badge key={index} variant="secondary">
                        {challenge}
                        <button
                          type="button"
                          onClick={() => removeArrayItem('trainingHistory.challenges', index)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Add training challenge and press Enter"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const value = (e.target as HTMLInputElement).value.trim()
                        if (value) {
                          addArrayItem('trainingHistory.challenges', value)
                          ;(e.target as HTMLInputElement).value = ''
                        }
                      }
                    }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Form Actions */}
      <Card variant="elevated">
        <CardContent spacing="md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              {hasChanges && (
                <>
                  <AlertCircle className="h-4 w-4" />
                  <span>You have unsaved changes</span>
                </>
              )}
              {!hasChanges && (
                <>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>All changes saved</span>
                </>
              )}
            </div>
            
            <div className="flex gap-3">
              {onCancel && (
                <Button type="button" variant="outline" onClick={onCancel}>
                  Cancel
                </Button>
              )}
              <Button type="submit" loading={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                {isEditing ? 'Update Information' : 'Save Information'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </form>
  )
}