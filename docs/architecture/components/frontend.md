# Frontend Architecture

## Overview
The frontend of the Dynamic English Course Creator App is a modern React-based single-page application (SPA) that provides role-specific portals and a seamless user experience across all functionalities.

## Core Features
- Role-based portal interfaces
- Responsive design
- Real-time updates
- Offline capabilities
- Progressive Web App (PWA)
- Accessibility compliance

## Technologies
- React 18.2+
- TypeScript
- Vite (build tool)
- TanStack Query (data fetching)
- Zustand (state management)
- TailwindCSS (styling)
- React Router v6 (routing)
- React Hook Form (form handling)
- Framer Motion (animations)

## Architecture Patterns
```typescript
// Feature-based Structure
src/
  ├── components/         # Shared components
  ├── context/           # React context providers
  ├── hooks/             # Custom hooks
  ├── pages/             # Route components
  ├── services/          # API services
  ├── stores/            # State management
  ├── types/             # TypeScript definitions
  └── utils/             # Helper functions

// Component Architecture
interface Props {
  data: CourseData;
  onUpdate: (id: string) => void;
  isLoading?: boolean;
}

const CourseCard: React.FC<Props> = ({
  data,
  onUpdate,
  isLoading = false,
}) => {
  // Component implementation
};
```

## State Management
### Global State (Zustand)
```typescript
interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

interface UIStore {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

### Server State (TanStack Query)
```typescript
// Query Hooks
const useCourses = () => {
  return useQuery({
    queryKey: ['courses'],
    queryFn: fetchCourses,
    staleTime: 5 * 60 * 1000,
  });
};

// Mutation Hooks
const useUpdateCourse = () => {
  return useMutation({
    mutationFn: updateCourse,
    onSuccess: () => {
      queryClient.invalidateQueries(['courses']);
    },
  });
};
```

## Performance Optimization
- Code splitting by route
- Lazy loading of components
- Image optimization
- Caching strategies
- Bundle size optimization
- Performance monitoring

## Security Measures
- JWT token management
- XSS prevention
- CSRF protection
- Input validation
- Secure data storage
- API error handling

## Testing Strategy
```typescript
// Component Testing
describe('CourseCard', () => {
  it('renders course information correctly', () => {
    render(<CourseCard data={mockData} onUpdate={mockFn} />);
    expect(screen.getByText(mockData.title)).toBeInTheDocument();
  });
});

// Hook Testing
describe('useAuth', () => {
  it('handles login successfully', async () => {
    const { result } = renderHook(() => useAuth());
    await act(() => result.current.login(mockCredentials));
    expect(result.current.isAuthenticated).toBe(true);
  });
});
```

## Accessibility
- WCAG 2.1 compliance
- Keyboard navigation
- Screen reader support
- Color contrast
- Focus management
- ARIA attributes

## Performance Metrics
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- First Input Delay: < 100ms 