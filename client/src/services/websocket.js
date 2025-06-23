class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000; // Start with 1 second
    this.listeners = new Map();
    this.isConnecting = false;
    this.messageQueue = [];
  }

  connect(url = null) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;
    const wsUrl = url || `${import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000'}/ws`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.isConnecting = false;
      this.handleReconnect();
    }
  }

  setupEventHandlers() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.reconnectInterval = 1000;
      
      // Send queued messages
      while (this.messageQueue.length > 0) {
        const message = this.messageQueue.shift();
        this.send(message);
      }
      
      // Notify listeners
      this.emit('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.isConnecting = false;
      this.emit('disconnected', { code: event.code, reason: event.reason });
      
      // Attempt to reconnect if not intentionally closed
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.handleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isConnecting = false;
      this.emit('error', error);
    };
  }

  handleMessage(data) {
    const { type, payload } = data;
    
    switch (type) {
      case 'generation_status':
        this.emit('generation_status', payload);
        break;
      case 'document_processed':
        this.emit('document_processed', payload);
        break;
      case 'course_generation_complete':
        this.emit('course_generation_complete', payload);
        break;
      case 'notification':
        this.emit('notification', payload);
        break;
      default:
        this.emit(type, payload);
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      this.emit('max_reconnect_attempts');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
    
    setTimeout(() => {
      this.connect();
    }, this.reconnectInterval);
    
    // Exponential backoff
    this.reconnectInterval = Math.min(this.reconnectInterval * 2, 30000);
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      // Queue message for later
      this.messageQueue.push(message);
    }
  }

  // Subscribe to course generation updates
  subscribeToGeneration(jobId) {
    this.send({
      type: 'subscribe_generation',
      job_id: jobId
    });
  }

  // Subscribe to document processing updates
  subscribeToDocument(documentId) {
    this.send({
      type: 'subscribe_document',
      document_id: documentId
    });
  }

  // Subscribe to user notifications
  subscribeToNotifications(userId) {
    this.send({
      type: 'subscribe_notifications',
      user_id: userId
    });
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error);
        }
      });
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.listeners.clear();
    this.messageQueue = [];
    this.reconnectAttempts = 0;
  }

  getConnectionState() {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

// Create singleton instance
const wsService = new WebSocketService();

// React hook for using WebSocket
import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (autoConnect = true) => {
  const [connectionState, setConnectionState] = useState('disconnected');
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const listenersRef = useRef([]);

  useEffect(() => {
    if (autoConnect) {
      wsService.connect();
    }

    const updateConnectionState = () => {
      setConnectionState(wsService.getConnectionState());
    };

    const handleMessage = (data) => {
      setLastMessage({ ...data, timestamp: Date.now() });
    };

    const handleError = (error) => {
      setError(error);
    };

    const handleConnected = () => {
      setConnectionState('connected');
      setError(null);
    };

    const handleDisconnected = () => {
      setConnectionState('disconnected');
    };

    // Register event listeners
    wsService.on('connected', handleConnected);
    wsService.on('disconnected', handleDisconnected);
    wsService.on('error', handleError);
    
    // Store listeners for cleanup
    listenersRef.current = [
      { event: 'connected', handler: handleConnected },
      { event: 'disconnected', handler: handleDisconnected },
      { event: 'error', handler: handleError }
    ];

    // Initial state update
    updateConnectionState();

    return () => {
      // Cleanup listeners
      listenersRef.current.forEach(({ event, handler }) => {
        wsService.off(event, handler);
      });
    };
  }, [autoConnect]);

  const subscribe = (event, callback) => {
    wsService.on(event, callback);
    
    // Add to cleanup list
    listenersRef.current.push({ event, handler: callback });
    
    return () => wsService.off(event, callback);
  };

  const send = (message) => {
    wsService.send(message);
  };

  const subscribeToGeneration = (jobId) => {
    wsService.subscribeToGeneration(jobId);
  };

  const subscribeToDocument = (documentId) => {
    wsService.subscribeToDocument(documentId);
  };

  const subscribeToNotifications = (userId) => {
    wsService.subscribeToNotifications(userId);
  };

  return {
    connectionState,
    lastMessage,
    error,
    subscribe,
    send,
    subscribeToGeneration,
    subscribeToDocument,
    subscribeToNotifications,
    connect: () => wsService.connect(),
    disconnect: () => wsService.disconnect()
  };
};

// Hook specifically for generation status tracking
export const useGenerationStatus = (jobId) => {
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const { subscribe, subscribeToGeneration, connectionState } = useWebSocket();

  useEffect(() => {
    if (jobId && connectionState === 'connected') {
      subscribeToGeneration(jobId);
    }
  }, [jobId, connectionState, subscribeToGeneration]);

  useEffect(() => {
    const unsubscribe = subscribe('generation_status', (data) => {
      if (data.job_id === jobId) {
        setStatus(data.status);
        setProgress(data.progress || 0);
        
        if (data.message) {
          setLogs(prev => [...prev, {
            timestamp: new Date().toISOString(),
            message: data.message,
            stage: data.stage || 'processing'
          }]);
        }
      }
    });

    return unsubscribe;
  }, [jobId, subscribe]);

  return { status, progress, logs };
};

// Hook for document processing status
export const useDocumentStatus = (documentId) => {
  const [status, setStatus] = useState('pending');
  const [result, setResult] = useState(null);
  const { subscribe, subscribeToDocument, connectionState } = useWebSocket();

  useEffect(() => {
    if (documentId && connectionState === 'connected') {
      subscribeToDocument(documentId);
    }
  }, [documentId, connectionState, subscribeToDocument]);

  useEffect(() => {
    const unsubscribe = subscribe('document_processed', (data) => {
      if (data.document_id === documentId) {
        setStatus(data.status);
        setResult(data);
      }
    });

    return unsubscribe;
  }, [documentId, subscribe]);

  return { status, result };
};

export default wsService;