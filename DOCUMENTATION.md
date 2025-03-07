# Microboss Frontend Documentation

## Introduction

Microboss is a powerful task management and execution platform built with Next.js, React, and TypeScript. This documentation provides a comprehensive guide to the frontend application, covering setup, architecture, components, testing, and deployment.

## Table of Contents

1. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the Application](#running-the-application)

2. [Application Architecture](#application-architecture)
   - [Project Structure](#project-structure)
   - [Technology Stack](#technology-stack)
   - [Key Libraries](#key-libraries)

3. [Core Components](#core-components)
   - [Layout Components](#layout-components)
   - [Task Components](#task-components)
   - [Visualization Components](#visualization-components)
   - [Forms and Inputs](#forms-and-inputs)

4. [API Integration](#api-integration)
   - [REST API](#rest-api)
   - [WebSocket Integration](#websocket-integration)
   - [Authentication](#authentication)

5. [Testing](#testing)
   - [Unit Testing with Jest](#unit-testing-with-jest)
   - [E2E Testing with Cypress](#e2e-testing-with-cypress)
   - [Running Tests](#running-tests)

6. [Deployment](#deployment)
   - [Build Process](#build-process)
   - [CI/CD Pipeline](#cicd-pipeline)
   - [Environment Variables](#environment-variables)

7. [Contributing](#contributing)
   - [Code Style](#code-style)
   - [Branching Strategy](#branching-strategy)
   - [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-org/microboss-frontend.git
   cd microboss-frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   ```
   cp .env.example .env.local
   ```
   Edit the `.env.local` file to set your environment-specific variables.

### Running the Application

- Development server:
  ```
  npm run dev
  ```
  This will start the development server at `http://localhost:3000`.

- Production build:
  ```
  npm run build
  npm start
  ```

## Application Architecture

### Project Structure

The application follows a modular structure:

```
microboss-frontend/
├── .github/         # GitHub Actions workflows
├── cypress/         # Cypress tests
├── public/          # Static assets
├── src/
│   ├── app/         # Next.js App Router pages
│   ├── components/  # React components
│   │   ├── common/  # Shared UI components
│   │   ├── layout/  # Layout components
│   │   ├── task/    # Task-related components
│   │   └── ...
│   ├── lib/         # Utilities, hooks, contexts
│   │   ├── contexts/  # React contexts
│   │   ├── hooks/     # Custom hooks
│   │   ├── services/  # API services
│   │   └── types.ts   # TypeScript types
│   └── ...
├── .babelrc         # Babel configuration
├── jest.config.js   # Jest configuration
├── next.config.js   # Next.js configuration
└── ...
```

### Technology Stack

- **Framework**: Next.js 15.x
- **Language**: TypeScript
- **UI Libraries**: Tailwind CSS, React Bootstrap
- **State Management**: React Context API
- **Form Handling**: React Hook Form
- **Validation**: Zod
- **API Communication**: Axios, Socket.IO

### Key Libraries

- **next**: The React framework for production
- **react**, **react-dom**: React core libraries
- **typescript**: TypeScript language support
- **tailwindcss**: Utility-first CSS framework
- **react-bootstrap**: Bootstrap components for React
- **axios**: HTTP client for API requests
- **socket.io-client**: WebSocket client for real-time updates
- **react-hook-form**: Form handling library
- **zod**: TypeScript-first schema validation
- **vis-network**: Network visualization library
- **highlight.js**: Syntax highlighting for code blocks
- **react-hot-toast**: Toast notifications

## Core Components

### Layout Components

- **MainLayout**: The main application layout with header, sidebar, and footer
- **Header**: Top navigation bar with user menu and notifications
- **Sidebar**: Navigation menu with links to main sections
- **Footer**: Page footer with links and copyright information

### Task Components

- **TaskCard**: Card component for displaying task summaries
- **TaskList**: List component for displaying multiple tasks with filtering and sorting
- **TaskForm**: Form for creating or editing tasks
- **TaskDetails**: Detailed view of a task with status, metadata, and actions

### Visualization Components

- **StatusBadge**: Badge component for displaying task status (pending, running, completed, failed)
- **CodeViewer**: Component for displaying code with syntax highlighting
- **LogConsole**: Console-like component for displaying task logs
- **Timeline**: Component for visualizing task event timeline
- **DependencyGraph**: Component for visualizing task dependencies using vis-network
- **ResultViewer**: Component for displaying task results

### Forms and Inputs

- **Button**: Customizable button component with different variants
- **TextInput**: Text input field with validation
- **SelectInput**: Dropdown select field with validation
- **Checkbox**: Checkbox input component
- **TextArea**: Multi-line text input component

## API Integration

### REST API

The application communicates with the backend through RESTful API endpoints. The `api.ts` service provides a centralized interface for making API requests using Axios.

Key API services:

- **TaskApi**: Services for task CRUD operations
- **AuthService**: Services for authentication and user management

Example usage:

```typescript
import { TaskApi } from '@/lib/services/api';

// Get all tasks
const tasks = await TaskApi.getTasks();

// Get a single task
const task = await TaskApi.getTask('123');

// Create a new task
const newTask = await TaskApi.createTask({ title: 'New Task', description: 'Description' });
```

### WebSocket Integration

Real-time updates are handled through WebSocket connections using Socket.IO. The `socket.ts` service and `useSocketEvents` hook provide a unified interface for WebSocket communication.

Example usage:

```typescript
import { useSocketEvents } from '@/lib/hooks/useSocketEvents';

// In a component
const { subscribe, unsubscribe } = useSocketEvents();

useEffect(() => {
  // Subscribe to task events
  const taskId = '123';
  const handler = (event) => {
    console.log('New event:', event);
    // Update UI with new event data
  };
  
  subscribe(`task:${taskId}:event`, handler);
  
  return () => {
    unsubscribe(`task:${taskId}:event`, handler);
  };
}, []);
```

### Authentication

Authentication is managed through the `AuthContext` which provides authentication state and methods for login, registration, and logout.

Example usage:

```typescript
import { useAuth } from '@/lib/contexts/AuthContext';

// In a component
const { user, isAuthenticated, login, logout } = useAuth();

// Login
const handleLogin = async (credentials) => {
  try {
    await login(credentials);
    // Redirect or show success message
  } catch (error) {
    // Handle error
  }
};

// Logout
const handleLogout = () => {
  logout();
  // Redirect to login page
};
```

## Testing

### Unit Testing with Jest

We use Jest and React Testing Library for unit testing components, services, and hooks.

Examples of what we test:

- **Components**: Rendering, user interactions, state changes
- **Services**: API calls, data transformation
- **Hooks**: State management, side effects
- **Contexts**: Provider functionality, consumer behavior

### E2E Testing with Cypress

We use Cypress for end-to-end testing of key user flows.

Key test scenarios:

- **Authentication**: Login, registration, profile management
- **Task Management**: Creating, viewing, and managing tasks
- **Navigation**: Moving between different sections of the application
- **Form Validation**: Testing form inputs and validation
- **Real-time Updates**: Testing WebSocket notifications and UI updates

### Running Tests

- Running unit tests:
  ```
  npm test
  ```

- Running unit tests in watch mode:
  ```
  npm run test:watch
  ```

- Running unit tests with coverage:
  ```
  npm run test:coverage
  ```

- Running Cypress tests in UI mode:
  ```
  npm run cypress
  ```

- Running Cypress tests headlessly:
  ```
  npm run cypress:headless
  ```

- Running E2E tests with dev server:
  ```
  npm run e2e
  ```

## Deployment

### Build Process

The application is built using Next.js's production build system:

```
npm run build
```

This generates optimized production assets in the `.next` directory.

### CI/CD Pipeline

We use GitHub Actions for continuous integration and deployment. The pipeline:

1. Runs linting checks
2. Executes unit tests
3. Builds the application
4. Runs Cypress tests against the built application
5. Deploys to production (if on the main branch)

The workflow configuration is in `.github/workflows/ci.yml`.

### Environment Variables

The application uses environment variables for configuration. These are defined in `.env.local` for local development and set as secrets in the CI/CD environment for deployment.

Key environment variables:

- `NEXT_PUBLIC_API_BASE_URL`: Base URL for the backend API
- `NEXT_PUBLIC_SOCKET_URL`: URL for the WebSocket server
- `NEXT_PUBLIC_SITE_URL`: URL for the frontend application

## Contributing

### Code Style

We follow a consistent code style enforced by ESLint and Prettier:

- Running linting:
  ```
  npm run lint
  ```

- Automatically fixing linting issues:
  ```
  npm run lint -- --fix
  ```

### Branching Strategy

- `main`: Production-ready code
- `develop`: Latest development changes
- Feature branches: `feature/feature-name`
- Bug fix branches: `fix/bug-name`

### Pull Request Process

1. Create a branch from `develop`
2. Make your changes and commit with descriptive messages
3. Push your branch and create a pull request against `develop`
4. Ensure all CI checks pass
5. Request review from at least one team member
6. Address review comments
7. Once approved, merge your pull request

---

This documentation is maintained by the Microboss team. For questions or support, please contact [support@microboss.example.com](mailto:support@microboss.example.com). 