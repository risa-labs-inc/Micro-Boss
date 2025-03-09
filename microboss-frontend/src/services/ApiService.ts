/**
 * Service for communicating with the Microboss backend API
 */

// Base API URL - use environment variables or fallback to defaults
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:5000';

/**
 * Make a GET request to the API
 */
async function get(endpoint: string) {
  console.log(`Making GET request to ${API_BASE_URL}${endpoint}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`GET request failed for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Make a POST request to the API
 */
async function post(endpoint: string, data?: any) {
  console.log(`Making POST request to ${API_BASE_URL}${endpoint}`, data);
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`POST request failed for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * API service for interacting with the Microboss backend
 */
const ApiService = {
  // Task methods
  getTasks: () => get('/api/tasks'),
  getTask: (taskId: string) => get(`/api/tasks/${taskId}`),
  createTask: (taskData: any) => post('/api/tasks', taskData),
  startTask: (taskId: string) => post(`/api/tasks/${taskId}/start`),
  
  // Event methods
  getTaskEvents: (taskId: string) => get(`/api/tasks/${taskId}/events`),
  
  // Model methods
  getAvailableModels: () => get('/api/models'),
  
  // Configuration for WebSocket connection
  socketUrl: SOCKET_URL,
};

export default ApiService; 