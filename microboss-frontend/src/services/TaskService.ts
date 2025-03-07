import { TaskStatus } from '@/types/Task';

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

// Mock data to simulate tasks
const mockTasks: Task[] = [
  {
    task_id: '1',
    description: 'Calculate factorial of 10',
    depth: 1,
    max_retries: 3,
    max_decomposition_depth: 10,
    created_at: Date.now() - 10000,
    started_at: Date.now() - 9000,
    completed_at: Date.now() - 2000,
    status: TaskStatus.COMPLETED,
    result: '3628800',
    model_info: 'Anthropic Claude'
  },
  {
    task_id: '2',
    description: 'Find prime numbers between 1 and 100',
    depth: 2,
    max_retries: 3,
    max_decomposition_depth: 10,
    created_at: Date.now() - 30000,
    started_at: Date.now() - 29000,
    status: TaskStatus.RUNNING,
    model_info: 'OpenAI GPT-4'
  },
  {
    task_id: '3',
    description: 'Solve differential equation dy/dx = y^2 + x',
    depth: 3,
    max_retries: 3,
    max_decomposition_depth: 10,
    created_at: Date.now() - 50000,
    status: TaskStatus.PENDING
  },
  {
    task_id: '4',
    description: 'Implement a basic neural network',
    depth: 2,
    max_retries: 2,
    max_decomposition_depth: 8,
    created_at: Date.now() - 100000,
    started_at: Date.now() - 95000,
    completed_at: Date.now() - 85000,
    status: TaskStatus.FAILED,
    error: 'Dependencies installation failed',
    model_info: 'OpenAI GPT-4'
  }
];

class TaskService {
  private tasks: Task[] = [...mockTasks];

  // Get all tasks
  async getTasks(): Promise<Task[]> {
    // In a real application, this would be an API call
    return Promise.resolve(this.tasks.map(task => this.formatTaskDates(task)));
  }

  // Get a specific task by ID
  async getTask(taskId: string): Promise<Task | undefined> {
    // In a real application, this would be an API call
    const task = this.tasks.find(t => t.task_id === taskId);
    return Promise.resolve(task ? this.formatTaskDates(task) : undefined);
  }

  // Create a new task
  async createTask(
    description: string,
    depth: number = 1,
    max_retries: number = 3,
    max_decomposition_depth: number = 10,
    model?: string
  ): Promise<Task> {
    // In a real application, this would be an API call
    const task: Task = {
      task_id: Math.random().toString(36).substring(2, 11),
      description,
      depth,
      max_retries,
      max_decomposition_depth,
      created_at: Date.now(),
      status: TaskStatus.PENDING,
      model_info: model
    };
    
    this.tasks.push(task);
    return Promise.resolve(this.formatTaskDates(task));
  }

  // Start a task
  async startTask(taskId: string): Promise<Task | undefined> {
    // In a real application, this would be an API call
    const taskIndex = this.tasks.findIndex(t => t.task_id === taskId);
    
    if (taskIndex === -1) {
      return Promise.resolve(undefined);
    }
    
    const task = this.tasks[taskIndex];
    
    if (task.status === TaskStatus.RUNNING) {
      return Promise.resolve(this.formatTaskDates(task));
    }
    
    task.status = TaskStatus.RUNNING;
    task.started_at = Date.now();
    
    // Simulate task execution with a timeout
    this.simulateTaskExecution(task);
    
    return Promise.resolve(this.formatTaskDates(task));
  }

  // Helper method to simulate task execution
  private simulateTaskExecution(task: Task): void {
    const executionTime = Math.random() * 10000 + 5000; // 5-15 seconds
    
    setTimeout(() => {
      if (Math.random() > 0.2) { // 80% success rate
        task.status = TaskStatus.COMPLETED;
        
        // Simulate different types of results
        if (task.description.includes('factorial')) {
          task.result = '3628800';
        } else if (task.description.includes('prime')) {
          task.result = '[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]';
        } else {
          task.result = 'Task completed successfully';
        }
      } else {
        task.status = TaskStatus.FAILED;
        task.error = 'Execution error: Failed to complete the task';
      }
      
      task.completed_at = Date.now();
    }, executionTime);
  }

  // Format task dates for display
  private formatTaskDates(task: Task): Task {
    const formattedTask = { ...task };
    
    if (task.created_at) {
      formattedTask.formatted_created = new Date(task.created_at).toLocaleString();
    }
    
    if (task.started_at) {
      formattedTask.formatted_started = new Date(task.started_at).toLocaleString();
    }
    
    if (task.completed_at && task.started_at) {
      formattedTask.formatted_completed = new Date(task.completed_at).toLocaleString();
      formattedTask.duration = task.completed_at - task.started_at;
    }
    
    return formattedTask;
  }

  // Get events for a task (logs, code snippets, etc.)
  async getTaskEvents(taskId: string): Promise<any[]> {
    // In a real application, this would fetch events from an API
    // For now, return mock events based on the task
    const task = await this.getTask(taskId);
    
    if (!task) {
      return Promise.resolve([]);
    }
    
    return Promise.resolve(this.generateMockEvents(task));
  }

  // Generate mock events for a task
  private generateMockEvents(task: Task): any[] {
    const events = [];
    const baseTime = task.created_at;
    
    // Task creation event
    events.push({
      id: `e-${Math.random().toString(36).substring(2, 9)}`,
      timestamp: baseTime,
      formatted_time: new Date(baseTime).toLocaleString(),
      level: 'info',
      message: `Created task: ${task.description}`,
      task_id: task.task_id,
      type: 'task'
    });
    
    if (task.started_at) {
      // Task started event
      events.push({
        id: `e-${Math.random().toString(36).substring(2, 9)}`,
        timestamp: task.started_at,
        formatted_time: new Date(task.started_at).toLocaleString(),
        level: 'info',
        message: `Starting task: ${task.description}`,
        task_id: task.task_id,
        type: 'task'
      });
      
      // Model info event
      if (task.model_info) {
        events.push({
          id: `e-${Math.random().toString(36).substring(2, 9)}`,
          timestamp: task.started_at + 100,
          formatted_time: new Date(task.started_at + 100).toLocaleString(),
          level: 'info',
          message: `Task will be solved using ${task.model_info}`,
          task_id: task.task_id,
          type: 'info',
          data: { model_info: task.model_info }
        });
      }
      
      // Add code events
      const codeTime = task.started_at + 2000;
      events.push({
        id: `e-${Math.random().toString(36).substring(2, 9)}`,
        timestamp: codeTime,
        formatted_time: new Date(codeTime).toLocaleString(),
        level: 'code',
        message: 'Generated code to solve the task',
        task_id: task.task_id,
        type: 'code',
        data: {
          code: this.getMockCodeForTask(task),
          language: 'python'
        }
      });
      
      // Add result event if completed
      if (task.completed_at && task.status === TaskStatus.COMPLETED) {
        events.push({
          id: `e-${Math.random().toString(36).substring(2, 9)}`,
          timestamp: task.completed_at - 500,
          formatted_time: new Date(task.completed_at - 500).toLocaleString(),
          level: 'result',
          message: 'Task result',
          task_id: task.task_id,
          type: 'result',
          data: {
            result: task.result
          }
        });
        
        // Success event
        events.push({
          id: `e-${Math.random().toString(36).substring(2, 9)}`,
          timestamp: task.completed_at,
          formatted_time: new Date(task.completed_at).toLocaleString(),
          level: 'success',
          message: 'Task completed successfully',
          task_id: task.task_id,
          type: 'task'
        });
      }
      
      // Add error event if failed
      if (task.completed_at && task.status === TaskStatus.FAILED) {
        events.push({
          id: `e-${Math.random().toString(36).substring(2, 9)}`,
          timestamp: task.completed_at,
          formatted_time: new Date(task.completed_at).toLocaleString(),
          level: 'error',
          message: task.error || 'Task failed with an unknown error',
          task_id: task.task_id,
          type: 'task'
        });
      }
    }
    
    return events.sort((a, b) => a.timestamp - b.timestamp);
  }

  // Get mock code for a task based on its description
  private getMockCodeForTask(task: Task): string {
    if (task.description.includes('factorial')) {
      return `def factorial(n):
    """Calculate the factorial of a number."""
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

# Calculate factorial of 10
result = factorial(10)
print(f"The factorial of 10 is {result}")`;
    } else if (task.description.includes('prime')) {
      return `def sieve_of_eratosthenes(limit):
    """Find all prime numbers up to a given limit."""
    primes = []
    prime = [True for i in range(limit + 1)]
    p = 2
    while p * p <= limit:
        if prime[p]:
            for i in range(p * p, limit + 1, p):
                prime[i] = False
        p += 1
    
    for p in range(2, limit + 1):
        if prime[p]:
            primes.append(p)
    return primes

# Find prime numbers between 1 and 100
primes = sieve_of_eratosthenes(100)
print(f"Prime numbers between 1 and 100: {primes}")`;
    } else {
      return `def solve_task():
    """Solve the given task."""
    print("Implementing solution for: ${task.description}")
    # Task implementation would go here
    return "Solution completed"

result = solve_task()
print(result)`;
    }
  }
}

// Create and export a singleton instance
const taskService = new TaskService();
export default taskService; 