import { TaskStatus } from '@/types/Task';
import ApiService from './ApiService';
import WebSocketService from './WebSocketService';

// Define the Task interface
export interface Task {
  task_id: string;
  description: string;
  depth: number;
  max_retries: number;
  max_decomposition_depth: number;
  created_at: number;
  started_at?: number;
  completed_at?: number;
  status: TaskStatus;
  result?: string;
  error?: string;
  duration?: number;
  formatted_created?: string;
  formatted_started?: string;
  formatted_completed?: string;
  model_info?: string;
}

// Mock data to use as fallback when the backend is unavailable
const mockTasks: Task[] = [
  {
    task_id: 'mock-1',
    description: 'Calculate factorial of 10',
    depth: 1,
    max_retries: 3,
    max_decomposition_depth: 10,
    created_at: Date.now() / 1000 - 10000,
    started_at: Date.now() / 1000 - 9000,
    completed_at: Date.now() / 1000 - 2000,
    status: TaskStatus.COMPLETED,
    result: '3628800',
    model_info: 'Anthropic Claude'
  },
  {
    task_id: 'mock-2',
    description: 'Find prime numbers between 1 and 100',
    depth: 2,
    max_retries: 3,
    max_decomposition_depth: 10,
    created_at: Date.now() / 1000 - 30000,
    started_at: Date.now() / 1000 - 29000,
    status: TaskStatus.RUNNING,
    model_info: 'OpenAI GPT-4'
  }
];

// Mock events to use as fallback
const mockEvents: Record<string, any[]> = {
  'mock-1': [
    {
      id: 'e-1',
      timestamp: Date.now() / 1000 - 10000,
      formatted_time: new Date((Date.now() - 10000 * 1000)).toLocaleString(),
      level: 'task',
      message: 'Created task: Calculate factorial of 10',
      task_id: 'mock-1',
      type: 'task',
      depth: 0
    },
    {
      id: 'e-2',
      timestamp: Date.now() / 1000 - 9000,
      formatted_time: new Date((Date.now() - 9000 * 1000)).toLocaleString(),
      level: 'code',
      message: 'Generated code to solve the task',
      task_id: 'mock-1',
      type: 'code',
      data: {
        code: `def factorial(n):\n    """Calculate the factorial of a number."""\n    if n == 0 or n == 1:\n        return 1\n    else:\n        return n * factorial(n-1)\n\n# Calculate factorial of 10\nresult = factorial(10)\nprint(f"The factorial of 10 is {result}")`,
        language: 'python'
      },
      depth: 0
    },
    {
      id: 'e-3',
      timestamp: Date.now() / 1000 - 2500,
      formatted_time: new Date((Date.now() - 2500 * 1000)).toLocaleString(),
      level: 'result',
      message: 'Task result',
      task_id: 'mock-1',
      type: 'result',
      data: {
        result: '3628800'
      },
      depth: 0
    }
  ]
};

class TaskService {
  private useMockData = false;
  private mockTasksData: Task[] = [...mockTasks];

  constructor() {
    // Check if the API is available on startup
    this.checkApiAvailability();
  }

  // Check if the API is available
  private async checkApiAvailability() {
    try {
      await ApiService.getTasks();
      this.useMockData = false;
      console.log('Using real API data');
    } catch (error) {
      this.useMockData = true;
      console.warn('API unavailable, using mock data:', error);
    }
  }

  // Get all tasks
  async getTasks(): Promise<Task[]> {
    try {
      if (this.useMockData) {
        return this.mockTasksData.map(task => this.formatTaskDates(task));
      }
      
      const tasks = await ApiService.getTasks();
      return tasks.map((task: any) => this.formatTaskDates(task));
    } catch (error) {
      console.error('Error fetching tasks, falling back to mock data:', error);
      this.useMockData = true;
      return this.mockTasksData.map(task => this.formatTaskDates(task));
    }
  }

  // Get a specific task by ID
  async getTask(taskId: string): Promise<Task | undefined> {
    try {
      if (this.useMockData) {
        const task = this.mockTasksData.find(t => t.task_id === taskId);
        return task ? this.formatTaskDates(task) : undefined;
      }
      
      const task = await ApiService.getTask(taskId);
      return this.formatTaskDates(task);
    } catch (error) {
      console.error(`Error fetching task ${taskId}, checking mock data:`, error);
      this.useMockData = true;
      const task = this.mockTasksData.find(t => t.task_id === taskId);
      return task ? this.formatTaskDates(task) : undefined;
    }
  }

  // Create a new task
  async createTask(
    description: string,
    depth: number = 1,
    max_retries: number = 3,
    max_decomposition_depth: number = 10,
    model?: string
  ): Promise<Task> {
    try {
      if (this.useMockData) {
        const task: Task = {
          task_id: `mock-${Math.random().toString(36).substring(2, 11)}`,
          description,
          depth,
          max_retries,
          max_decomposition_depth,
          created_at: Date.now() / 1000,
          status: TaskStatus.PENDING,
          model_info: model
        };
        
        this.mockTasksData.push(task);
        return this.formatTaskDates(task);
      }
      
      const taskData = {
        description,
        depth,
        max_retries,
        max_decomposition_depth,
        model
      };
      
      const task = await ApiService.createTask(taskData);
      return this.formatTaskDates(task);
    } catch (error) {
      console.error('Error creating task, using mock task:', error);
      this.useMockData = true;
      
      const task: Task = {
        task_id: `mock-${Math.random().toString(36).substring(2, 11)}`,
        description,
        depth,
        max_retries,
        max_decomposition_depth,
        created_at: Date.now() / 1000,
        status: TaskStatus.PENDING,
        model_info: model
      };
      
      this.mockTasksData.push(task);
      return this.formatTaskDates(task);
    }
  }

  // Start a task
  async startTask(taskId: string): Promise<Task | undefined> {
    try {
      if (this.useMockData) {
        const taskIndex = this.mockTasksData.findIndex(t => t.task_id === taskId);
        
        if (taskIndex === -1) {
          return undefined;
        }
        
        const task = this.mockTasksData[taskIndex];
        
        if (task.status === TaskStatus.RUNNING) {
          return this.formatTaskDates(task);
        }
        
        task.status = TaskStatus.RUNNING;
        task.started_at = Date.now() / 1000;
        
        // Simulate task execution with a timeout
        setTimeout(() => {
          task.status = TaskStatus.COMPLETED;
          task.completed_at = Date.now() / 1000;
          task.result = task.description.includes('factorial') 
            ? '3628800' 
            : 'Task completed successfully';
        }, 10000);
        
        return this.formatTaskDates(task);
      }
      
      const task = await ApiService.startTask(taskId);
      return this.formatTaskDates(task);
    } catch (error) {
      console.error(`Error starting task ${taskId}, using mock data:`, error);
      this.useMockData = true;
      
      const taskIndex = this.mockTasksData.findIndex(t => t.task_id === taskId);
      
      if (taskIndex === -1) {
        return undefined;
      }
      
      const task = this.mockTasksData[taskIndex];
      
      if (task.status === TaskStatus.RUNNING) {
        return this.formatTaskDates(task);
      }
      
      task.status = TaskStatus.RUNNING;
      task.started_at = Date.now() / 1000;
      
      // Simulate task execution with a timeout
      setTimeout(() => {
        task.status = TaskStatus.COMPLETED;
        task.completed_at = Date.now() / 1000;
        task.result = task.description.includes('factorial') 
          ? '3628800' 
          : 'Task completed successfully';
      }, 10000);
      
      return this.formatTaskDates(task);
    }
  }

  // Format task dates for display - made public to be used by other components
  formatTaskDates(task: any): Task {
    // Use the dates from the API response
    return {
      ...task,
      // Add formatted dates if they're not already provided by the API
      formatted_created: task.formatted_created || new Date(task.created_at * 1000).toLocaleString(),
      formatted_started: task.started_at ? (task.formatted_started || new Date(task.started_at * 1000).toLocaleString()) : undefined,
      formatted_completed: task.completed_at ? (task.formatted_completed || new Date(task.completed_at * 1000).toLocaleString()) : undefined,
    };
  }

  // Get events for a task (logs, code snippets, etc.)
  async getTaskEvents(taskId: string): Promise<any[]> {
    try {
      if (this.useMockData) {
        // Return mock events if available
        return mockEvents[taskId] || [];
      }
      
      return await ApiService.getTaskEvents(taskId);
    } catch (error) {
      console.error(`Error fetching events for task ${taskId}, using mock events:`, error);
      this.useMockData = true;
      return mockEvents[taskId] || [];
    }
  }

  // Subscribe to real-time events for a task
  subscribeToTaskEvents(taskId: string, callback: Function) {
    if (this.useMockData) {
      // For mock data, we don't need real-time updates
      console.log('Using mock data, real-time updates not available');
      return () => {};
    }
    
    return WebSocketService.subscribeToTaskEvents(taskId, callback);
  }

  // Subscribe to all log events
  subscribeToLogEvents(callback: Function) {
    if (this.useMockData) {
      // For mock data, we don't need real-time updates
      console.log('Using mock data, real-time updates not available');
      return () => {};
    }
    
    return WebSocketService.subscribeToLogEvents(callback);
  }
}

// Create and export singleton instance
const taskService = new TaskService();
export default taskService; 