import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import StudentPortal from '../student/page'

// Mock the auth context
jest.mock('@/contexts/auth-context', () => ({
  useAuth: () => ({
    user: { 
      first_name: 'John', 
      username: 'john.doe',
      id: '1',
      email: 'john@example.com',
      role: 'student'
    }
  })
}))

// Mock the toast hook
jest.mock('@/components/ui/use-toast', () => ({
  toast: jest.fn()
}))

// Mock the AI Chat Interface
jest.mock('@/components/ai/ai-chat-interface', () => ({
  AIChatInterface: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="ai-chat-interface">
      <button onClick={onClose} data-testid="close-chat">Close</button>
    </div>
  )
}))

// Mock the Progress Tracker
jest.mock('@/components/learning/progress-tracker', () => ({
  ProgressTracker: ({ variant, onModuleClick }: { variant: string; onModuleClick: (id: string) => void }) => (
    <div data-testid={`progress-tracker-${variant}`}>
      <button onClick={() => onModuleClick('1')} data-testid="module-click">Module 1</button>
    </div>
  )
}))

// Mock Next.js Link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href} data-testid="next-link">{children}</a>
  )
})

describe('StudentPortal', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the student dashboard', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('Learning Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Welcome back, John! Continue your learning journey.')).toBeInTheDocument()
    })
  })

  it('shows loading state initially', () => {
    render(<StudentPortal />)
    
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('displays user profile stats', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('Level')).toBeInTheDocument()
      expect(screen.getByText('Streak')).toBeInTheDocument()
      expect(screen.getByText('Time Spent')).toBeInTheDocument()
      expect(screen.getByText('Achievements')).toBeInTheDocument()
    })
  })

  it('shows active courses section', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('Continue Learning')).toBeInTheDocument()
      expect(screen.getByText('Advanced JavaScript Programming')).toBeInTheDocument()
      expect(screen.getByText('Data Structures & Algorithms')).toBeInTheDocument()
    })
  })

  it('shows upcoming deadlines', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('Upcoming Deadlines')).toBeInTheDocument()
      expect(screen.getByText('Final Project Submission')).toBeInTheDocument()
      expect(screen.getByText('Quiz: Tree Traversal')).toBeInTheDocument()
    })
  })

  it('shows AI recommendations', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('Recommended for You')).toBeInTheDocument()
      expect(screen.getByText('React Advanced Patterns')).toBeInTheDocument()
      expect(screen.getByText('Algorithm Practice Problems')).toBeInTheDocument()
    })
  })

  it('opens AI chat when AI Tutor button is clicked', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const aiTutorButton = screen.getByText('AI Tutor')
      fireEvent.click(aiTutorButton)
      
      expect(screen.getByTestId('ai-chat-interface')).toBeInTheDocument()
    })
  })

  it('closes AI chat when close button is clicked', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const aiTutorButton = screen.getByText('AI Tutor')
      fireEvent.click(aiTutorButton)
      
      const closeButton = screen.getByTestId('close-chat')
      fireEvent.click(closeButton)
      
      expect(screen.queryByTestId('ai-chat-interface')).not.toBeInTheDocument()
    })
  })

  it('navigates to course when Continue button is clicked', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const continueButtons = screen.getAllByText('Continue')
      fireEvent.click(continueButtons[0])
      
      // Check if the navigation would happen (mocked in real scenario)
      expect(window.location.href).toBe('http://localhost/student/courses/1/continue')
    })
  })

  it('switches between tabs correctly', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const coursesTab = screen.getByRole('tab', { name: 'My Courses' })
      fireEvent.click(coursesTab)
      
      expect(screen.getAllByText('Advanced JavaScript Programming')[0]).toBeInTheDocument()
    })
  })

  it('displays progress tracker in progress tab', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const progressTab = screen.getByRole('tab', { name: 'Progress' })
      fireEvent.click(progressTab)
      
      expect(screen.getByTestId('progress-tracker-linear')).toBeInTheDocument()
    })
  })

  it('displays achievements in achievements tab', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const achievementsTab = screen.getByRole('tab', { name: 'Achievements' })
      fireEvent.click(achievementsTab)
      
      expect(screen.getByTestId('progress-tracker-skill-tree')).toBeInTheDocument()
    })
  })

  it('handles course card interactions', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const coursesTab = screen.getByRole('tab', { name: 'My Courses' })
      fireEvent.click(coursesTab)
      
      const viewDetailsButton = screen.getAllByText('View Details')[0]
      fireEvent.click(viewDetailsButton)
      
      // This would trigger course details view in real scenario
    })
  })

  it('shows course instructors and due dates', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const coursesTab = screen.getByRole('tab', { name: 'My Courses' })
      fireEvent.click(coursesTab)
      
      expect(screen.getByText('Instructor: Dr. Sarah Johnson')).toBeInTheDocument()
      expect(screen.getByText('Due: 1/20/2024')).toBeInTheDocument()
    })
  })

  it('displays course progress bars', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const coursesTab = screen.getByRole('tab', { name: 'My Courses' })
      fireEvent.click(coursesTab)
      
      expect(screen.getByText('75%')).toBeInTheDocument()
      expect(screen.getByText('45%')).toBeInTheDocument()
      expect(screen.getByText('90%')).toBeInTheDocument()
    })
  })

  it('shows next lesson information', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('Next: Async/Await Patterns')).toBeInTheDocument()
      expect(screen.getByText('Next: Binary Search Trees')).toBeInTheDocument()
    })
  })

  it('handles module clicks in progress tracker', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      const progressTab = screen.getByRole('tab', { name: 'Progress' })
      fireEvent.click(progressTab)
      
      const moduleButton = screen.getByTestId('module-click')
      fireEvent.click(moduleButton)
      
      // This would trigger module selection in real scenario
    })
  })

  it('shows badge priorities for deadlines', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('high')).toBeInTheDocument()
      expect(screen.getByText('medium')).toBeInTheDocument()
    })
  })

  it('displays user level and XP progress', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument() // Level
      expect(screen.getByText('2450/3000 XP')).toBeInTheDocument()
    })
  })

  it('shows streak information', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('7')).toBeInTheDocument() // Streak days
      expect(screen.getByText('days in a row')).toBeInTheDocument()
    })
  })

  it('displays total learning time', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('39h')).toBeInTheDocument() // 2340 minutes = 39 hours
      expect(screen.getByText('0m total learning time')).toBeInTheDocument()
    })
  })

  it('shows achievement count', async () => {
    render(<StudentPortal />)
    
    await waitFor(() => {
      expect(screen.getByText('12')).toBeInTheDocument() // Achievement count
      expect(screen.getByText('badges earned')).toBeInTheDocument()
    })
  })
})