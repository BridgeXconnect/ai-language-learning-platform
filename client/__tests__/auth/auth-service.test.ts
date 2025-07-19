import { authService } from '@/lib/auth-service';
import { ApiError } from '@/lib/api';

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock document.cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: '',
});

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    localStorageMock.setItem.mockImplementation(() => {});
    localStorageMock.removeItem.mockImplementation(() => {});
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const credentials = { email: 'test@example.com', password: 'password123' };
      const result = await authService.login(credentials);

      expect(result).toEqual(mockResponse);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'mock-access-token');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token');
    });

    it('should throw ApiError for invalid credentials', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: 'Invalid credentials' }),
      });

      const credentials = { email: 'test@example.com', password: 'wrongpassword' };

      await expect(authService.login(credentials)).rejects.toThrow(ApiError);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    });

    it('should handle network errors', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const credentials = { email: 'test@example.com', password: 'password123' };

      await expect(authService.login(credentials)).rejects.toThrow();
    });
  });

  describe('refreshToken', () => {
    it('should successfully refresh token', async () => {
      localStorageMock.getItem.mockReturnValue('mock-refresh-token');

      const mockResponse = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
        token_type: 'bearer',
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await authService.refreshToken();

      expect(result).toBe(true);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'new-access-token');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'new-refresh-token');
    });

    it('should return false when no refresh token exists', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = await authService.refreshToken();

      expect(result).toBe(false);
      expect(fetch).not.toHaveBeenCalled();
    });

    it('should handle refresh token failure', async () => {
      localStorageMock.getItem.mockReturnValue('invalid-refresh-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      const result = await authService.refreshToken();

      expect(result).toBe(false);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('getProfile', () => {
    it('should fetch user profile successfully', async () => {
      const mockProfile = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        roles: ['user'],
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockProfile),
      });

      const result = await authService.getProfile();

      expect(result).toEqual(mockProfile);
    });

    it('should handle invalid profile data', async () => {
      const invalidProfile = { name: 'test' }; // Missing required fields

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(invalidProfile),
      });

      await expect(authService.getProfile()).rejects.toThrow('Invalid profile data received');
    });
  });

  describe('logout', () => {
    it('should logout and clear tokens', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      await authService.logout();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    });

    it('should clear tokens even if server call fails', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Server error'));

      await authService.logout();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when access token exists', () => {
      localStorageMock.getItem.mockReturnValue('mock-access-token');

      const result = authService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false when no access token exists', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = authService.isAuthenticated();

      expect(result).toBe(false);
    });
  });
});