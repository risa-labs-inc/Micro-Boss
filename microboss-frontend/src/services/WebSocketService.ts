/**
 * Service for handling WebSocket connections with the microboss backend
 */
import { io, Socket } from 'socket.io-client';
import ApiService from './ApiService';

class WebSocketService {
  private socket: Socket | null = null;
  private taskEventCallbacks: Record<string, Function[]> = {};
  private logEventCallbacks: Function[] = [];
  private connected: boolean = false;
  private connectionAttempts: number = 0;
  private readonly maxReconnectAttempts: number = 5;

  /**
   * Connect to the WebSocket server
   */
  connect() {
    if (this.socket) {
      return;
    }

    const socketUrl = process.env.NEXT_PUBLIC_SOCKET_URL || ApiService.socketUrl;
    console.log(`Connecting to WebSocket server at ${socketUrl}`);

    try {
      this.socket = io(socketUrl, {
        reconnectionAttempts: this.maxReconnectAttempts,
        timeout: 10000,
        transports: ['websocket', 'polling'],
      });

      this.socket.on('connect', () => {
        console.log('Connected to Microboss WebSocket server');
        this.connected = true;
        this.connectionAttempts = 0;
      });

      this.socket.on('disconnect', () => {
        console.log('Disconnected from Microboss WebSocket server');
        this.connected = false;
      });

      this.socket.on('connect_error', (error) => {
        this.connectionAttempts++;
        console.error(`WebSocket connection error (attempt ${this.connectionAttempts}/${this.maxReconnectAttempts}):`, error);
        
        if (this.connectionAttempts >= this.maxReconnectAttempts) {
          console.warn('Max WebSocket reconnect attempts reached. Falling back to polling.');
        }
      });

      // Listen for task events
      this.socket.on('task_event', (data: any) => {
        console.log('Received task event:', data);
        
        if (data.task && data.task.task_id) {
          const taskId = data.task.task_id;
          const callbacks = this.taskEventCallbacks[taskId] || [];
          
          callbacks.forEach(callback => {
            try {
              callback(data);
            } catch (error) {
              console.error('Error in task event callback:', error);
            }
          });
        }
      });

      // Listen for log events
      this.socket.on('log_event', (data: any) => {
        console.log('Received log event:', data);
        
        this.logEventCallbacks.forEach(callback => {
          try {
            callback(data);
          } catch (error) {
            console.error('Error in log event callback:', error);
          }
        });
      });
    } catch (error) {
      console.error('Failed to initialize WebSocket connection:', error);
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
      this.connectionAttempts = 0;
    }
  }

  /**
   * Subscribe to task events for a specific task
   */
  subscribeToTaskEvents(taskId: string, callback: Function) {
    if (!this.taskEventCallbacks[taskId]) {
      this.taskEventCallbacks[taskId] = [];
    }
    
    this.taskEventCallbacks[taskId].push(callback);
    
    // Connect if not already connected
    if (!this.connected) {
      this.connect();
    }
    
    return () => this.unsubscribeFromTaskEvents(taskId, callback);
  }

  /**
   * Unsubscribe from task events
   */
  unsubscribeFromTaskEvents(taskId: string, callback: Function) {
    if (this.taskEventCallbacks[taskId]) {
      this.taskEventCallbacks[taskId] = this.taskEventCallbacks[taskId].filter(
        cb => cb !== callback
      );
      
      // If no more callbacks for this task, clean up
      if (this.taskEventCallbacks[taskId].length === 0) {
        delete this.taskEventCallbacks[taskId];
      }
    }
  }

  /**
   * Subscribe to all log events
   */
  subscribeToLogEvents(callback: Function) {
    this.logEventCallbacks.push(callback);
    
    // Connect if not already connected
    if (!this.connected) {
      this.connect();
    }
    
    return () => this.unsubscribeFromLogEvents(callback);
  }

  /**
   * Unsubscribe from log events
   */
  unsubscribeFromLogEvents(callback: Function) {
    this.logEventCallbacks = this.logEventCallbacks.filter(cb => cb !== callback);
  }

  /**
   * Check if connected to the WebSocket server
   */
  isConnected() {
    return this.connected;
  }
}

// Create and export singleton instance
const webSocketService = new WebSocketService();
export default webSocketService; 