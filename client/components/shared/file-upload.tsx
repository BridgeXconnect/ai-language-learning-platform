"use client"
import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { UploadCloud, FileText, X, Loader2, RefreshCw, AlertTriangle, CheckCircle, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { useToast } from "@/hooks/use-toast"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import type { SOPFile } from "@/lib/types"
import { SOPFileStatus } from "@/lib/types"

interface FileUploadProps {
  onFilesSelected: (files: SOPFile[]) => void
  onFileRemoved: (fileId: string) => void
  onFileRetry?: (fileId: string) => void
  uploadedFiles: SOPFile[]
  acceptedTypes?: string[]
  maxFiles?: number
  maxFileSizeMB?: number
  disabled?: boolean
}

const defaultAcceptedTypes = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "text/plain": [".txt"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
}

export function FileUpload({
  onFilesSelected,
  onFileRemoved,
  onFileRetry,
  uploadedFiles,
  acceptedTypes = ['.pdf', '.doc', '.docx'],
  maxFiles = 5,
  maxFileSizeMB = 50,
  disabled = false,
}: FileUploadProps) {
  const { toast } = useToast()
  const [isDragOver, setIsDragOver] = useState(false)

  const validateFile = useCallback((file: File): { isValid: boolean; error?: string } => {
    // Check file size
    if (file.size > maxFileSizeMB * 1024 * 1024) {
      return { isValid: false, error: `File size exceeds ${maxFileSizeMB}MB limit` }
    }
    
    // Check file type
    const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
    if (!acceptedTypes.includes(extension)) {
      return { isValid: false, error: `File type ${extension} not supported` }
    }
    
    // Check for potentially dangerous file names
    if (file.name.includes('..') || file.name.includes('/') || file.name.includes('\\')) {
      return { isValid: false, error: 'Invalid file name' }
    }
    
    return { isValid: true }
  }, [maxFileSizeMB, acceptedTypes])

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: any[]) => {
      setIsDragOver(false)
      
      if (disabled) {
        toast({
          variant: "destructive",
          title: "Upload disabled",
          description: "File upload is currently disabled.",
        })
        return
      }

      if (uploadedFiles.length + acceptedFiles.length > maxFiles) {
        toast({
          variant: "destructive",
          title: "Too many files",
          description: `You can upload a maximum of ${maxFiles} files.`,
        })
        return
      }

      // Validate each file
      const validFiles: File[] = []
      const invalidFiles: { file: File; error: string }[] = []
      
      acceptedFiles.forEach(file => {
        const validation = validateFile(file)
        if (validation.isValid) {
          validFiles.push(file)
        } else {
          invalidFiles.push({ file, error: validation.error! })
        }
      })

      // Show validation errors
      invalidFiles.forEach(({ file, error }) => {
        toast({
          variant: "destructive",
          title: `File Error: ${file.name}`,
          description: error,
        })
      })

      // Create SOPFile objects for valid files
      if (validFiles.length > 0) {
        const newSopFiles: SOPFile[] = validFiles.map((file) => ({
          id: crypto.randomUUID(), // Temporary client-side ID
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          status: SOPFileStatus.PENDING,
          progress: 0,
        }))
        onFilesSelected(newSopFiles)
        
        toast({
          title: "Files added",
          description: `${validFiles.length} file(s) ready for upload.`,
        })
      }

      // Handle dropzone rejections
      fileRejections.forEach((rejection: any) => {
        rejection.errors.forEach((error: any) => {
          toast({
            variant: "destructive",
            title: `File Error: ${rejection.file.name}`,
            description: error.message,
          })
        })
      })
    },
    [onFilesSelected, maxFileSizeMB, maxFiles, uploadedFiles.length, toast, disabled, validateFile],
  )

  const acceptedFileTypes = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/msword": [".doc"],
    "text/plain": [".txt"],
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDragEnter: () => setIsDragOver(true),
    onDragLeave: () => setIsDragOver(false),
    accept: acceptedFileTypes,
    maxSize: maxFileSizeMB * 1024 * 1024,
    disabled,
  })

  const getStatusIcon = (status: SOPFileStatus) => {
    switch (status) {
      case SOPFileStatus.PENDING:
        return <Info className="h-4 w-4 text-blue-500" />
      case SOPFileStatus.UPLOADING:
      case SOPFileStatus.PROCESSING:
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case SOPFileStatus.COMPLETED:
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case SOPFileStatus.ERROR:
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <FileText className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: SOPFileStatus) => {
    const variants = {
      [SOPFileStatus.PENDING]: { variant: 'outline' as const, text: 'Pending' },
      [SOPFileStatus.UPLOADING]: { variant: 'default' as const, text: 'Uploading' },
      [SOPFileStatus.PROCESSING]: { variant: 'default' as const, text: 'Processing' },
      [SOPFileStatus.COMPLETED]: { variant: 'default' as const, text: 'Completed' },
      [SOPFileStatus.ERROR]: { variant: 'destructive' as const, text: 'Error' },
    }
    
    const { variant, text } = variants[status] || { variant: 'outline' as const, text: 'Unknown' }
    return <Badge variant={variant} className="text-xs">{text}</Badge>
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <TooltipProvider>
      <div className="space-y-4">
        {/* Upload Guidelines */}
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Upload Standard Operating Procedures, training materials, or company documents that will help our AI agents create a customized course for your organization.
          </AlertDescription>
        </Alert>

        {/* Upload Zone */}
        <div
          {...getRootProps()}
          className={cn(
            "flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted/75 transition-all duration-200",
            isDragActive && "border-primary bg-primary/10 scale-[1.02]",
            disabled && "opacity-50 cursor-not-allowed bg-muted/25",
            uploadedFiles.length >= maxFiles && "opacity-50 cursor-not-allowed"
          )}
        >
          <input {...getInputProps()} />
          <UploadCloud className={cn(
            "h-12 w-12 mb-3 transition-colors",
            isDragActive ? "text-primary" : "text-muted-foreground",
            disabled && "text-muted-foreground/50"
          )} />
          {isDragActive ? (
            <p className="text-lg font-semibold text-primary">Drop the files here ...</p>
          ) : (
            <>
              <p className="mb-2 text-sm text-muted-foreground">
                <span className="font-semibold">
                  {disabled ? "Upload disabled" : uploadedFiles.length >= maxFiles ? "Maximum files reached" : "Click to upload"}
                </span>
                {!disabled && uploadedFiles.length < maxFiles && " or drag and drop"}
              </p>
              <p className="text-xs text-muted-foreground text-center">
                PDF, DOCX, DOC, TXT, XLSX<br />
                (MAX. {maxFileSizeMB}MB per file, up to {maxFiles} files)
              </p>
              {uploadedFiles.length > 0 && (
                <p className="text-xs text-blue-600 mt-2 font-medium">
                  {uploadedFiles.length} of {maxFiles} files uploaded
                </p>
              )}
            </>
          )}
        </div>

        {/* Files List */}
        {uploadedFiles.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium">
                Files ({uploadedFiles.length}/{maxFiles})
              </h4>
              <div className="flex gap-1">
                {uploadedFiles.filter(f => f.status === SOPFileStatus.COMPLETED).length > 0 && (
                  <Badge variant="outline" className="text-green-600">
                    {uploadedFiles.filter(f => f.status === SOPFileStatus.COMPLETED).length} completed
                  </Badge>
                )}
                {uploadedFiles.filter(f => f.status === SOPFileStatus.ERROR).length > 0 && (
                  <Badge variant="destructive">
                    {uploadedFiles.filter(f => f.status === SOPFileStatus.ERROR).length} error(s)
                  </Badge>
                )}
              </div>
            </div>
            
            {uploadedFiles.map((sopFile) => (
              <div key={sopFile.id} className="border rounded-lg p-3 space-y-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 overflow-hidden flex-1">
                    {getStatusIcon(sopFile.status)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <p className="text-sm font-medium truncate cursor-help" title={sopFile.name}>
                              {sopFile.name}
                            </p>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{sopFile.name}</p>
                          </TooltipContent>
                        </Tooltip>
                        {getStatusBadge(sopFile.status)}
                      </div>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{formatFileSize(sopFile.size)}</span>
                        {sopFile.type && (
                          <span className="uppercase">{sopFile.type.split('/')[1] || 'Unknown'}</span>
                        )}
                      </div>
                      {sopFile.notes && (
                        <p className="text-xs text-muted-foreground mt-1 italic">
                          Note: {sopFile.notes}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 ml-2">
                    {sopFile.status === SOPFileStatus.ERROR && onFileRetry && (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => onFileRetry(sopFile.id)}
                            className="h-7 w-7 p-0"
                          >
                            <RefreshCw className="h-3 w-3" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Retry upload</p>
                        </TooltipContent>
                      </Tooltip>
                    )}
                    
                    {sopFile.status !== SOPFileStatus.UPLOADING && 
                     sopFile.status !== SOPFileStatus.PROCESSING && (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => onFileRemoved(sopFile.id)}
                            className="h-7 w-7 p-0 text-muted-foreground hover:text-destructive"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Remove file</p>
                        </TooltipContent>
                      </Tooltip>
                    )}
                  </div>
                </div>
                
                {/* Progress Bar */}
                {(sopFile.status === SOPFileStatus.UPLOADING || sopFile.status === SOPFileStatus.PROCESSING) &&
                 sopFile.progress !== undefined && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>
                        {sopFile.status === SOPFileStatus.UPLOADING ? 'Uploading...' : 'Processing...'}
                      </span>
                      <span>{sopFile.progress}%</span>
                    </div>
                    <Progress value={sopFile.progress} className="h-2" />
                  </div>
                )}
                
                {/* Error Message */}
                {sopFile.status === SOPFileStatus.ERROR && sopFile.errorMessage && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription className="text-xs">
                      {sopFile.errorMessage}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </TooltipProvider>
  )
}
