import { renderHook, act, waitFor } from '@testing-library/react';
import { useCourseRequestStatus, useMultipleCourseRequestStatus } from '@/hooks/use-course-request-status';

// Mock WebSocketService
const mockWebSocketService = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  isConnected: jest.fn(),
  on: jest.fn(),
  onConnect: jest.fn(),
  onDisconnect: jest.fn(),
  onError: jest.fn(),
};

jest.mock('@/lib/websocket', () => ({
  WebSocketService: jest.fn().mockImplementation(() => mockWebSocketService),
}));

// Mock useAuth
const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  first_name: 'Test',
  last_name: 'User',
  status: 'active',
  roles: ['student'],
};

jest.mock('@/contexts/auth-context', () => ({
  useAuth: () => ({ user: mockUser }),
}));

// Mock useToastHelpers
const mockToastHelpers = {
  info: jest.fn(),
  warning: jest.fn(),
  error: jest.fn(),
};

jest.mock('@/components/ui/notification-toast', () => ({
  useToastHelpers: () => mockToastHelpers,
}));

describe('useCourseRequestStatus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockWebSocketService.isConnected.mockReturnValue(false);
  });

  it('initializes with default values', () => {
    const { result } = renderHook(() => useCourseRequestStatus());
    
    expect(result.current.status).toBeNull();
    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionError).toBeNull();
    expect(result.current.isProcessing).toBe(false);
    expect(result.current.isCompleted).toBe(false);
    expect(result.current.isApproved).toBe(false);
    expect(result.current.isRejected).toBe(false);
    expect(result.current.progress).toBe(0);
  });

  it('connects automatically when requestId is provided', () => {
    const requestId = 123;
    renderHook(() => useCourseRequestStatus({ requestId }));
    
    expect(mockWebSocketService.connect).toHaveBeenCalled();
    expect(mockWebSocketService.onConnect).toHaveBeenCalled();
    expect(mockWebSocketService.onDisconnect).toHaveBeenCalled();
    expect(mockWebSocketService.onError).toHaveBeenCalled();
  });

  it('does not connect when autoConnect is false', () => {
    const requestId = 123;
    renderHook(() => useCourseRequestStatus({ requestId, autoConnect: false }));
    
    expect(mockWebSocketService.connect).not.toHaveBeenCalled();
  });

  it('handles connection success', async () => {
    const requestId = 123;
    let onConnectCallback: () => void;
    
    mockWebSocketService.onConnect.mockImplementation((callback) => {
      onConnectCallback = callback;
    });
    
    const { result } = renderHook(() => useCourseRequestStatus({ requestId }));
    
    act(() => {
      onConnectCallback();
    });
    
    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
      expect(result.current.connectionError).toBeNull();
    });
  });

  it('handles connection error', async () => {
    const requestId = 123;
    let onErrorCallback: (error: any) => void;
    
    mockWebSocketService.onError.mockImplementation((callback) => {
      onErrorCallback = callback;
    });
    
    const { result } = renderHook(() => useCourseRequestStatus({ requestId }));
    
    act(() => {
      onErrorCallback(new Error('Connection failed'));
    });
    
    await waitFor(() => {
      expect(result.current.connectionError).toBe('Real-time updates connection failed');
      expect(mockToastHelpers.warning).toHaveBeenCalledWith(
        'Connection issue',
        'Real-time updates may be delayed'
      );
    });
  });

  it('handles status change events', async () => {
    const requestId = 123;
    let onStatusChangeCallback: (update: any) => void;
    
    mockWebSocketService.on.mockImplementation((event, callback) => {
      if (event === 'status_change') {
        onStatusChangeCallback = callback;
      }
    });
    
    const { result } = renderHook(() => useCourseRequestStatus({ requestId }));
    
    const statusUpdate = {
      event: 'status_change',
      request_id: requestId,
      data: {
        id: requestId,
        status: 'approved',
        progress: 50,
        message: 'Course approved',
        updated_at: '2023-01-01T00:00:00Z',
      },
    };
    
    act(() => {
      onStatusChangeCallback(statusUpdate);
    });
    
    await waitFor(() => {
      expect(result.current.status).toEqual(statusUpdate.data);
      expect(result.current.isApproved).toBe(true);
      expect(result.current.progress).toBe(50);
      expect(mockToastHelpers.info).toHaveBeenCalledWith(
        'Course Approved',
        'Your course request has been approved!'
      );
    });
  });

  it('handles progress update events', async () => {
    const requestId = 123;
    let onProgressCallback: (update: any) => void;
    
    mockWebSocketService.on.mockImplementation((event, callback) => {
      if (event === 'progress_update') {
        onProgressCallback = callback;
      }
    });
    
    const { result } = renderHook(() => useCourseRequestStatus({ requestId }));
    
    // Set initial status
    act(() => {
      result.current.status = {
        id: requestId,
        status: 'generation_in_progress',
        progress: 25,
        updated_at: '2023-01-01T00:00:00Z',
      };
    });
    
    const progressUpdate = {
      event: 'progress_update',
      request_id: requestId,
      data: {
        id: requestId,
        status: 'generation_in_progress',
        progress: 75,
        updated_at: '2023-01-01T00:00:00Z',
      },
    };
    
    act(() => {
      onProgressCallback(progressUpdate);
    });
    
    await waitFor(() => {
      expect(result.current.progress).toBe(75);
      expect(result.current.isProcessing).toBe(true);
    });
  });

  it('handles generation complete events', async () => {
    const requestId = 123;
    let onGenerationCompleteCallback: (update: any) => void;
    
    mockWebSocketService.on.mockImplementation((event, callback) => {
      if (event === 'generation_complete') {
        onGenerationCompleteCallback = callback;
      }
    });
    
    const { result } = renderHook(() => useCourseRequestStatus({ requestId }));
    
    const completeUpdate = {
      event: 'generation_complete',
      request_id: requestId,
      data: {
        id: requestId,
        status: 'completed',
        progress: 100,
        updated_at: '2023-01-01T00:00:00Z',
        generated_course_id: 456,
      },
    };
    
    act(() => {
      onGenerationCompleteCallback(completeUpdate);
    });
    
    await waitFor(() => {
      expect(result.current.status).toEqual(completeUpdate.data);
      expect(result.current.isCompleted).toBe(true);
      expect(mockToastHelpers.info).toHaveBeenCalledWith(
        'Course Generation Complete',
        'Your course is ready! Course ID: 456',
        expect.objectContaining({
          duration: 0,
          action: expect.objectContaining({
            label: 'View Course',
          }),
        })
      );
    });
  });

  it('handles error events', async () => {
    const requestId = 123;
    let onErrorCallback: (update: any) => void;
    
    mockWebSocketService.on.mockImplementation((event, callback) => {
      if (event === 'error') {
        onErrorCallback = callback;
      }
    });
    
    const { result } = renderHook(() => useCourseRequestStatus({ requestId }));
    
    const errorUpdate = {
      event: 'error',
      request_id: requestId,
      data: {
        id: requestId,
        status: 'error',
        message: 'Processing failed',
        updated_at: '2023-01-01T00:00:00Z',
      },
    };
    
    act(() => {
      onErrorCallback(errorUpdate);
    });
    
    await waitFor(() => {
      expect(result.current.status).toEqual(errorUpdate.data);
      expect(mockToastHelpers.error).toHaveBeenCalledWith(
        'Processing Error',
        'Processing failed'
      );
    });
  });

  it('calls custom onStatusChange callback', async () => {
    const requestId = 123;
    const onStatusChange = jest.fn();
    let onStatusChangeCallback: (update: any) => void;
    
    mockWebSocketService.on.mockImplementation((event, callback) => {
      if (event === 'status_change') {
        onStatusChangeCallback = callback;
      }
    });
    
    renderHook(() => useCourseRequestStatus({ requestId, onStatusChange }));
    
    const statusUpdate = {
      event: 'status_change',
      request_id: requestId,
      data: {
        id: requestId,
        status: 'approved',
        updated_at: '2023-01-01T00:00:00Z',
      },
    };
    
    act(() => {
      onStatusChangeCallback(statusUpdate);
    });
    
    await waitFor(() => {
      expect(onStatusChange).toHaveBeenCalledWith(statusUpdate.data);
    });
  });

  it('provides connect method', () => {
    const { result } = renderHook(() => useCourseRequestStatus({ autoConnect: false }));
    
    expect(typeof result.current.connect).toBe('function');
    
    act(() => {
      result.current.connect(123);
    });
    
    expect(mockWebSocketService.connect).toHaveBeenCalled();
  });

  it('provides disconnect method', () => {
    const { result } = renderHook(() => useCourseRequestStatus({ requestId: 123 }));
    
    expect(typeof result.current.disconnect).toBe('function');
    
    act(() => {
      result.current.disconnect();
    });
    
    expect(mockWebSocketService.disconnect).toHaveBeenCalled();
  });

  it('provides reconnect method', () => {
    const { result } = renderHook(() => useCourseRequestStatus({ requestId: 123 }));
    
    expect(typeof result.current.reconnect).toBe('function');
    
    act(() => {
      result.current.reconnect();
    });
    
    expect(mockWebSocketService.disconnect).toHaveBeenCalled();
  });

  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => useCourseRequestStatus({ requestId: 123 }));
    
    unmount();
    
    expect(mockWebSocketService.disconnect).toHaveBeenCalled();
  });
});

describe('useMultipleCourseRequestStatus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockWebSocketService.isConnected.mockReturnValue(false);
  });

  it('initializes with default values', () => {
    const { result } = renderHook(() => useMultipleCourseRequestStatus([]));
    
    expect(result.current.statuses).toEqual({});
    expect(typeof result.current.connectToRequest).toBe('function');
    expect(typeof result.current.disconnectFromRequest).toBe('function');
    expect(typeof result.current.disconnectAll).toBe('function');
    expect(typeof result.current.getStatus).toBe('function');
    expect(typeof result.current.isConnected).toBe('function');
  });

  it('connects to multiple requests', () => {
    const requestIds = [123, 456, 789];
    renderHook(() => useMultipleCourseRequestStatus(requestIds));
    
    expect(mockWebSocketService.connect).toHaveBeenCalledTimes(3);
  });

  it('returns status for specific request', () => {
    const { result } = renderHook(() => useMultipleCourseRequestStatus([123]));
    
    expect(result.current.getStatus(123)).toBeNull();
    expect(result.current.getStatus(456)).toBeNull();
  });

  it('tracks connection status for specific request', () => {
    mockWebSocketService.isConnected.mockReturnValue(true);
    
    const { result } = renderHook(() => useMultipleCourseRequestStatus([123]));
    
    expect(result.current.isConnected(123)).toBe(false); // Initially false until connection is established
  });

  it('handles status updates for multiple requests', async () => {
    const requestIds = [123, 456];
    let onStatusChangeCallback: (update: any) => void;
    
    mockWebSocketService.on.mockImplementation((event, callback) => {
      if (event === 'status_change') {
        onStatusChangeCallback = callback;
      }
    });
    
    const { result } = renderHook(() => useMultipleCourseRequestStatus(requestIds));
    
    const statusUpdate = {
      event: 'status_change',
      request_id: 123,
      data: {
        id: 123,
        status: 'approved',
        updated_at: '2023-01-01T00:00:00Z',
      },
    };
    
    act(() => {
      onStatusChangeCallback(statusUpdate);
    });
    
    await waitFor(() => {
      expect(result.current.getStatus(123)).toEqual(statusUpdate.data);
    });
  });

  it('disconnects from specific request', () => {
    const { result } = renderHook(() => useMultipleCourseRequestStatus([123]));
    
    act(() => {
      result.current.disconnectFromRequest(123);
    });
    
    expect(mockWebSocketService.disconnect).toHaveBeenCalled();
  });

  it('disconnects from all requests', () => {
    const { result } = renderHook(() => useMultipleCourseRequestStatus([123, 456]));
    
    act(() => {
      result.current.disconnectAll();
    });
    
    expect(mockWebSocketService.disconnect).toHaveBeenCalled();
  });

  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => useMultipleCourseRequestStatus([123, 456]));
    
    unmount();
    
    expect(mockWebSocketService.disconnect).toHaveBeenCalled();
  });
});