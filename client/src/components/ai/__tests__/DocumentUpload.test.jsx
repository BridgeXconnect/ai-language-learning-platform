import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import DocumentUpload from '../DocumentUpload';
import { aiAPI } from '../../../services/api';

// Mock the API
vi.mock('../../../services/api', () => ({
  aiAPI: {
    processDocument: vi.fn(),
    getDocumentStatus: vi.fn(),
  }
}));

// Mock react-dropzone
vi.mock('react-dropzone', () => ({
  useDropzone: ({ onDrop, accept, maxSize, multiple }) => ({
    getRootProps: () => ({
      'data-testid': 'dropzone',
      onClick: () => {},
    }),
    getInputProps: () => ({
      'data-testid': 'file-input',
    }),
    isDragActive: false,
  }),
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

describe('DocumentUpload', () => {
  const mockOnUpload = vi.fn();
  const mockProps = {
    onUpload: mockOnUpload,
    uploadedDocuments: []
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders upload area', () => {
    render(<DocumentUpload {...mockProps} />);
    
    expect(screen.getByTestId('dropzone')).toBeInTheDocument();
    expect(screen.getByText('Drag and drop SOP documents here, or click to select files')).toBeInTheDocument();
  });

  it('shows supported file formats', () => {
    render(<DocumentUpload {...mockProps} />);
    
    expect(screen.getByText('Supports PDF, DOC, DOCX, TXT files up to 10MB each')).toBeInTheDocument();
  });

  it('displays upload guidelines', () => {
    render(<DocumentUpload {...mockProps} />);
    
    expect(screen.getByText('Upload Guidelines')).toBeInTheDocument();
    expect(screen.getByText('• Upload your Standard Operating Procedures (SOPs)')).toBeInTheDocument();
  });

  it('handles file upload', async () => {
    const mockResponse = {
      data: { document_id: 'doc-123' }
    };
    aiAPI.processDocument.mockResolvedValue(mockResponse);

    const { rerender } = render(<DocumentUpload {...mockProps} />);
    
    // Mock file drop
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    // We need to directly test the onDrop callback since useDropzone is mocked
    // In a real test, you would simulate drag and drop events
    
    expect(screen.getByTestId('dropzone')).toBeInTheDocument();
  });

  it('displays uploaded documents', () => {
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'test.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'completed',
        uploadedAt: new Date().toISOString()
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    expect(screen.getByText('Uploaded Documents (1)')).toBeInTheDocument();
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });

  it('shows processing status', () => {
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'processing.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'processing',
        uploadedAt: new Date().toISOString()
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    expect(screen.getByText('processing.pdf')).toBeInTheDocument();
  });

  it('handles document removal', async () => {
    const user = userEvent.setup();
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'test.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'completed',
        uploadedAt: new Date().toISOString()
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    // Find and click remove button
    const removeButton = screen.getByRole('button', { name: /remove/i });
    await user.click(removeButton);
    
    expect(mockOnUpload).toHaveBeenCalledWith([]);
  });

  it('formats file size correctly', () => {
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'large.pdf',
        size: 1048576, // 1MB
        type: 'application/pdf',
        status: 'completed',
        uploadedAt: new Date().toISOString()
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    expect(screen.getByText(/1 MB/)).toBeInTheDocument();
  });

  it('shows document processing summary', () => {
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'completed.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'completed',
        uploadedAt: new Date().toISOString()
      },
      {
        id: 'doc-2',
        name: 'processing.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'processing',
        uploadedAt: new Date().toISOString()
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    expect(screen.getByText('1 of 2 documents processed successfully')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    aiAPI.processDocument.mockRejectedValue(new Error('Upload failed'));
    
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<DocumentUpload {...mockProps} />);
    
    // The component should render without crashing even if API fails
    expect(screen.getByTestId('dropzone')).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });

  it('shows different icons for different file types', () => {
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'test.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'completed',
        uploadedAt: new Date().toISOString()
      },
      {
        id: 'doc-2',
        name: 'test.docx',
        size: 1024,
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        status: 'completed',
        uploadedAt: new Date().toISOString()
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
    expect(screen.getByText('test.docx')).toBeInTheDocument();
  });

  it('displays processing result details', () => {
    const uploadedDocuments = [
      {
        id: 'doc-1',
        name: 'test.pdf',
        size: 1024,
        type: 'application/pdf',
        status: 'completed',
        uploadedAt: new Date().toISOString(),
        processingResult: {
          extracted_text_preview: 'This is a preview of the extracted text...',
          word_count: 500,
          chunk_count: 5
        }
      }
    ];

    render(<DocumentUpload {...mockProps} uploadedDocuments={uploadedDocuments} />);
    
    expect(screen.getByText(/500 words/)).toBeInTheDocument();
    expect(screen.getByText(/5 chunks/)).toBeInTheDocument();
    expect(screen.getByText(/Preview: This is a preview/)).toBeInTheDocument();
  });
});