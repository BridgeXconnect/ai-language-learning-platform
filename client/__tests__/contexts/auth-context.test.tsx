import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/contexts/auth-context';
import { UserRole } from '@/lib/config';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Declare mock variables at the top level
let mockAuthApi: any;
let mockToast: any;
const mockPush = jest.fn();
let mockRouter: any;

jest.mock('@/lib/api', () => {
  mockAuthApi = {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    getProfile: jest.fn(),
  };
  return {
    authApi: mockAuthApi,
    testConnection: jest.fn(),
  };
});

jest.mock('@/hooks/use-toast', () => {
  mockToast = jest.fn();
  return {
    useToast: () => ({ toast: mockToast }),
  };
});

jest.mock('next/navigation', () => {
  mockRouter = {
    push: mockPush,
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  };
  return {
    useRouter: () => mockRouter,
  };
});

// Test component to access auth context
function TestComponent() {
  const auth = useAuth();
  
  return (
    <div>
      <div data-testid="user">{auth.user ? auth.user.email : 'null'}</div>
      <div data-testid="loading">{auth.isLoading.toString()}</div>
      <div data-testid="roles">{auth.roles.join(',')}</div>
      <button onClick={() => auth.login({ email: 'test@example.com', password: 'password' })}>
        Login
      </button>
      <button onClick={() => auth.register({ email: 'test@example.com', password: 'password' })}>
        Register
      </button>
      <button onClick={() => auth.logout()}>Logout</button>
      <div data-testid="has-sales-role">{auth.hasRole(UserRole.SALES).toString()}</div>
    </div>
  );
}

describe('AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
    mockLocalStorage.setItem.mockImplementation(() => {});
    mockLocalStorage.removeItem.mockImplementation(() => {});
    mockToast.mockClear();
    mockPush.mockClear();
    mockAuthApi.login.mockClear();
    mockAuthApi.register.mockClear();
    mockAuthApi.logout.mockClear();
    mockAuthApi.getProfile.mockClear();
  });

  it('provides auth context values', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('user')).toHaveTextContent('null');
    expect(screen.getByTestId('loading')).toHaveTextContent('true');
    expect(screen.getByTestId('roles')).toHaveTextContent('');
    expect(screen.getByTestId('has-sales-role')).toHaveTextContent('false');
  });

  it('throws error when useAuth is used outside provider', () => {
    const ConsoleError = console.error;
    console.error = jest.fn();
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');
    
    console.error = ConsoleError;
  });

  it('checks for existing auth on mount', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      status: 'active',
      roles: [UserRole.STUDENT],
    };

    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getProfile.mockResolvedValue(mockUser);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
      expect(screen.getByTestId('roles')).toHaveTextContent('student');
    });
  });

  it('clears invalid tokens on auth check failure', async () => {
    mockLocalStorage.getItem.mockReturnValue('invalid-token');
    mockAuthApi.getProfile.mockRejectedValue(new Error('Unauthorized'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('authToken');
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('refreshToken');
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });
  });

  it('handles successful login with profile fetch', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      status: 'active',
      roles: [UserRole.SALES],
    };

    mockAuthApi.login.mockResolvedValue({ user: mockUser });
    mockAuthApi.getProfile.mockResolvedValue(mockUser);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Login' }).click();
    });

    await waitFor(() => {
      expect(mockAuthApi.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
      expect(mockAuthApi.getProfile).toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      expect(mockPush).toHaveBeenCalledWith('/sales');
    });
  });

  it('handles login with profile fetch failure using fallback', async () => {
    const mockLoginResponse = {
      user: {
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        roles: [UserRole.STUDENT],
      },
    };

    mockAuthApi.login.mockResolvedValue(mockLoginResponse);
    mockAuthApi.getProfile.mockRejectedValue(new Error('Profile fetch failed'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Login' }).click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      expect(mockPush).toHaveBeenCalledWith('/student');
    });
  });

  it('handles login failure with error toast', async () => {
    const errorMessage = 'Invalid credentials';
    mockAuthApi.login.mockRejectedValue(new Error(errorMessage));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Login' }).click();
    });

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Login failed',
        description: errorMessage,
      });
    });
  });

  it('handles successful registration', async () => {
    mockAuthApi.register.mockResolvedValue(undefined);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Register' }).click();
    });

    await waitFor(() => {
      expect(mockAuthApi.register).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Registration successful',
        description: 'You can now log in with your credentials',
      });
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('handles registration failure with error toast', async () => {
    const errorMessage = 'Email already exists';
    mockAuthApi.register.mockRejectedValue(new Error(errorMessage));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Register' }).click();
    });

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Registration failed',
        description: errorMessage,
      });
    });
  });

  it('handles logout', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      status: 'active',
      roles: [UserRole.STUDENT],
    };

    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getProfile.mockResolvedValue(mockUser);
    mockAuthApi.logout.mockResolvedValue(undefined);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Logout' }).click();
    });

    await waitFor(() => {
      expect(mockAuthApi.logout).toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('continues logout even if API fails', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      status: 'active',
      roles: [UserRole.STUDENT],
    };

    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getProfile.mockResolvedValue(mockUser);
    mockAuthApi.logout.mockRejectedValue(new Error('Logout failed'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });

    await act(async () => {
      screen.getByRole('button', { name: 'Logout' }).click();
    });

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('checks user roles correctly', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      status: 'active',
      roles: [UserRole.SALES, UserRole.COURSE_MANAGER],
    };

    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getProfile.mockResolvedValue(mockUser);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('has-sales-role')).toHaveTextContent('true');
      expect(screen.getByTestId('roles')).toHaveTextContent('sales,course_manager');
    });
  });

  it('redirects to appropriate portal based on user role', async () => {
    const testCases = [
      { roles: [UserRole.SALES], expectedPath: '/sales' },
      { roles: [UserRole.COURSE_MANAGER], expectedPath: '/course-manager' },
      { roles: [UserRole.TRAINER], expectedPath: '/trainer' },
      { roles: [UserRole.STUDENT], expectedPath: '/student' },
      { roles: [], expectedPath: '/' },
    ];

    for (const { roles, expectedPath } of testCases) {
      jest.clearAllMocks();
      mockPush.mockClear();
      mockAuthApi.login.mockClear();
      mockAuthApi.getProfile.mockClear();

      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        status: 'active',
        roles,
      };

      mockAuthApi.login.mockResolvedValue({ user: mockUser });
      mockAuthApi.getProfile.mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });

      await act(async () => {
        screen.getByRole('button', { name: 'Login' }).click();
      });

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith(expectedPath);
      });
    }
  });
});