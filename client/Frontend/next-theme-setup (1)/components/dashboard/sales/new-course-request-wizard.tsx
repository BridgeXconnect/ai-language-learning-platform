"use client"

import type React from "react"
import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Progress } from "@/components/ui/progress"
import { FileUpload } from "@/components/shared/file-upload"
import type { ClientDetails, SOPFile, CourseRequest } from "@/lib/types"
import { SOPFileStatus, CourseRequestStatus } from "@/lib/types"
import { useAuth } from "@/contexts/auth-context"
import { API_BASE_URL } from "@/lib/config"
import { useToast } from "@/hooks/use-toast"
import { ChevronLeft, ChevronRight, Send, Loader2, CheckCircle2 } from "lucide-react"

interface NewCourseRequestWizardProps {
  isOpen: boolean
  onOpenChange: (isOpen: boolean) => void
  onSuccess?: (newRequest: CourseRequest) => void
}

const STEPS = [
  { id: 1, name: "Client Details" },
  { id: 2, name: "Upload SOPs" },
  { id: 3, name: "Review & Submit" },
]

export function NewCourseRequestWizard({ isOpen, onOpenChange, onSuccess }: NewCourseRequestWizardProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [clientDetails, setClientDetails] = useState<Partial<ClientDetails>>({})
  const [sopFiles, setSopFiles] = useState<SOPFile[]>([])
  const [notes, setNotes] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submissionSuccess, setSubmissionSuccess] = useState(false)

  const { user, fetchWithAuth } = useAuth()
  const { toast } = useToast()

  useEffect(() => {
    // Reset state if dialog is reopened
    if (isOpen) {
      setCurrentStep(1)
      setClientDetails({})
      setSopFiles([])
      setNotes("")
      setIsSubmitting(false)
      setSubmissionSuccess(false)
    }
  }, [isOpen])

  const handleClientDetailsChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setClientDetails({ ...clientDetails, [e.target.name]: e.target.value })
  }

  const handleFilesAdded = (newFiles: SOPFile[]) => {
    setSopFiles((prevFiles) => [...prevFiles, ...newFiles])
  }

  const handleFileRemove = (fileIdToRemove: string) => {
    setSopFiles((prevFiles) => prevFiles.filter((file) => file.id !== fileIdToRemove))
  }

  const nextStep = () => setCurrentStep((prev) => Math.min(prev + 1, STEPS.length))
  const prevStep = () => setCurrentStep((prev) => Math.max(prev - 1, 1))

  const uploadFile = async (sopFile: SOPFile): Promise<{ id: string; name: string; url: string }> => {
    // This function simulates file upload and returns a placeholder backend ID and URL.
    // In a real app, this would make an API call to upload the file.
    setSopFiles((prev) =>
      prev.map((sf) => (sf.id === sopFile.id ? { ...sf, status: SOPFileStatus.UPLOADING, progress: 0 } : sf)),
    )

    // Simulate upload progress
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((resolve) => setTimeout(resolve, 50)) // Simulate network latency
      setSopFiles((prev) => prev.map((sf) => (sf.id === sopFile.id ? { ...sf, progress: i } : sf)))
    }

    // Simulate backend processing
    setSopFiles((prev) =>
      prev.map((sf) => (sf.id === sopFile.id ? { ...sf, status: SOPFileStatus.PROCESSING, progress: 100 } : sf)),
    )
    await new Promise((resolve) => setTimeout(resolve, 300))

    // Replace with actual API call:
    // const formData = new FormData();
    // formData.append('file', sopFile.file);
    // const response = await fetchWithAuth(`${API_BASE_URL}/sales/course-requests/upload-sop`, { // Fictional endpoint
    //   method: 'POST',
    //   body: formData, // Don't set Content-Type, browser does it for FormData
    // });
    // if (!response.ok) throw new Error(`Failed to upload ${sopFile.name}`);
    // const result = await response.json();
    // return result; // { id: backendFileId, name: fileName, url: fileUrl }

    setSopFiles((prev) => prev.map((sf) => (sf.id === sopFile.id ? { ...sf, status: SOPFileStatus.COMPLETED } : sf)))
    return { id: `backend-${sopFile.id}`, name: sopFile.name, url: `/uploads/sops/${sopFile.name}` }
  }

  const handleSubmit = async () => {
    if (!user) {
      toast({ variant: "destructive", title: "Authentication Error", description: "You must be logged in." })
      return
    }
    setIsSubmitting(true)

    try {
      const uploadedSopDetails: { id: string; name: string; url: string }[] = []
      for (const sopFile of sopFiles) {
        if (sopFile.status !== SOPFileStatus.COMPLETED) {
          // Only upload if not already "uploaded" (e.g. from a previous attempt)
          try {
            const uploadedDetail = await uploadFile(sopFile)
            uploadedSopDetails.push(uploadedDetail)
          } catch (uploadError: any) {
            setSopFiles((prev) =>
              prev.map((sf) =>
                sf.id === sopFile.id ? { ...sf, status: SOPFileStatus.ERROR, errorMessage: uploadError.message } : sf,
              ),
            )
            throw new Error(`Failed to upload ${sopFile.name}. Please try again.`)
          }
        } else {
          // If already marked completed (e.g. from a retry), use existing details if available
          uploadedSopDetails.push({
            id: `backend-${sopFile.id}`,
            name: sopFile.name,
            url: `/uploads/sops/${sopFile.name}`,
          })
        }
      }

      const payload = {
        clientDetails,
        sopFiles: uploadedSopDetails,
        notes,
        status: CourseRequestStatus.SUBMITTED,
        requestedBy: user.id,
      }

      const response = await fetchWithAuth(`${API_BASE_URL}/sales/course-requests`, {
        method: "POST",
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || "Failed to submit course request.")
      }

      const newRequest = await response.json()
      toast({ title: "Success", description: "Course request submitted successfully." })
      setSubmissionSuccess(true)
      if (onSuccess) onSuccess(newRequest)
      // Keep dialog open to show success message, then close after a delay or user action
      setTimeout(() => {
        onOpenChange(false)
      }, 2000)
    } catch (error: any) {
      toast({ variant: "destructive", title: "Submission Failed", description: error.message })
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1: // Client Details
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="companyName">Company Name</Label>
              <Input
                id="companyName"
                name="companyName"
                value={clientDetails.companyName || ""}
                onChange={handleClientDetailsChange}
                required
              />
            </div>
            <div>
              <Label htmlFor="contactPerson">Contact Person</Label>
              <Input
                id="contactPerson"
                name="contactPerson"
                value={clientDetails.contactPerson || ""}
                onChange={handleClientDetailsChange}
                required
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={clientDetails.email || ""}
                onChange={handleClientDetailsChange}
                required
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone (Optional)</Label>
              <Input id="phone" name="phone" value={clientDetails.phone || ""} onChange={handleClientDetailsChange} />
            </div>
          </div>
        )
      case 2: // Upload SOPs
        return (
          <FileUpload
            onFilesAdded={handleFilesAdded}
            currentFiles={sopFiles}
            onFileRemove={handleFileRemove}
            maxFiles={10} // Example: allow more files
          />
        )
      case 3: // Review & Submit
        return (
          <div className="space-y-4">
            <h4 className="font-semibold">Client Details:</h4>
            <p>Company: {clientDetails.companyName}</p>
            <p>
              Contact: {clientDetails.contactPerson} ({clientDetails.email})
            </p>
            <h4 className="font-semibold mt-2">SOP Files:</h4>
            {sopFiles.length > 0 ? (
              <ul className="list-disc list-inside">
                {sopFiles.map((f) => (
                  <li key={f.id}>
                    {f.name} ({(f.size / 1024 / 1024).toFixed(2)} MB)
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground">No SOP files uploaded.</p>
            )}
            <div className="mt-2">
              <Label htmlFor="notes">Additional Notes (Optional)</Label>
              <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
            </div>
          </div>
        )
      default:
        return null
    }
  }

  if (submissionSuccess) {
    return (
      <Dialog open={isOpen} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-6 w-6 text-success" />
              Submission Successful!
            </DialogTitle>
          </DialogHeader>
          <p>Your new course request has been submitted. You can track its progress in the dashboard.</p>
          <DialogFooter>
            <Button onClick={() => onOpenChange(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg md:max-w-xl lg:max-w-2xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>New Course Request Wizard</DialogTitle>
          <DialogDescription>
            Step {currentStep} of {STEPS.length}: {STEPS[currentStep - 1].name}
          </DialogDescription>
        </DialogHeader>
        <Progress value={(currentStep / STEPS.length) * 100} className="mb-4" />

        <div className="flex-grow overflow-y-auto pr-2 py-4">{renderStepContent()}</div>

        <DialogFooter className="mt-auto pt-4 border-t">
          {currentStep > 1 && (
            <Button variant="outline" onClick={prevStep} disabled={isSubmitting}>
              <ChevronLeft className="mr-2 h-4 w-4" /> Previous
            </Button>
          )}
          <div className="flex-grow"></div> {/* Spacer */}
          {currentStep < STEPS.length && (
            <Button onClick={nextStep} disabled={isSubmitting}>
              Next <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          )}
          {currentStep === STEPS.length && (
            <Button
              onClick={handleSubmit}
              disabled={
                isSubmitting ||
                sopFiles.some((sf) => sf.status === SOPFileStatus.UPLOADING || sf.status === SOPFileStatus.PROCESSING)
              }
            >
              {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
              Submit Request
            </Button>
          )}
          <DialogClose asChild>
            <Button variant="ghost" disabled={isSubmitting}>
              Cancel
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
