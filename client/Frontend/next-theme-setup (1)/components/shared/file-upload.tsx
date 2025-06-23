"use client"
import { useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { UploadCloud, FileText, X, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { useToast } from "@/hooks/use-toast"
import type { SOPFile } from "@/lib/types"
import { SOPFileStatus } from "@/lib/types"

interface FileUploadProps {
  onFilesAdded: (files: SOPFile[]) => void
  acceptedFileTypes?: Record<string, string[]> // e.g., { 'application/pdf': ['.pdf'] }
  maxFileSizeMB?: number
  maxFiles?: number
  currentFiles: SOPFile[]
  onFileRemove: (fileName: string) => void
  // onFileUpload: (file: SOPFile) => Promise<void>; // For actual upload logic
}

const defaultAcceptedTypes = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "text/plain": [".txt"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
}

export function FileUpload({
  onFilesAdded,
  acceptedFileTypes = defaultAcceptedTypes,
  maxFileSizeMB = 50,
  maxFiles = 5,
  currentFiles,
  onFileRemove,
}: FileUploadProps) {
  const { toast } = useToast()

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: any[]) => {
      if (currentFiles.length + acceptedFiles.length > maxFiles) {
        toast({
          variant: "destructive",
          title: "Too many files",
          description: `You can upload a maximum of ${maxFiles} files.`,
        })
        return
      }

      const newSopFiles: SOPFile[] = acceptedFiles.map((file) => ({
        id: crypto.randomUUID(), // Temporary client-side ID
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        status: SOPFileStatus.PENDING,
        progress: 0,
      }))
      onFilesAdded(newSopFiles)

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
    [onFilesAdded, maxFileSizeMB, maxFiles, currentFiles.length, toast],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes,
    maxSize: maxFileSizeMB * 1024 * 1024,
  })

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          "flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted/75 transition-colors",
          isDragActive && "border-primary bg-primary/10",
        )}
      >
        <input {...getInputProps()} />
        <UploadCloud className={cn("h-12 w-12 mb-3", isDragActive ? "text-primary" : "text-muted-foreground")} />
        {isDragActive ? (
          <p className="text-lg font-semibold text-primary">Drop the files here ...</p>
        ) : (
          <>
            <p className="mb-2 text-sm text-muted-foreground">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, DOCX, TXT, XLSX (MAX. {maxFileSizeMB}MB per file, up to {maxFiles} files)
            </p>
          </>
        )}
      </div>

      {currentFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Uploaded Files:</h4>
          {currentFiles.map((sopFile) => (
            <div key={sopFile.id} className="flex items-center justify-between p-2 border rounded-md">
              <div className="flex items-center gap-2 overflow-hidden">
                <FileText className="h-5 w-5 text-muted-foreground shrink-0" />
                <div className="flex-grow overflow-hidden">
                  <p className="text-sm font-medium truncate" title={sopFile.name}>
                    {sopFile.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {(sopFile.size / 1024 / 1024).toFixed(2)} MB - {sopFile.status}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {sopFile.status === SOPFileStatus.UPLOADING || sopFile.status === SOPFileStatus.PROCESSING ? (
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                ) : (
                  <Button variant="ghost" size="icon" onClick={() => onFileRemove(sopFile.id)}>
                    <X className="h-4 w-4" />
                    <span className="sr-only">Remove file</span>
                  </Button>
                )}
              </div>
              {(sopFile.status === SOPFileStatus.UPLOADING || sopFile.status === SOPFileStatus.PROCESSING) &&
              sopFile.progress !== undefined ? (
                <Progress value={sopFile.progress} className="h-1 w-full mt-1" />
              ) : null}
              {sopFile.status === SOPFileStatus.ERROR && sopFile.errorMessage && (
                <p className="text-xs text-destructive mt-1">{sopFile.errorMessage}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
