import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { AIChatInterface } from '../ai-chat-interface'

// Mock the auth context
jest.mock('@/contexts/auth-context', () => ({
  useAuth: () => ({
    user: { first_name: 'Test', username: 'testuser' }
  })
}))

// Mock the toast hook
jest.mock('@/components/ui/use-toast', () => ({
  toast: jest.fn()
}))

describe('AIChatInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders with default props', () => {
    render(<AIChatInterface />)
    
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
    expect(screen.getByText('General assistance')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument()
  })

  it('renders with course creation context', () => {
    render(<AIChatInterface context="course-creation" />)
    
    expect(screen.getByText('Course creation & curriculum design')).toBeInTheDocument()
    expect(screen.getByText('Help me create a course outline')).toBeInTheDocument()
  })

  it('renders with student learning context', () => {
    render(<AIChatInterface context="student-learning" />)
    
    expect(screen.getByText('Learning assistance & progress tracking')).toBeInTheDocument()
    expect(screen.getByText('Explain this concept')).toBeInTheDocument()
  })

  it('sends message on button click', async () => {
    render(<AIChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me anything...')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument()
    })
  })

  it('sends message on Enter key press', async () => {
    render(<AIChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me anything...')
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })
    
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument()
    })
  })

  it('shows loading state while processing', async () => {
    render(<AIChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me anything...')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    expect(screen.getByText('AI is thinking...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.queryByText('AI is thinking...')).not.toBeInTheDocument()
    })
  })

  it('handles suggestion clicks', () => {
    render(<AIChatInterface context="course-creation" />)
    
    const suggestion = screen.getByText('Help me create a course outline')
    fireEvent.click(suggestion)
    
    const input = screen.getByPlaceholderText('Ask me anything...')
    expect(input).toHaveValue('Help me create a course outline')
  })

  it('renders compact variant correctly', () => {
    render(<AIChatInterface variant="compact" />)
    
    const container = screen.getByText('AI Assistant').closest('div')
    expect(container).toHaveClass('h-80', 'w-80')
  })

  it('renders overlay variant correctly', () => {
    render(<AIChatInterface variant="overlay" />)
    
    const container = screen.getByText('AI Assistant').closest('div')
    expect(container).toHaveClass('fixed', 'bottom-4', 'right-4', 'z-50')
  })

  it('calls onSuggestionApply when action is applied', async () => {
    const mockOnSuggestionApply = jest.fn()
    render(<AIChatInterface onSuggestionApply={mockOnSuggestionApply} />)
    
    const input = screen.getByPlaceholderText('Ask me anything...')
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })
    
    await waitFor(() => {
      const applyButton = screen.getByText('Apply')
      fireEvent.click(applyButton)
      expect(mockOnSuggestionApply).toHaveBeenCalled()
    })
  })

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = jest.fn()
    render(<AIChatInterface onClose={mockOnClose} />)
    
    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)
    
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('minimizes overlay variant correctly', () => {
    render(<AIChatInterface variant="overlay" />)
    
    const minimizeButton = screen.getByRole('button', { name: /minimize/i })
    fireEvent.click(minimizeButton)
    
    expect(screen.getByRole('button')).toHaveClass('rounded-full')
  })

  it('disables send button when input is empty', () => {
    render(<AIChatInterface />)
    
    const sendButton = screen.getByRole('button', { name: /send/i })
    expect(sendButton).toBeDisabled()
  })

  it('enables send button when input has content', () => {
    render(<AIChatInterface />)
    
    const input = screen.getByPlaceholderText('Ask me anything...')
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    expect(sendButton).not.toBeDisabled()
  })
})