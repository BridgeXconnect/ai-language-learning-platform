import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ProgressTracker } from '../progress-tracker'

const mockProgressData = {
  overall: {
    percentage: 75,
    completedItems: 15,
    totalItems: 20,
    timeSpent: 1200,
    streak: 5,
    level: 3,
    xp: 2500,
    nextLevelXp: 3000
  },
  skills: [
    {
      id: '1',
      name: 'JavaScript',
      category: 'Programming',
      level: 2,
      progress: 60,
      maxLevel: 5,
      prerequisites: [],
      unlocked: true,
      mastery: 'intermediate' as const
    },
    {
      id: '2',
      name: 'React',
      category: 'Frontend',
      level: 1,
      progress: 30,
      maxLevel: 5,
      prerequisites: ['JavaScript'],
      unlocked: false,
      mastery: 'beginner' as const
    }
  ],
  modules: [
    {
      id: '1',
      title: 'Introduction to Programming',
      description: 'Learn the basics of programming',
      progress: 80,
      status: 'in_progress' as const,
      estimatedTime: 120,
      completedTime: 96,
      lessons: [
        {
          id: '1',
          title: 'Variables and Data Types',
          type: 'video' as const,
          status: 'completed' as const,
          progress: 100,
          score: 95,
          timeSpent: 30
        },
        {
          id: '2',
          title: 'Functions',
          type: 'reading' as const,
          status: 'in_progress' as const,
          progress: 50,
          timeSpent: 15
        }
      ]
    },
    {
      id: '2',
      title: 'Advanced JavaScript',
      description: 'Master advanced JavaScript concepts',
      progress: 45,
      status: 'available' as const,
      estimatedTime: 180,
      lessons: []
    }
  ],
  achievements: [
    {
      id: '1',
      title: 'First Steps',
      description: 'Complete your first lesson',
      icon: '🎯',
      category: 'completion' as const,
      earned: true,
      earnedAt: new Date('2024-01-01')
    },
    {
      id: '2',
      title: 'Speed Learner',
      description: 'Complete 5 lessons in one day',
      icon: '⚡',
      category: 'streak' as const,
      earned: false,
      progress: 3,
      target: 5
    }
  ],
  timeline: [
    {
      id: '1',
      type: 'lesson_completed' as const,
      title: 'Variables and Data Types',
      description: 'Completed with 95% score',
      timestamp: new Date('2024-01-10'),
      points: 100
    },
    {
      id: '2',
      type: 'achievement_earned' as const,
      title: 'First Steps',
      description: 'Earned First Steps achievement',
      timestamp: new Date('2024-01-01'),
      points: 50
    }
  ]
}

describe('ProgressTracker', () => {
  it('renders linear progress variant', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} />)
    
    expect(screen.getByText('Overall Progress')).toBeInTheDocument()
    expect(screen.getByText('Course Modules')).toBeInTheDocument()
    expect(screen.getByText('75%')).toBeInTheDocument()
    expect(screen.getByText('15/20 completed')).toBeInTheDocument()
  })

  it('renders circular progress variant', () => {
    render(<ProgressTracker variant="circular" data={mockProgressData} />)
    
    expect(screen.getByText('Introduction to Programming')).toBeInTheDocument()
    expect(screen.getByText('Advanced JavaScript')).toBeInTheDocument()
    expect(screen.getByText('80%')).toBeInTheDocument()
    expect(screen.getByText('45%')).toBeInTheDocument()
  })

  it('renders skill tree variant', () => {
    render(<ProgressTracker variant="skill-tree" data={mockProgressData} />)
    
    expect(screen.getByText('Skill Progression')).toBeInTheDocument()
    expect(screen.getByText('JavaScript')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Programming')).toBeInTheDocument()
    expect(screen.getByText('Frontend')).toBeInTheDocument()
  })

  it('renders timeline variant', () => {
    render(<ProgressTracker variant="timeline" data={mockProgressData} />)
    
    expect(screen.getByText('Learning Timeline')).toBeInTheDocument()
    expect(screen.getByText('Variables and Data Types')).toBeInTheDocument()
    expect(screen.getByText('First Steps')).toBeInTheDocument()
  })

  it('displays achievements when enabled', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} showAchievements={true} />)
    
    expect(screen.getByText('Achievements')).toBeInTheDocument()
expect(screen.getAllByText('First Steps').length).toBeGreaterThan(0)
    expect(screen.getByText('Speed Learner')).toBeInTheDocument()
    expect(screen.getByText('🎯')).toBeInTheDocument()
    expect(screen.getByText('⚡')).toBeInTheDocument()
  })

  it('displays timeline when enabled', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} showTimeline={true} />)
    
    expect(screen.getByText('Learning Timeline')).toBeInTheDocument()
    expect(screen.getByText('Variables and Data Types')).toBeInTheDocument()
    expect(screen.getByText('Completed with 95% score')).toBeInTheDocument()
  })

  it('calls onModuleClick when module is clicked', () => {
    const mockOnModuleClick = jest.fn()
    render(<ProgressTracker variant="linear" data={mockProgressData} onModuleClick={mockOnModuleClick} />)
    
    const moduleCard = screen.getByText('Introduction to Programming').closest('div')
    fireEvent.click(moduleCard!)
    
    expect(mockOnModuleClick).toHaveBeenCalledWith('1')
  })

  it('shows correct module status badges', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} />)
    
    expect(screen.getByText('in progress')).toBeInTheDocument()
    expect(screen.getByText('available')).toBeInTheDocument()
  })

  it('displays lesson progress correctly', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} />)
    
    expect(screen.getByText('2 lessons')).toBeInTheDocument()
    expect(screen.getByText('Est. 120min')).toBeInTheDocument()
    expect(screen.getByText('Est. 180min')).toBeInTheDocument()
  })

  it('shows locked skills with prerequisites', () => {
    render(<ProgressTracker variant="skill-tree" data={mockProgressData} />)
    
    expect(screen.getByText('Requires: JavaScript')).toBeInTheDocument()
  })

  it('displays achievement progress for unearned achievements', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} showAchievements={true} />)
    
    expect(screen.getByText('3/5')).toBeInTheDocument()
  })

  it('shows earned achievement dates', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} showAchievements={true} />)
    
    expect(screen.getByText('Earned 1/1/2024')).toBeInTheDocument()
  })

  it('displays XP progress correctly', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} />)
    
    expect(screen.getByText('2500/3000 XP')).toBeInTheDocument()
    expect(screen.getByText('Level 3')).toBeInTheDocument()
  })

  it('shows time spent statistics', () => {
    render(<ProgressTracker variant="linear" data={mockProgressData} />)
    
    expect(screen.getByText('20h 0m spent')).toBeInTheDocument()
    expect(screen.getByText('5 day streak')).toBeInTheDocument()
  })

  it('handles circular progress Continue button click', () => {
    const mockOnModuleClick = jest.fn()
    render(<ProgressTracker variant="circular" data={mockProgressData} onModuleClick={mockOnModuleClick} />)
    
    const continueButtons = screen.getAllByText('Continue')
    fireEvent.click(continueButtons[0])
    
    expect(mockOnModuleClick).toHaveBeenCalledWith('1')
  })

  it('shows Review button for completed modules', () => {
    const completedModuleData = {
      ...mockProgressData,
      modules: [
        {
          ...mockProgressData.modules[0],
          status: 'completed' as const,
          progress: 100
        }
      ]
    }
    
    render(<ProgressTracker variant="circular" data={completedModuleData} />)
    
    expect(screen.getByText('Review')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <ProgressTracker variant="linear" data={mockProgressData} className="custom-class" />
    )
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
})