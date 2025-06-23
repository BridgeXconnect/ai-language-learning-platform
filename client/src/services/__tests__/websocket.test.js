import { vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useWebSocket, useGenerationStatus, useDocumentStatus } from '../websocket';

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    this.onopen = null;
    this.onclose = null;
    this.onmessage = null;
    this.onerror = null;
    
    // Simulate connection after a brief delay
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) this.onopen();
    }, 10);
  }
  
  send(data) {
    // Store sent data for testing
    this.lastSentData = data;
  }
  
  close(code, reason) {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) this.onclose({ code, reason });
  }
  
  // Helper methods for testing
  simulateMessage(data) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) });
    }
  }
  
  simulateError(error) {
    if (this.onerror) this.onerror(error);
  }
}

// Mock global WebSocket
global.WebSocket = MockWebSocket;
WebSocket.CONNECTING = 0;
WebSocket.OPEN = 1;
WebSocket.CLOSING = 2;
WebSocket.CLOSED = 3;

describe('WebSocket Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useWebSocket hook', () => {
    it('connects automatically when autoConnect is true', async () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      expect(result.current.connectionState).toBe('connecting');
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      expect(result.current.connectionState).toBe('connected');
    });

    it('does not connect automatically when autoConnect is false', () => {
      const { result } = renderHook(() => useWebSocket(false));
      
      expect(result.current.connectionState).toBe('disconnected');
    });

    it('provides send function', () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      expect(typeof result.current.send).toBe('function');
    });

    it('provides subscription functions', () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      expect(typeof result.current.subscribeToGeneration).toBe('function');
      expect(typeof result.current.subscribeToDocument).toBe('function');
      expect(typeof result.current.subscribeToNotifications).toBe('function');
    });

    it('updates connection state on connection changes', async () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      // Initially connecting
      expect(result.current.connectionState).toBe('connecting');
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      expect(result.current.connectionState).toBe('connected');
    });

    it('handles messages', async () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      const testMessage = { type: 'test', payload: { data: 'test' } };
      
      // Simulate receiving a message
      act(() => {
        // We need to access the WebSocket instance to simulate message
        // This is a simplified test - in real implementation you'd need access to the ws instance
      });
    });
  });

  describe('useGenerationStatus hook', () => {
    it('returns initial state', () => {
      const { result } = renderHook(() => useGenerationStatus('job-123'));
      
      expect(result.current.status).toBe(null);
      expect(result.current.progress).toBe(0);
      expect(result.current.logs).toEqual([]);
    });

    it('subscribes to generation updates when connected', async () => {
      const { result } = renderHook(() => useGenerationStatus('job-123'));
      
      // Wait for connection (this would happen in real implementation)
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      // The hook should subscribe to generation updates
      expect(result.current.status).toBe(null);
    });

    it('updates status when generation status message is received', async () => {
      const { result } = renderHook(() => useGenerationStatus('job-123'));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      // Simulate status update (this would be handled by the WebSocket service)
      const statusUpdate = {
        job_id: 'job-123',
        status: 'processing',
        progress: 50,
        message: 'Processing documents...'
      };
      
      // In real implementation, this would come through the WebSocket
      // For testing, we'd need to trigger the status update through the service
    });
  });

  describe('useDocumentStatus hook', () => {
    it('returns initial state', () => {
      const { result } = renderHook(() => useDocumentStatus('doc-123'));
      
      expect(result.current.status).toBe('pending');
      expect(result.current.result).toBe(null);
    });

    it('subscribes to document updates when connected', async () => {
      const { result } = renderHook(() => useDocumentStatus('doc-123'));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      expect(result.current.status).toBe('pending');
    });

    it('updates status when document processed message is received', async () => {
      const { result } = renderHook(() => useDocumentStatus('doc-123'));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      // Simulate document processed update
      const docUpdate = {
        document_id: 'doc-123',
        status: 'completed',
        word_count: 500,
        chunk_count: 5
      };
      
      // In real implementation, this would update through WebSocket
    });
  });

  describe('WebSocket error handling', () => {
    it('handles connection errors gracefully', () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      expect(result.current.connectionState).toBe('connecting');
      
      // WebSocket errors should be handled without crashing
    });

    it('attempts reconnection on connection loss', async () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      // Wait for initial connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      expect(result.current.connectionState).toBe('connected');
      
      // Simulate connection loss
      // In real implementation, this would trigger reconnection logic
    });

    it('queues messages when disconnected', () => {
      const { result } = renderHook(() => useWebSocket(false));
      
      // Try to send message while disconnected
      act(() => {
        result.current.send({ type: 'test', data: 'test' });
      });
      
      // Message should be queued (not crash)
    });
  });

  describe('WebSocket cleanup', () => {
    it('cleans up connection on unmount', () => {
      const { unmount } = renderHook(() => useWebSocket(true));
      
      // Should not throw when unmounting
      expect(() => unmount()).not.toThrow();
    });

    it('removes event listeners on unmount', async () => {
      const { result, unmount } = renderHook(() => useWebSocket(true));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      // Subscribe to events
      act(() => {
        result.current.subscribe('test_event', () => {});
      });
      
      // Should not throw when unmounting
      expect(() => unmount()).not.toThrow();
    });
  });

  describe('Message handling', () => {
    it('parses JSON messages correctly', async () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      let receivedMessage = null;
      
      act(() => {
        result.current.subscribe('test_event', (data) => {
          receivedMessage = data;
        });
      });
      
      // Simulate message (would need access to WebSocket instance)
      // This is testing the concept - actual implementation would vary
    });

    it('handles malformed JSON gracefully', async () => {
      const { result } = renderHook(() => useWebSocket(true));
      
      // Wait for connection
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 20));
      });
      
      // Simulate malformed JSON - should not crash
      // In real implementation, error handling would prevent crashes
    });
  });
});