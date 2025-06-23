import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import CourseGenerationWizard from '../CourseGenerationWizard';
import { aiAPI, salesAPI } from '../../../services/api';

// Mock the API modules
vi.mock('../../../services/api', () => ({
  aiAPI: {
    generateCourse: vi.fn(),
    getGenerationStatus: vi.fn(),
    getGenerationResult: vi.fn(),
  },
  salesAPI: {
    getCourseRequests: vi.fn(),
  }
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  }
}));

describe('CourseGenerationWizard', () => {
  const mockProps = {
    isOpen: true,
    onClose: vi.fn(),
    initialData: {
      id: 1,
      company_name: 'Test Company',
      industry: 'Technology'
    }
  };

  const mockCourseRequests = [
    {
      id: 1,
      company_name: 'Test Company',
      training_objectives: 'Improve communication skills'
    },
    {
      id: 2,
      company_name: 'Another Company',
      training_objectives: 'Technical writing'
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    salesAPI.getCourseRequests.mockResolvedValue({
      data: { requests: mockCourseRequests }
    });
  });

  it('renders when open', async () => {
    render(<CourseGenerationWizard {...mockProps} />);
    
    expect(screen.getByText('AI Course Generation')).toBeInTheDocument();
    expect(screen.getByText('Course Request')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<CourseGenerationWizard {...mockProps} isOpen={false} />);
    
    expect(screen.queryByText('AI Course Generation')).not.toBeInTheDocument();
  });

  it('loads course requests on mount', async () => {
    render(<CourseGenerationWizard {...mockProps} />);
    
    await waitFor(() => {
      expect(salesAPI.getCourseRequests).toHaveBeenCalledWith({ status: 'submitted' });
    });
  });

  it('navigates through steps', async () => {
    const user = userEvent.setup();
    render(<CourseGenerationWizard {...mockProps} />);
    
    // Should start on first step
    expect(screen.getByText('Course Request')).toBeInTheDocument();
    
    // Click next
    const nextButton = screen.getByText('Next');
    await user.click(nextButton);
    
    // Should move to second step
    expect(screen.getByText('Upload Documents')).toBeInTheDocument();
  });

  it('validates form fields', async () => {
    const user = userEvent.setup();
    render(<CourseGenerationWizard {...mockProps} />);
    
    // Try to submit without selecting a course request
    const nextButton = screen.getByText('Next');
    await user.click(nextButton);
    
    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText('Course request is required')).toBeInTheDocument();
    });
  });

  it('handles course generation', async () => {
    const user = userEvent.setup();
    const mockGenerationJob = { job_id: 'test-job-123' };
    
    aiAPI.generateCourse.mockResolvedValue({
      data: mockGenerationJob
    });
    
    render(<CourseGenerationWizard {...mockProps} />);
    
    // Fill out form
    await waitFor(() => {
      const select = screen.getByDisplayValue('Select a course request...');
      expect(select).toBeInTheDocument();
    });
    
    // Select a course request
    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');
    
    // Navigate through steps
    for (let i = 0; i < 3; i++) {
      const nextButton = screen.getByText('Next');
      await user.click(nextButton);
    }
    
    // Generate course
    const generateButton = screen.getByText('Generate Course');
    await user.click(generateButton);
    
    await waitFor(() => {
      expect(aiAPI.generateCourse).toHaveBeenCalled();
    });
  });

  it('handles close', async () => {
    const user = userEvent.setup();
    render(<CourseGenerationWizard {...mockProps} />);
    
    const closeButton = screen.getByText('×');
    await user.click(closeButton);
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('pre-fills form with initial data', async () => {
    render(<CourseGenerationWizard {...mockProps} />);
    
    await waitFor(() => {
      const select = screen.getByRole('combobox');
      expect(select.value).toBe('1');
    });
  });

  it('displays focus areas checkboxes', async () => {
    render(<CourseGenerationWizard {...mockProps} />);
    
    expect(screen.getByLabelText('communication')).toBeInTheDocument();
    expect(screen.getByLabelText('grammar')).toBeInTheDocument();
    expect(screen.getByLabelText('vocabulary')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup();
    salesAPI.getCourseRequests.mockRejectedValue(new Error('API Error'));
    
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<CourseGenerationWizard {...mockProps} />);
    
    // Should handle error without crashing
    await waitFor(() => {
      expect(consoleSpy).not.toHaveBeenCalled();
    });
    
    consoleSpy.mockRestore();
  });

  it('updates progress indicator', async () => {
    const user = userEvent.setup();
    render(<CourseGenerationWizard {...mockProps} />);
    
    // First step should be active
    const firstStep = screen.getByText('Course Request');
    expect(firstStep.closest('div')).toHaveClass('font-medium');
    
    // Click next
    const nextButton = screen.getByText('Next');
    await user.click(nextButton);
    
    // Second step should be active
    const secondStep = screen.getByText('Upload Documents');
    expect(secondStep.closest('div')).toHaveClass('font-medium');
  });

  it('handles previous button', async () => {
    const user = userEvent.setup();
    render(<CourseGenerationWizard {...mockProps} />);
    
    // Navigate to second step
    const nextButton = screen.getByText('Next');
    await user.click(nextButton);
    
    // Go back
    const previousButton = screen.getByText('Previous');
    await user.click(previousButton);
    
    // Should be back on first step
    expect(screen.getByText('Course Request')).toBeInTheDocument();
  });

  it('disables previous button on first step', () => {
    render(<CourseGenerationWizard {...mockProps} />);
    
    const previousButton = screen.getByText('Previous');
    expect(previousButton).toBeDisabled();
  });
});