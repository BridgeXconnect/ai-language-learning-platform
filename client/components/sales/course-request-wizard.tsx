/**
 * Course Request Wizard Component
 * Multi-step form for capturing comprehensive client information and training needs
 */

"use client"

import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/enhanced-button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Progress } from '@/components/ui/progress'
import { LoadingSpinner, LoadingOverlay } from '@/components/ui/progress-indicator'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/enhanced-card'
import { 
  Building2, 
  Users, 
  MapPin, 
  DollarSign, 
  Calendar, 
  Target, 
  FileText, 
  Upload,
  CheckCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  RefreshCw
} from 'lucide-react'
import { cn } from '@/lib/utils'

// Form validation schemas
const clientInfoSchema = z.object({
  companyName: z.string().min(2, 'Company name must be at least 2 characters'),
  industry: z.string().min(1, 'Please select an industry'),
  companySize: z.string().min(1, 'Please select company size'),
  location: z.string().min(2, 'Location is required'),
  website: z.string().url('Please enter a valid website URL').optional().or(z.literal('')),
  contactPerson: z.string().min(2, 'Contact person name is required'),
  contactEmail: z.string().email('Please enter a valid email address'),
  contactPhone: z.string().min(10, 'Please enter a valid phone number'),
  decisionMaker: z.string().min(2, 'Decision maker name is required'),
  decisionMakerRole: z.string().min(2, 'Decision maker role is required'),
})

const projectInfoSchema = z.object({
  projectTitle: z.string().min(5, 'Project title must be at least 5 characters'),
  projectDescription: z.string().min(20, 'Please provide a detailed description'),
  estimatedBudget: z.string().min(1, 'Please select a budget range'),
  timeline: z.string().min(1, 'Please select a timeline'),
  urgency: z.string().min(1, 'Please select urgency level'),
  hasExistingTraining: z.boolean(),
  existingTrainingDescription: z.string().optional(),
})

const trainingNeedsSchema = z.object({
  currentEnglishLevel: z.string().min(1, 'Please select current English level'),
  targetEnglishLevel: z.string().min(1, 'Please select target English level'),
  participantCount: z.number().min(1, 'Must have at least 1 participant'),
  targetRoles: z.array(z.string()).min(1, 'Please select at least one target role'),
  communicationScenarios: z.array(z.string()).min(1, 'Please select at least one scenario'),
  trainingGoals: z.string().min(20, 'Please describe training goals in detail'),
  specificChallenges: z.string().min(10, 'Please describe specific challenges'),
  successMetrics: z.string().min(10, 'Please describe how success will be measured'),
})

type ClientInfo = z.infer<typeof clientInfoSchema>
type ProjectInfo = z.infer<typeof projectInfoSchema>
type TrainingNeeds = z.infer<typeof trainingNeedsSchema>

interface CourseRequestWizardProps {
  open: boolean
  onClose: () => void
  onSubmit?: (data: ClientInfo & ProjectInfo & TrainingNeeds) => void
  isSubmitting?: boolean
}

const INDUSTRIES = [
  'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail',
  'Education', 'Government', 'Energy', 'Transportation', 'Real Estate',
  'Consulting', 'Media', 'Non-Profit', 'Other'
]

const COMPANY_SIZES = [
  '1-10 employees', '11-50 employees', '51-200 employees', 
  '201-500 employees', '501-1000 employees', '1000+ employees'
]

const BUDGET_RANGES = [
  'Under $5,000', '$5,000 - $15,000', '$15,000 - $30,000',
  '$30,000 - $50,000', '$50,000 - $100,000', '$100,000+'
]

const TIMELINES = [
  'ASAP (Within 2 weeks)', '1 month', '2-3 months', 
  '3-6 months', '6+ months', 'Flexible'
]

const URGENCY_LEVELS = [
  { value: 'low', label: 'Low - Planning ahead', description: 'No immediate deadline' },
  { value: 'medium', label: 'Medium - Standard timeline', description: 'Normal business priority' },
  { value: 'high', label: 'High - Time sensitive', description: 'Important business need' },
  { value: 'critical', label: 'Critical - Urgent', description: 'Immediate business impact' }
]

const ENGLISH_LEVELS = [
  { value: 'A1', label: 'A1 - Beginner', description: 'Basic words and phrases' },
  { value: 'A2', label: 'A2 - Elementary', description: 'Simple conversations' },
  { value: 'B1', label: 'B1 - Intermediate', description: 'Work-related discussions' },
  { value: 'B2', label: 'B2 - Upper Intermediate', description: 'Complex topics, presentations' },
  { value: 'C1', label: 'C1 - Advanced', description: 'Fluent professional communication' },
  { value: 'C2', label: 'C2 - Proficient', description: 'Native-level fluency' }
]

const TARGET_ROLES = [
  'Customer Service Representatives', 'Sales Teams', 'Technical Support',
  'Project Managers', 'Team Leaders', 'C-Level Executives',
  'Engineers', 'Consultants', 'Administrative Staff', 'All Employees'
]

const COMMUNICATION_SCENARIOS = [
  'Email Communication', 'Phone Calls & Video Meetings', 'Client Presentations',
  'Team Meetings', 'Technical Discussions', 'Customer Support',
  'Sales & Negotiations', 'Project Reporting', 'Documentation Writing',
  'Cross-cultural Communication'
]

export function CourseRequestWizard({ open, onClose, onSubmit, isSubmitting = false }: CourseRequestWizardProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [clientInfo, setClientInfo] = useState<ClientInfo | null>(null)
  const [projectInfo, setProjectInfo] = useState<ProjectInfo | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [isValidating, setIsValidating] = useState(false)
  const [stepErrors, setStepErrors] = useState<Record<number, string | null>>({})

  // Form instances for each step
  const clientForm = useForm<ClientInfo>({
    resolver: zodResolver(clientInfoSchema),
    mode: 'onBlur'
  })

  const projectForm = useForm<ProjectInfo>({
    resolver: zodResolver(projectInfoSchema),
    mode: 'onBlur'
  })

  const trainingForm = useForm<TrainingNeeds>({
    resolver: zodResolver(trainingNeedsSchema),
    mode: 'onBlur',
    defaultValues: {
      participantCount: 1,
      targetRoles: [],
      communicationScenarios: []
    }
  })

  // Auto-save functionality
  useEffect(() => {
    const interval = setInterval(() => {
      // Save form data to localStorage
      const formData = {
        step: currentStep,
        clientInfo: clientForm.getValues(),
        projectInfo: projectForm.getValues(),
        trainingNeeds: trainingForm.getValues()
      }
      localStorage.setItem('courseRequestDraft', JSON.stringify(formData))
    }, 10000) // Save every 10 seconds

    return () => clearInterval(interval)
  }, [currentStep, clientForm, projectForm, trainingForm])

  // Load saved data on mount
  useEffect(() => {
    const savedData = localStorage.getItem('courseRequestDraft')
    if (savedData) {
      try {
        const data = JSON.parse(savedData)
        if (data.clientInfo) clientForm.reset(data.clientInfo)
        if (data.projectInfo) projectForm.reset(data.projectInfo)
        if (data.trainingNeeds) trainingForm.reset(data.trainingNeeds)
      } catch (error) {
        console.error('Error loading saved form data:', error)
      }
    }
  }, [clientForm, projectForm, trainingForm])

  const steps = [
    { 
      id: 1, 
      title: 'Client Information', 
      description: 'Company details and contacts',
      icon: Building2
    },
    { 
      id: 2, 
      title: 'Project Details', 
      description: 'Budget, timeline, and scope',
      icon: Target
    },
    { 
      id: 3, 
      title: 'Training Needs', 
      description: 'Skills assessment and goals',
      icon: Users
    },
    { 
      id: 4, 
      title: 'SOP Upload', 
      description: 'Standard Operating Procedures',
      icon: FileText
    },
    { 
      id: 5, 
      title: 'Review & Submit', 
      description: 'Confirm and submit request',
      icon: CheckCircle
    }
  ]

  const progress = (currentStep / steps.length) * 100

  const handleNext = async () => {
    setIsValidating(true)
    setStepErrors({ ...stepErrors, [currentStep]: null })
    
    try {
      let isValid = false

      switch (currentStep) {
        case 1:
          isValid = await clientForm.trigger()
          if (isValid) {
            setClientInfo(clientForm.getValues())
          } else {
            setStepErrors({ ...stepErrors, [currentStep]: "Please complete all required fields" })
          }
          break
        case 2:
          isValid = await projectForm.trigger()
          if (isValid) {
            setProjectInfo(projectForm.getValues())
          } else {
            setStepErrors({ ...stepErrors, [currentStep]: "Please complete all required fields" })
          }
          break
        case 3:
          isValid = await trainingForm.trigger()
          if (!isValid) {
            setStepErrors({ ...stepErrors, [currentStep]: "Please complete all required fields" })
          }
          break
        default:
          isValid = true
      }

      // Add a small delay to show loading state
      await new Promise(resolve => setTimeout(resolve, 500))

      if (isValid && currentStep < steps.length) {
        setCurrentStep(currentStep + 1)
      }
    } finally {
      setIsValidating(false)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    const isValid = await trainingForm.trigger()
    if (!isValid) return

    if (isSubmitting) return // Prevent double submission
    
    try {
      const trainingNeeds = trainingForm.getValues()
      
      const submissionData = {
        // Client Information
        company_name: clientInfo!.companyName,
        industry: clientInfo!.industry,
        company_size: clientInfo!.companySize,
        location: clientInfo!.location,
        website: clientInfo!.website || '',
        
        // Contact Information
        contact_person: clientInfo!.contactPerson,
        contact_email: clientInfo!.contactEmail,
        contact_phone: clientInfo!.contactPhone,
        decision_maker: clientInfo!.decisionMaker,
        decision_maker_role: clientInfo!.decisionMakerRole,
        
        // Project Information
        project_title: projectInfo!.projectTitle,
        project_description: projectInfo!.projectDescription,
        estimated_budget: projectInfo!.estimatedBudget,
        timeline: projectInfo!.timeline,
        urgency: projectInfo!.urgency,
        has_existing_training: projectInfo!.hasExistingTraining,
        existing_training_description: projectInfo!.existingTrainingDescription || '',
        
        // Training Requirements
        participant_count: trainingNeeds.participantCount,
        current_english_level: trainingNeeds.currentEnglishLevel,
        target_english_level: trainingNeeds.targetEnglishLevel,
        target_roles: trainingNeeds.targetRoles,
        communication_scenarios: trainingNeeds.communicationScenarios,
        training_goals: trainingNeeds.trainingGoals,
        specific_challenges: trainingNeeds.specificChallenges,
        success_metrics: trainingNeeds.successMetrics,
        
        // SOP Files (to be uploaded separately)
        sopFiles: uploadedFiles
      }
      
      // Helper to convert snake_case keys to camelCase
      function toCamelCase(obj: any): any {
        if (Array.isArray(obj)) {
          return obj.map(toCamelCase)
        } else if (obj && typeof obj === 'object') {
          return Object.keys(obj).reduce((acc, key) => {
            const camelKey = key.replace(/_([a-z])/g, g => g[1].toUpperCase())
            acc[camelKey] = toCamelCase(obj[key])
            return acc
          }, {} as any)
        }
        return obj
      }

      if (onSubmit) {
        await onSubmit(toCamelCase(submissionData))
      }

      // Clear saved draft only on successful submission
      localStorage.removeItem('courseRequestDraft')
      
    } catch (error) {
      console.error('Error in wizard submission:', error)
      // Error handling is now done in the parent component
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <ClientInfoStep form={clientForm} />
      case 2:
        return <ProjectInfoStep form={projectForm} />
      case 3:
        return <TrainingNeedsStep form={trainingForm} />
      case 4:
        return <SOPUploadStep uploadedFiles={uploadedFiles} setUploadedFiles={setUploadedFiles} />
      case 5:
        return <ReviewStep 
          clientInfo={clientInfo} 
          projectInfo={projectInfo} 
          trainingNeeds={trainingForm.getValues()} 
        />
      default:
        return null
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="h-6 w-6 text-primary" />
            New Course Request
          </DialogTitle>
          <DialogDescription>
            Create a customized English training program tailored to your company's needs
          </DialogDescription>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Step {currentStep} of {steps.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <Progress value={progress} className="w-full" />
        </div>

        {/* Step Navigation */}
        <div className="flex items-center justify-between mb-6">
          {steps.map((step, index) => {
            const StepIcon = step.icon
            const isActive = step.id === currentStep
            const isCompleted = step.id < currentStep
            
            return (
              <div 
                key={step.id} 
                className={cn(
                  "flex flex-col items-center space-y-2 relative flex-1",
                  index < steps.length - 1 && "after:absolute after:top-6 after:left-1/2 after:w-full after:h-0.5 after:bg-border after:z-0"
                )}
              >
                <div className={cn(
                  "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 relative z-10",
                  isActive && "bg-primary text-primary-foreground shadow-lg",
                  isCompleted && "bg-green-500 text-white",
                  !isActive && !isCompleted && "bg-muted text-muted-foreground"
                )}>
                  {isCompleted ? (
                    <CheckCircle className="h-6 w-6" />
                  ) : (
                    <StepIcon className="h-6 w-6" />
                  )}
                </div>
                <div className="text-center">
                  <div className={cn(
                    "text-sm font-medium",
                    isActive && "text-primary",
                    isCompleted && "text-green-600"
                  )}>
                    {step.title}
                  </div>
                  <div className="text-xs text-muted-foreground hidden md:block">
                    {step.description}
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Step Content */}
        <div className="min-h-[400px] relative">
          {renderStepContent()}
          
          {/* Loading Overlay */}
          {(isValidating || isSubmitting) && (
            <LoadingOverlay 
              message={isSubmitting ? "Submitting your request..." : "Validating form..."}
              description={isSubmitting ? "Please wait while we process your course request" : "Checking form data"}
            />
          )}
          
          {/* Step Error */}
          {stepErrors[currentStep] && (
            <div className="absolute bottom-4 left-4 right-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center gap-2 text-red-800">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm font-medium">{stepErrors[currentStep]}</span>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-6 border-t">
          <Button 
            variant="outline" 
            onClick={handlePrevious}
            disabled={currentStep === 1 || isValidating || isSubmitting}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>

          <div className="text-sm text-muted-foreground flex items-center gap-2">
            <span>Auto-saved</span>
            <CheckCircle className="h-3 w-3 text-green-500" />
            {(isValidating || isSubmitting) && (
              <>
                <span>•</span>
                <LoadingSpinner size="sm" />
              </>
            )}
          </div>

          {currentStep < steps.length ? (
            <Button 
              onClick={handleNext}
              disabled={isValidating || isSubmitting}
            >
              {isValidating ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Validating...
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          ) : (
            <Button 
              onClick={handleSubmit}
              disabled={isValidating || isSubmitting}
              variant="default"
              className="bg-green-600 hover:bg-green-700 text-white disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Submit Request
                </>
              )}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Step Components
function ClientInfoStep({ form }: { form: any }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Company Information
          </CardTitle>
          <CardDescription>
            Tell us about your organization
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="companyName">Company Name *</Label>
              <Input
                id="companyName"
                placeholder="Enter company name"
                {...form.register('companyName')}
              />
              {form.formState.errors.companyName && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.companyName.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">Industry *</Label>
              <Select onValueChange={(value) => form.setValue('industry', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  {INDUSTRIES.map((industry) => (
                    <SelectItem key={industry} value={industry}>
                      {industry}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {form.formState.errors.industry && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.industry.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="companySize">Company Size *</Label>
              <Select onValueChange={(value) => form.setValue('companySize', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select company size" />
                </SelectTrigger>
                <SelectContent>
                  {COMPANY_SIZES.map((size) => (
                    <SelectItem key={size} value={size}>
                      {size}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {form.formState.errors.companySize && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.companySize.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location *</Label>
              <Input
                id="location"
                placeholder="City, Country"
                {...form.register('location')}
              />
              {form.formState.errors.location && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.location.message}
                </p>
              )}
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="website">Company Website</Label>
              <Input
                id="website"
                type="url"
                placeholder="https://www.company.com"
                {...form.register('website')}
              />
              {form.formState.errors.website && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.website.message}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Contact Information
          </CardTitle>
          <CardDescription>
            Primary contacts for this project
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contactPerson">Contact Person *</Label>
              <Input
                id="contactPerson"
                placeholder="Full name"
                {...form.register('contactPerson')}
              />
              {form.formState.errors.contactPerson && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.contactPerson.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="contactEmail">Email Address *</Label>
              <Input
                id="contactEmail"
                type="email"
                placeholder="email@company.com"
                {...form.register('contactEmail')}
              />
              {form.formState.errors.contactEmail && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.contactEmail.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="contactPhone">Phone Number *</Label>
              <Input
                id="contactPhone"
                placeholder="+1 (555) 123-4567"
                {...form.register('contactPhone')}
              />
              {form.formState.errors.contactPhone && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.contactPhone.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="decisionMaker">Decision Maker *</Label>
              <Input
                id="decisionMaker"
                placeholder="Name of decision maker"
                {...form.register('decisionMaker')}
              />
              {form.formState.errors.decisionMaker && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.decisionMaker.message}
                </p>
              )}
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="decisionMakerRole">Decision Maker Role *</Label>
              <Input
                id="decisionMakerRole"
                placeholder="e.g., HR Director, Training Manager"
                {...form.register('decisionMakerRole')}
              />
              {form.formState.errors.decisionMakerRole && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.decisionMakerRole.message}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ProjectInfoStep({ form }: { form: any }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Project Overview
          </CardTitle>
          <CardDescription>
            Describe your training project
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="projectTitle">Project Title *</Label>
            <Input
              id="projectTitle"
              placeholder="e.g., Customer Service English Training Program"
              {...form.register('projectTitle')}
            />
            {form.formState.errors.projectTitle && (
              <p className="text-sm text-destructive">
                {form.formState.errors.projectTitle.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="projectDescription">Project Description *</Label>
            <Textarea
              id="projectDescription"
              placeholder="Describe the training project, its context, and desired outcomes..."
              rows={4}
              {...form.register('projectDescription')}
            />
            {form.formState.errors.projectDescription && (
              <p className="text-sm text-destructive">
                {form.formState.errors.projectDescription.message}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Budget & Timeline
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="estimatedBudget">Estimated Budget *</Label>
              <Select onValueChange={(value) => form.setValue('estimatedBudget', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select budget range" />
                </SelectTrigger>
                <SelectContent>
                  {BUDGET_RANGES.map((range) => (
                    <SelectItem key={range} value={range}>
                      {range}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {form.formState.errors.estimatedBudget && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.estimatedBudget.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="timeline">Preferred Timeline *</Label>
              <Select onValueChange={(value) => form.setValue('timeline', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select timeline" />
                </SelectTrigger>
                <SelectContent>
                  {TIMELINES.map((timeline) => (
                    <SelectItem key={timeline} value={timeline}>
                      {timeline}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {form.formState.errors.timeline && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.timeline.message}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <Label>Project Urgency *</Label>
            <div className="space-y-3">
              {URGENCY_LEVELS.map((level) => (
                <div 
                  key={level.value}
                  className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent cursor-pointer"
                  onClick={() => form.setValue('urgency', level.value)}
                >
                  <input
                    type="radio"
                    name="urgency"
                    value={level.value}
                    {...form.register('urgency')}
                    className="sr-only"
                  />
                  <div className={cn(
                    "w-4 h-4 rounded-full border-2 flex items-center justify-center",
                    form.watch('urgency') === level.value ? "border-primary bg-primary" : "border-muted-foreground"
                  )}>
                    {form.watch('urgency') === level.value && (
                      <div className="w-2 h-2 rounded-full bg-white" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{level.label}</div>
                    <div className="text-sm text-muted-foreground">{level.description}</div>
                  </div>
                </div>
              ))}
            </div>
            {form.formState.errors.urgency && (
              <p className="text-sm text-destructive">
                {form.formState.errors.urgency.message}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Existing Training</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="hasExistingTraining"
              {...form.register('hasExistingTraining')}
            />
            <Label htmlFor="hasExistingTraining">
              We currently have existing English training programs
            </Label>
          </div>

          {form.watch('hasExistingTraining') && (
            <div className="space-y-2">
              <Label htmlFor="existingTrainingDescription">
                Please describe your existing training programs
              </Label>
              <Textarea
                id="existingTrainingDescription"
                placeholder="Describe current training programs, providers, effectiveness, etc."
                rows={3}
                {...form.register('existingTrainingDescription')}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function TrainingNeedsStep({ form }: { form: any }) {
  const selectedRoles = form.watch('targetRoles') || []
  const selectedScenarios = form.watch('communicationScenarios') || []

  const toggleRole = (role: string) => {
    const currentRoles = selectedRoles
    const updated = currentRoles.includes(role)
      ? currentRoles.filter((r: string) => r !== role)
      : [...currentRoles, role]
    form.setValue('targetRoles', updated)
  }

  const toggleScenario = (scenario: string) => {
    const currentScenarios = selectedScenarios
    const updated = currentScenarios.includes(scenario)
      ? currentScenarios.filter((s: string) => s !== scenario)
      : [...currentScenarios, scenario]
    form.setValue('communicationScenarios', updated)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            English Level Assessment
          </CardTitle>
          <CardDescription>
            Current and target English proficiency levels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <Label>Current English Level *</Label>
              <div className="space-y-2">
                {ENGLISH_LEVELS.map((level) => (
                  <div 
                    key={level.value}
                    className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent cursor-pointer"
                    onClick={() => form.setValue('currentEnglishLevel', level.value)}
                  >
                    <input
                      type="radio"
                      name="currentEnglishLevel"
                      value={level.value}
                      {...form.register('currentEnglishLevel')}
                      className="sr-only"
                    />
                    <div className={cn(
                      "w-4 h-4 rounded-full border-2 flex items-center justify-center",
                      form.watch('currentEnglishLevel') === level.value ? "border-primary bg-primary" : "border-muted-foreground"
                    )}>
                      {form.watch('currentEnglishLevel') === level.value && (
                        <div className="w-2 h-2 rounded-full bg-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{level.label}</div>
                      <div className="text-sm text-muted-foreground">{level.description}</div>
                    </div>
                  </div>
                ))}
              </div>
              {form.formState.errors.currentEnglishLevel && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.currentEnglishLevel.message}
                </p>
              )}
            </div>

            <div className="space-y-4">
              <Label>Target English Level *</Label>
              <div className="space-y-2">
                {ENGLISH_LEVELS.map((level) => (
                  <div 
                    key={level.value}
                    className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent cursor-pointer"
                    onClick={() => form.setValue('targetEnglishLevel', level.value)}
                  >
                    <input
                      type="radio"
                      name="targetEnglishLevel"
                      value={level.value}
                      {...form.register('targetEnglishLevel')}
                      className="sr-only"
                    />
                    <div className={cn(
                      "w-4 h-4 rounded-full border-2 flex items-center justify-center",
                      form.watch('targetEnglishLevel') === level.value ? "border-primary bg-primary" : "border-muted-foreground"
                    )}>
                      {form.watch('targetEnglishLevel') === level.value && (
                        <div className="w-2 h-2 rounded-full bg-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{level.label}</div>
                      <div className="text-sm text-muted-foreground">{level.description}</div>
                    </div>
                  </div>
                ))}
              </div>
              {form.formState.errors.targetEnglishLevel && (
                <p className="text-sm text-destructive">
                  {form.formState.errors.targetEnglishLevel.message}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="participantCount">Number of Participants *</Label>
            <Input
              id="participantCount"
              type="number"
              min="1"
              placeholder="Enter number of participants"
              {...form.register('participantCount', { valueAsNumber: true })}
            />
            {form.formState.errors.participantCount && (
              <p className="text-sm text-destructive">
                {form.formState.errors.participantCount.message}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Target Roles & Scenarios</CardTitle>
          <CardDescription>
            Select the roles and communication scenarios for training focus
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <Label>Target Roles * (Select all that apply)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {TARGET_ROLES.map((role) => (
                <div 
                  key={role}
                  className={cn(
                    "flex items-center space-x-2 p-3 border rounded-lg cursor-pointer transition-colors",
                    selectedRoles.includes(role) ? "bg-primary/10 border-primary" : "hover:bg-accent"
                  )}
                  onClick={() => toggleRole(role)}
                >
                  <Checkbox
                    checked={selectedRoles.includes(role)}
                    onChange={() => toggleRole(role)}
                  />
                  <Label className="cursor-pointer">{role}</Label>
                </div>
              ))}
            </div>
            {form.formState.errors.targetRoles && (
              <p className="text-sm text-destructive">
                {form.formState.errors.targetRoles.message}
              </p>
            )}
          </div>

          <div className="space-y-4">
            <Label>Communication Scenarios * (Select all that apply)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {COMMUNICATION_SCENARIOS.map((scenario) => (
                <div 
                  key={scenario}
                  className={cn(
                    "flex items-center space-x-2 p-3 border rounded-lg cursor-pointer transition-colors",
                    selectedScenarios.includes(scenario) ? "bg-primary/10 border-primary" : "hover:bg-accent"
                  )}
                  onClick={() => toggleScenario(scenario)}
                >
                  <Checkbox
                    checked={selectedScenarios.includes(scenario)}
                    onChange={() => toggleScenario(scenario)}
                  />
                  <Label className="cursor-pointer">{scenario}</Label>
                </div>
              ))}
            </div>
            {form.formState.errors.communicationScenarios && (
              <p className="text-sm text-destructive">
                {form.formState.errors.communicationScenarios.message}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Training Goals & Success Metrics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="trainingGoals">Training Goals *</Label>
            <Textarea
              id="trainingGoals"
              placeholder="Describe specific learning objectives and desired outcomes..."
              rows={4}
              {...form.register('trainingGoals')}
            />
            {form.formState.errors.trainingGoals && (
              <p className="text-sm text-destructive">
                {form.formState.errors.trainingGoals.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="specificChallenges">Specific Challenges *</Label>
            <Textarea
              id="specificChallenges"
              placeholder="What specific English communication challenges does your team face?"
              rows={3}
              {...form.register('specificChallenges')}
            />
            {form.formState.errors.specificChallenges && (
              <p className="text-sm text-destructive">
                {form.formState.errors.specificChallenges.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="successMetrics">Success Metrics *</Label>
            <Textarea
              id="successMetrics"
              placeholder="How will you measure the success of this training program?"
              rows={3}
              {...form.register('successMetrics')}
            />
            {form.formState.errors.successMetrics && (
              <p className="text-sm text-destructive">
                {form.formState.errors.successMetrics.message}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function SOPUploadStep({ uploadedFiles, setUploadedFiles }: { 
  uploadedFiles: File[]
  setUploadedFiles: React.Dispatch<React.SetStateAction<File[]>>
}) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    const validFiles: File[] = []
    const invalidFiles: string[] = []
    
    // Validate files
    files.forEach(file => {
      const maxSize = 50 * 1024 * 1024 // 50MB
      const allowedTypes = ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls']
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
      
      // Check file size
      if (file.size > maxSize) {
        invalidFiles.push(`${file.name} (too large - max 50MB)`)
        return
      }
      
      // Check file type
      if (!allowedTypes.includes(fileExtension)) {
        invalidFiles.push(`${file.name} (unsupported format - allowed: ${allowedTypes.join(', ')})`)
        return
      }
      
      // Check for duplicate files
      const isDuplicate = uploadedFiles.some(existing => 
        existing.name === file.name && existing.size === file.size
      )
      
      if (isDuplicate) {
        invalidFiles.push(`${file.name} (duplicate file)`)
        return
      }
      
      // Check total number of files (limit to 10)
      if (uploadedFiles.length + validFiles.length >= 10) {
        invalidFiles.push(`${file.name} (maximum 10 files allowed)`)
        return
      }
      
      validFiles.push(file)
    })
    
    // Show validation feedback
    if (invalidFiles.length > 0) {
      console.warn('Invalid files:', invalidFiles)
      // You could show a toast here for invalid files
    }
    
    if (validFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...validFiles])
    }
    
    // Clear the input
    event.target.value = ''
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Standard Operating Procedures
          </CardTitle>
          <CardDescription>
            Upload company SOPs and training materials to customize course content
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center space-y-4">
            <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
            <div>
              <p className="text-lg font-medium">Drop files here or click to browse</p>
              <p className="text-sm text-muted-foreground">
                Supports PDF, DOCX, TXT files up to 50MB each
              </p>
            </div>
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <Label htmlFor="file-upload">
              <Button variant="outline" asChild className="cursor-pointer">
                <span>
                  <FileText className="h-4 w-4 mr-2" />
                  Choose Files
                </span>
              </Button>
            </Label>
          </div>

          {uploadedFiles.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-medium">Uploaded Files ({uploadedFiles.length})</h4>
              <div className="space-y-2">
                {uploadedFiles.map((file, index) => {
                  const progress = uploadProgress[file.name] || 0
                  const isUploading = progress > 0 && progress < 100
                  
                  return (
                    <div key={index} className="p-3 border rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {(file.size / (1024 * 1024)).toFixed(2)} MB
                              {isUploading && ` • ${progress}% uploaded`}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                          disabled={isUploading}
                        >
                          {isUploading ? <LoadingSpinner size="sm" /> : 'Remove'}
                        </Button>
                      </div>
                      
                      {/* Progress bar for uploading files */}
                      {isUploading && (
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-900">
                  Why do we need your SOPs?
                </p>
                <p className="text-blue-700 mt-1">
                  Our AI analyzes your Standard Operating Procedures to create highly customized 
                  training content that reflects your actual business processes, terminology, and 
                  communication requirements.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ReviewStep({ 
  clientInfo, 
  projectInfo, 
  trainingNeeds 
}: { 
  clientInfo: ClientInfo | null
  projectInfo: ProjectInfo | null
  trainingNeeds: TrainingNeeds 
}) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Review Your Request
          </CardTitle>
          <CardDescription>
            Please review all information before submitting
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {clientInfo && (
            <div>
              <h4 className="font-semibold mb-2">Client Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Company:</span> {clientInfo.companyName}
                </div>
                <div>
                  <span className="font-medium">Industry:</span> {clientInfo.industry}
                </div>
                <div>
                  <span className="font-medium">Size:</span> {clientInfo.companySize}
                </div>
                <div>
                  <span className="font-medium">Location:</span> {clientInfo.location}
                </div>
                <div>
                  <span className="font-medium">Contact:</span> {clientInfo.contactPerson}
                </div>
                <div>
                  <span className="font-medium">Email:</span> {clientInfo.contactEmail}
                </div>
              </div>
            </div>
          )}

          {projectInfo && (
            <div>
              <h4 className="font-semibold mb-2">Project Details</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium">Title:</span> {projectInfo.projectTitle}
                </div>
                <div>
                  <span className="font-medium">Budget:</span> {projectInfo.estimatedBudget}
                </div>
                <div>
                  <span className="font-medium">Timeline:</span> {projectInfo.timeline}
                </div>
                <div>
                  <span className="font-medium">Urgency:</span> {projectInfo.urgency}
                </div>
                <div>
                  <span className="font-medium">Description:</span>
                  <p className="mt-1 text-muted-foreground">{projectInfo.projectDescription}</p>
                </div>
              </div>
            </div>
          )}

          <div>
            <h4 className="font-semibold mb-2">Training Requirements</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Current Level:</span> {trainingNeeds.currentEnglishLevel}
              </div>
              <div>
                <span className="font-medium">Target Level:</span> {trainingNeeds.targetEnglishLevel}
              </div>
              <div>
                <span className="font-medium">Participants:</span> {trainingNeeds.participantCount}
              </div>
              <div>
                <span className="font-medium">Target Roles:</span>
                <p className="mt-1 text-muted-foreground">
                  {trainingNeeds.targetRoles.join(', ')}
                </p>
              </div>
            </div>
            <div className="mt-4">
              <div className="font-medium">Training Goals:</div>
              <p className="mt-1 text-sm text-muted-foreground">
                {trainingNeeds.trainingGoals}
              </p>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-medium text-green-900">
                  Ready to Submit
                </p>
                <p className="text-green-700 mt-1">
                  Your course request will be processed by our AI system and reviewed by 
                  our course managers. You'll receive updates via email and can track 
                  progress in your dashboard.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}