"use client"

import * as React from "react"
import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useRouter } from "next/navigation"
import {
  CheckCircle,
  Building,
  Users,
  FileText,
  Settings,
  ChevronRight,
  ChevronLeft,
  Upload,
  X,
  AlertCircle,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { FileUpload } from "@/components/shared/file-upload"
import { salesApi } from "@/lib/api"
import { CourseRequestStatus, SOPFile, SOPFileStatus } from "@/lib/types"

// Form schemas for each step
const clientInfoSchema = z.object({
  companyName: z.string().min(2, "Company name must be at least 2 characters"),
  contactPerson: z.string().min(2, "Contact person name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  phone: z.string().optional(),
  industry: z.string().optional(),
  companySize: z.string().optional(),
})

const trainingNeedsSchema = z.object({
  courseTitle: z.string().min(5, "Course title must be at least 5 characters"),
  currentCEFRLevel: z.enum(["A1", "A2", "B1", "B2", "C1", "C2"], {
    required_error: "Please select current CEFR level"
  }),
  targetCEFRLevel: z.enum(["A1", "A2", "B1", "B2", "C1", "C2"], {
    required_error: "Please select target CEFR level"
  }),
  participantCount: z.coerce
    .number()
    .min(1, "Must have at least 1 participant")
    .max(1000, "Maximum 1000 participants"),
  trainingObjectives: z.string()
    .min(10, "Please provide detailed training objectives (minimum 10 characters)")
    .max(500, "Training objectives cannot exceed 500 characters"),
  painPoints: z.string()
    .min(10, "Please describe current challenges (minimum 10 characters)")
    .max(300, "Pain points cannot exceed 300 characters")
    .optional(),
  specificRoles: z.string().optional(),
  courseLengthHours: z.coerce.number().min(1).max(500).optional(),
  lessonsPerModule: z.coerce.number().min(1).max(20).optional(),
  deliveryMethod: z.enum(["IN_PERSON", "VIRTUAL", "BLENDED"], {
    required_error: "Please select delivery method"
  }),
  preferredSchedule: z.string().optional(),
  priority: z.enum(["LOW", "NORMAL", "HIGH", "URGENT"]).default("NORMAL"),
  internalNotes: z.string().optional()
})
.refine((data) => validateCEFRProgression(data.currentCEFRLevel, data.targetCEFRLevel), {
  message: "Target CEFR level must be same or higher than current level, max 2 levels progression",
  path: ["targetCEFRLevel"]
})

const sopUploadSchema = z.object({
  sopFiles: z.array(z.custom<SOPFile>()).min(1, "Please upload at least one SOP document"),
})

type ClientInfoData = z.infer<typeof clientInfoSchema>
type TrainingNeedsData = z.infer<typeof trainingNeedsSchema>
type SOPUploadData = z.infer<typeof sopUploadSchema>

// Add type definitions for form data
interface FormData extends ClientInfoData, TrainingNeedsData, SOPUploadData {}

interface WizardStep {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
}

const steps: WizardStep[] = [
  {
    id: "client-info",
    title: "Client Information",
    description: "Basic company and contact details",
    icon: Building,
  },
  {
    id: "training-needs",
    title: "Training Requirements",
    description: "Course objectives and specifications",
    icon: Users,
  },
  {
    id: "sop-upload",
    title: "SOP Documents",
    description: "Upload Standard Operating Procedures",
    icon: FileText,
  },
  {
    id: "review",
    title: "Review & Submit",
    description: "Confirm details and submit request",
    icon: Settings,
  },
]

const CEFR_LEVELS = [
  { value: "A1", label: "A1 - Beginner" },
  { value: "A2", label: "A2 - Elementary" },
  { value: "B1", label: "B1 - Intermediate" },
  { value: "B2", label: "B2 - Upper Intermediate" },
  { value: "C1", label: "C1 - Advanced" },
  { value: "C2", label: "C2 - Proficiency" },
]

const COMPANY_SIZES = [
  { value: "1-10", label: "1-10 employees" },
  { value: "11-50", label: "11-50 employees" },
  { value: "51-200", label: "51-200 employees" },
  { value: "201-1000", label: "201-1000 employees" },
  { value: "1000+", label: "1000+ employees" },
]

const DELIVERY_METHODS = [
  { value: "IN_PERSON", label: "In-person Training" },
  { value: "VIRTUAL", label: "Virtual/Online" },
  { value: "BLENDED", label: "Blended Learning" }
]

const PRIORITY_LEVELS = [
  { value: "LOW", label: "Low Priority" },
  { value: "NORMAL", label: "Normal Priority" },
  { value: "HIGH", label: "High Priority" },
  { value: "URGENT", label: "Urgent" }
]

// CEFR Level ordering for validation
const CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

// Add type for validation function
const validateCEFRProgression = (currentLevel: string, targetLevel: string): boolean => {
  if (!currentLevel || !targetLevel) return true
  
  const currentIndex = CEFR_ORDER.indexOf(currentLevel)
  const targetIndex = CEFR_ORDER.indexOf(targetLevel)
  
  return targetIndex >= currentIndex && targetIndex <= currentIndex + 2
}

export function NewCourseRequestWizard() {
  const router = useRouter()
  const { toast } = useToast()
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<SOPFile[]>([])

  // Form instances for each step
  const clientInfoForm = useForm<ClientInfoData>({
    resolver: zodResolver(clientInfoSchema),
    defaultValues: {
      companyName: "",
      contactPerson: "",
      email: "",
      phone: "",
      industry: "",
      companySize: "",
    },
  })

  const trainingNeedsForm = useForm<TrainingNeedsData>({
    resolver: zodResolver(trainingNeedsSchema),
    defaultValues: {
      courseTitle: "",
      currentCEFRLevel: undefined,
      targetCEFRLevel: undefined,
      participantCount: 1,
      trainingObjectives: "",
      painPoints: "",
      specificRoles: "",
      courseLengthHours: undefined,
      lessonsPerModule: undefined,
      deliveryMethod: undefined,
      preferredSchedule: "",
      priority: "NORMAL",
      internalNotes: "",
    },
  })

  const sopUploadForm = useForm<SOPUploadData>({
    resolver: zodResolver(sopUploadSchema),
    defaultValues: {
      sopFiles: [],
    },
  })

  const currentStepData = steps[currentStep]
  const progress = ((currentStep + 1) / steps.length) * 100

  const validateCurrentStep = async () => {
    switch (currentStep) {
      case 0:
        return await clientInfoForm.trigger()
      case 1:
        return await trainingNeedsForm.trigger()
      case 2:
        sopUploadForm.setValue("sopFiles", uploadedFiles)
        return await sopUploadForm.trigger()
      case 3:
        return true // Review step doesn't need validation
      default:
        return true
    }
  }

  const nextStep = async () => {
    const isValid = await validateCurrentStep()
    if (isValid && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFileUpload = (newFiles: SOPFile[]): void => {
    setUploadedFiles(prev => [...prev, ...newFiles])
    sopUploadForm.setValue('sopFiles', [...uploadedFiles, ...newFiles])
  }

  const removeFile = (fileId: string): void => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId))
    sopUploadForm.setValue('sopFiles', uploadedFiles.filter(file => file.id !== fileId))
  }

  const submitRequest = async (): Promise<void> => {
    try {
      setIsSubmitting(true)
      
      const clientInfo = clientInfoForm.getValues()
      const trainingNeeds = trainingNeedsForm.getValues()
      
      const requestData = {
        // Client Information
        company_name: clientInfo.companyName,
        industry: clientInfo.industry || clientInfo.companySize,
        contact_person: clientInfo.contactPerson,
        contact_email: clientInfo.email,
        contact_phone: clientInfo.phone || null,
        
        // Training Requirements
        cohort_size: trainingNeeds.participantCount,
        current_cefr: trainingNeeds.currentCEFRLevel,
        target_cefr: trainingNeeds.targetCEFRLevel,
        training_objectives: trainingNeeds.trainingObjectives,
        pain_points: trainingNeeds.painPoints || null,
        specific_requirements: trainingNeeds.specificRoles || null,
        
        // Course Structure Preferences
        course_length_hours: trainingNeeds.courseLengthHours || null,
        lessons_per_module: trainingNeeds.lessonsPerModule || null,
        delivery_method: trainingNeeds.deliveryMethod,
        preferred_schedule: trainingNeeds.preferredSchedule || null,
        
        // Request Management
        priority: trainingNeeds.priority,
        internal_notes: trainingNeeds.internalNotes || null
      }

      const response = await fetch('http://localhost:8000/api/sales/course-requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(requestData)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to submit request')
      }

      const data = await response.json()
      
      // Upload SOP files if any
      if (uploadedFiles.length > 0) {
        for (const file of uploadedFiles) {
          const formData = new FormData()
          formData.append('file', file.file)
          if (file.notes) {
            formData.append('upload_notes', file.notes)
          }

          const uploadResponse = await fetch(`http://localhost:8000/api/sales/course-requests/${data.id}/sop`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
          })

          if (!uploadResponse.ok) {
            throw new Error(`Failed to upload file ${file.name}`)
          }
        }
      }

      toast({
        title: "Success",
        description: "Course request submitted successfully",
        variant: "default"
      })
      
      router.push('/dashboard/sales/requests')
    } catch (error) {
      console.error('Submission error:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit request",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderClientInfoStep = () => {
    return (
      <Form {...clientInfoForm}>
        <form onSubmit={clientInfoForm.handleSubmit(nextStep)} className="space-y-6">
          <div className="grid gap-4">
            <FormField
              control={clientInfoForm.control}
              name="companyName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Company Name *</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={clientInfoForm.control}
              name="contactPerson"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Contact Person *</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={clientInfoForm.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email Address *</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={clientInfoForm.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone Number</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={clientInfoForm.control}
              name="industry"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Industry</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={clientInfoForm.control}
              name="companySize"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Company Size</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select company size" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {COMPANY_SIZES.map((size) => (
                        <SelectItem key={size.value} value={size.value}>
                          {size.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting}>
              Next <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </form>
      </Form>
    )
  }

  const renderTrainingNeedsStep = () => {
    return (
      <Form {...trainingNeedsForm}>
        <form onSubmit={trainingNeedsForm.handleSubmit(nextStep)} className="space-y-6">
          <div className="grid gap-4">
            <FormField
              control={trainingNeedsForm.control}
              name="courseTitle"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Course Title *</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={trainingNeedsForm.control}
                name="currentCEFRLevel"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Current CEFR Level *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select level" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {CEFR_LEVELS.map((level) => (
                          <SelectItem key={level.value} value={level.value}>
                            {level.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={trainingNeedsForm.control}
                name="targetCEFRLevel"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Target CEFR Level *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select level" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {CEFR_LEVELS.map((level) => (
                          <SelectItem key={level.value} value={level.value}>
                            {level.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={trainingNeedsForm.control}
              name="participantCount"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Number of Participants *</FormLabel>
                  <FormControl>
                    <Input type="number" min="1" max="1000" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={trainingNeedsForm.control}
              name="trainingObjectives"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Training Objectives *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe the main objectives and desired outcomes..."
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    {field.value?.length || 0}/500 characters
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={trainingNeedsForm.control}
              name="painPoints"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Current Challenges</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe current language-related challenges..."
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    {field.value?.length || 0}/300 characters
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={trainingNeedsForm.control}
              name="deliveryMethod"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Delivery Method *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select method" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {DELIVERY_METHODS.map((method) => (
                        <SelectItem key={method.value} value={method.value}>
                          {method.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={trainingNeedsForm.control}
                name="courseLengthHours"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Course Length (Hours)</FormLabel>
                    <FormControl>
                      <Input type="number" min="1" max="500" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={trainingNeedsForm.control}
                name="lessonsPerModule"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Lessons per Module</FormLabel>
                    <FormControl>
                      <Input type="number" min="1" max="20" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={trainingNeedsForm.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Priority</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {PRIORITY_LEVELS.map((level) => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={trainingNeedsForm.control}
              name="internalNotes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Internal Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter any internal notes or comments"
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <div className="flex justify-between">
            <Button type="button" variant="outline" onClick={prevStep}>
              <ChevronLeft className="mr-2 h-4 w-4" /> Back
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              Next <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </form>
      </Form>
    )
  }

  const renderSOPUploadStep = () => {
    return (
      <div className="space-y-6">
        <FileUpload
          onFilesSelected={handleFileUpload}
          onFileRemoved={removeFile}
          uploadedFiles={uploadedFiles}
          maxFiles={5}
          acceptedTypes={['.pdf', '.doc', '.docx']}
        />
        <div className="flex justify-between">
          <Button type="button" variant="outline" onClick={prevStep}>
            <ChevronLeft className="mr-2 h-4 w-4" /> Back
          </Button>
          <Button onClick={nextStep} disabled={isSubmitting}>
            Next <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    )
  }

  const renderReviewStep = () => {
    const clientInfo = clientInfoForm.getValues();
    const trainingNeeds = trainingNeedsForm.getValues();
    
    return (
      <div className="space-y-6">
        <div className="rounded-lg border p-4 space-y-4">
          <div>
            <h3 className="font-medium mb-2">Client Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><strong>Company:</strong> {clientInfo.companyName}</div>
              <div><strong>Contact:</strong> {clientInfo.contactPerson}</div>
              <div><strong>Email:</strong> {clientInfo.email}</div>
              <div><strong>Phone:</strong> {clientInfo.phone || 'N/A'}</div>
              <div><strong>Industry:</strong> {clientInfo.industry || 'N/A'}</div>
              <div><strong>Size:</strong> {clientInfo.companySize || 'N/A'}</div>
            </div>
          </div>

          <div>
            <h3 className="font-medium mb-2">Training Requirements</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><strong>Course Title:</strong> {trainingNeeds.courseTitle}</div>
              <div><strong>Participants:</strong> {trainingNeeds.participantCount}</div>
              <div><strong>Current Level:</strong> {trainingNeeds.currentCEFRLevel}</div>
              <div><strong>Target Level:</strong> {trainingNeeds.targetCEFRLevel}</div>
              <div><strong>Delivery:</strong> {trainingNeeds.deliveryMethod}</div>
              <div><strong>Course Length:</strong> {trainingNeeds.courseLengthHours} hours</div>
              <div><strong>Priority:</strong> {trainingNeeds.priority}</div>
            </div>
          </div>

          <div>
            <h3 className="font-medium mb-2">Training Objectives</h3>
            <p className="text-sm text-muted-foreground">{trainingNeeds.trainingObjectives}</p>
          </div>

          {trainingNeeds.painPoints && (
            <div>
              <h3 className="font-medium mb-2">Current Challenges</h3>
              <p className="text-sm text-muted-foreground">{trainingNeeds.painPoints}</p>
            </div>
          )}

          {uploadedFiles.length > 0 && (
            <div>
              <h3 className="font-medium mb-2">SOP Documents</h3>
              <ul className="text-sm space-y-1">
                {uploadedFiles.map((file) => (
                  <li key={file.id}>{file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex justify-between">
          <Button type="button" variant="outline" onClick={prevStep}>
            <ChevronLeft className="mr-2 h-4 w-4" /> Back
          </Button>
          <Button onClick={submitRequest} disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit Request'}
          </Button>
        </div>
      </div>
    );
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderClientInfoStep();
      case 1:
        return renderTrainingNeedsStep();
      case 2:
        return renderSOPUploadStep();
      case 3:
        return renderReviewStep();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold">{currentStepData.title}</h2>
            <p className="text-muted-foreground">{currentStepData.description}</p>
          </div>
          <div className="text-sm text-muted-foreground">
            Step {currentStep + 1} of {steps.length}
          </div>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Step Indicators */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((step, index) => {
          const Icon = step.icon
          const isActive = index === currentStep
          const isCompleted = index < currentStep
          
          return (
            <div key={step.id} className="flex items-center">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  isCompleted
                    ? "bg-primary border-primary text-primary-foreground"
                    : isActive
                    ? "border-primary text-primary"
                    : "border-muted text-muted-foreground"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <Icon className="h-5 w-5" />
                )}
              </div>
              <div className="ml-3 min-w-0 flex-1">
                <p className={`text-sm font-medium ${isActive ? "text-primary" : ""}`}>
                  {step.title}
                </p>
              </div>
              {index < steps.length - 1 && (
                <ChevronRight className="h-5 w-5 text-muted-foreground mx-4" />
              )}
            </div>
          )
        })}
      </div>

      {/* Step Content */}
      <div className="mb-8">
        {renderStepContent()}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>

        <div className="flex space-x-2">
          {currentStep < steps.length - 1 ? (
            <Button onClick={nextStep}>
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={submitRequest} disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : "Submit Request"}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}