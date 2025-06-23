import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  File, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Download
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { aiAPI } from '../../services/api';

const DocumentUpload = ({ onUpload, uploadedDocuments = [] }) => {
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState(uploadedDocuments);
  const [processingStatus, setProcessingStatus] = useState({});

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    
    try {
      const uploadPromises = acceptedFiles.map(async (file) => {
        const metadata = {
          filename: file.name,
          size: file.size,
          type: file.type
        };

        const response = await aiAPI.processDocument(file, metadata);
        const documentId = response.data.document_id;
        
        // Start polling for processing status
        pollProcessingStatus(documentId);
        
        return {
          id: documentId,
          name: file.name,
          size: file.size,
          type: file.type,
          status: 'processing',
          uploadedAt: new Date().toISOString()
        };
      });

      const newDocuments = await Promise.all(uploadPromises);
      const updatedDocuments = [...documents, ...newDocuments];
      
      setDocuments(updatedDocuments);
      onUpload(updatedDocuments);
      
      toast.success(`${acceptedFiles.length} document(s) uploaded successfully`);
    } catch (error) {
      toast.error('Failed to upload documents');
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  }, [documents, onUpload]);

  const pollProcessingStatus = async (documentId) => {
    const interval = setInterval(async () => {
      try {
        const response = await aiAPI.getDocumentStatus(documentId);
        const status = response.data.status;
        
        setProcessingStatus(prev => ({
          ...prev,
          [documentId]: status
        }));

        if (status === 'completed' || status === 'failed') {
          clearInterval(interval);
          
          // Update document status
          setDocuments(prev => prev.map(doc => 
            doc.id === documentId 
              ? { ...doc, status, processingResult: response.data }
              : doc
          ));
        }
      } catch (error) {
        console.error('Status polling error:', error);
        clearInterval(interval);
      }
    }, 2000);

    // Cleanup after 5 minutes
    setTimeout(() => clearInterval(interval), 300000);
  };

  const removeDocument = (documentId) => {
    const updatedDocuments = documents.filter(doc => doc.id !== documentId);
    setDocuments(updatedDocuments);
    onUpload(updatedDocuments);
    
    // Clean up processing status
    setProcessingStatus(prev => {
      const newStatus = { ...prev };
      delete newStatus[documentId];
      return newStatus;
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return <FileText className="w-5 h-5 text-red-500" />;
    if (type.includes('word') || type.includes('document')) return <File className="w-5 h-5 text-blue-500" />;
    return <File className="w-5 h-5 text-gray-500" />;
  };

  const getStatusIcon = (document) => {
    const status = processingStatus[document.id] || document.status;
    
    switch (status) {
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        {isDragActive ? (
          <p className="text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-2">
              Drag and drop SOP documents here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, DOC, DOCX, TXT files up to 10MB each
            </p>
          </div>
        )}
        {uploading && (
          <div className="mt-4">
            <Loader2 className="w-6 h-6 text-blue-500 animate-spin mx-auto" />
            <p className="text-sm text-blue-600 mt-2">Uploading...</p>
          </div>
        )}
      </div>

      {/* Uploaded Documents List */}
      {documents.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Documents ({documents.length})
          </h3>
          
          <AnimatePresence>
            {documents.map((document) => (
              <motion.div
                key={document.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border"
              >
                <div className="flex items-center space-x-3">
                  {getFileIcon(document.type)}
                  <div>
                    <p className="font-medium text-gray-900">{document.name}</p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(document.size)} • 
                      {new Date(document.uploadedAt).toLocaleDateString()}
                    </p>
                    {document.processingResult?.extracted_text_preview && (
                      <p className="text-xs text-gray-400 mt-1 max-w-md truncate">
                        Preview: {document.processingResult.extracted_text_preview}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {getStatusIcon(document)}
                  
                  {document.status === 'completed' && document.processingResult && (
                    <div className="text-xs text-gray-500">
                      {document.processingResult.word_count} words • 
                      {document.processingResult.chunk_count} chunks
                    </div>
                  )}
                  
                  {document.status === 'failed' && (
                    <div className="text-xs text-red-500">
                      Processing failed
                    </div>
                  )}

                  <button
                    onClick={() => removeDocument(document.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Processing Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <FileText className="w-5 h-5 text-blue-400" />
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-blue-800">
                  Document Processing
                </h4>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    {documents.filter(d => (processingStatus[d.id] || d.status) === 'completed').length} of {documents.length} documents processed successfully
                  </p>
                  <p className="mt-1">
                    These documents will be used to generate contextually relevant course content
                    based on your organization's specific procedures and requirements.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Guidelines */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">
          Upload Guidelines
        </h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Upload your Standard Operating Procedures (SOPs)</li>
          <li>• Include company policies and training materials</li>
          <li>• Add industry-specific documents for better context</li>
          <li>• Ensure documents are in English for best results</li>
          <li>• Clean, well-formatted documents produce better courses</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUpload;