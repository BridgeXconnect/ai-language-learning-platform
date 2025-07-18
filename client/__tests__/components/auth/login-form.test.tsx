import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '@/components/auth/login-form';

// Mock the useAuth hook
const mockLogin = jest.fn();
const mockUseAuth = {
  login: mockLogin,
  isLoading: false,
  user: null,
  logout: jest.fn(),
  isAuthenticated: false,
};

// Mock the useToast hook
const mockToast = jest.fn();
const mockUseToast = {
  toast: mockToast,
};

// Mock the useRouter hook
const mockPush = jest.fn();
const mockUseRouter = {
  push: mockPush,
  replace: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  prefetch: jest.fn(),
};

jest.mock('@/contexts/auth-context', () => ({
  useAuth: () => mockUseAuth,
}));

jest.mock('@/hooks/use-toast', () => ({
  useToast: () => mockUseToast,
}));

jest.mock('next/navigation', () => ({
  useRouter: () => mockUseRouter,
}));

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.isLoading = false;
    mockLogin.mockClear();
    mockToast.mockClear();
    mockPush.mockClear();
  });

  it('renders login form with all required fields', () => {
    render(<LoginForm />);
    
    expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
    expect(screen.getByText('Don\'t have an account?')).toBeInTheDocument();
  });

  it('validates email field', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Invalid email address')).toBeInTheDocument();
    });
  });

  it('validates password field', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);
    
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(passwordInput, '123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
    });
  });

  it('submits form with valid credentials', async () => {
    const user = userEvent.setup();
    mockLogin.mockResolvedValueOnce(undefined);
    
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows loading state during form submission', async () => {
    const user = userEvent.setup();
    mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    expect(screen.getByRole('button', { name: 'Logging in...' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Logging in...' })).toBeDisabled();
  });

  it('shows loading state when auth context is loading', () => {
    mockUseAuth.isLoading = true;
    
    render(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: 'Logging in...' });
    expect(submitButton).toBeDisabled();
  });

  it('handles login errors and shows toast', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Invalid credentials';
    mockLogin.mockRejectedValueOnce(new Error(errorMessage));
    
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        variant: 'destructive',
        title: 'Login failed',
        description: errorMessage,
      });
    });
  });

  it('does not show toast for server connection errors', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Cannot connect to server';
    mockLogin.mockRejectedValueOnce(new Error(errorMessage));
    
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled();
    });
    
    expect(mockToast).not.toHaveBeenCalled();
  });

  it('navigates to register page when sign up link is clicked', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);
    
    const signUpLink = screen.getByRole('button', { name: 'Sign up' });
    await user.click(signUpLink);
    
    expect(mockPush).toHaveBeenCalledWith('/register');
  });

  it('disables form fields during submission', async () => {
    const user = userEvent.setup();
    mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
  });

  it('resets form state after submission error', async () => {
    const user = userEvent.setup();
    mockLogin.mockRejectedValueOnce(new Error('Login failed'));
    
    render(<LoginForm />);
    
    const emailInput = screen.getByLabelText('Email');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Login' });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
    });
    
    expect(emailInput).not.toBeDisabled();
    expect(passwordInput).not.toBeDisabled();
  });
});