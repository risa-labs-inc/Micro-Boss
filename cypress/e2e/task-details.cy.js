describe('Task Details Page', () => {
  beforeEach(() => {
    // Mock the authentication state
    cy.window().then((win) => {
      win.localStorage.setItem('token', 'fake-jwt-token');
      win.localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    // Intercept API calls
    cy.intercept('GET', '/api/tasks/1', {
      statusCode: 200,
      body: {
        id: '1',
        title: 'Test Task',
        description: 'This is a test task description',
        type: 'script',
        status: 'running',
        scriptPath: '/path/to/script.py',
        parameters: '--flag1 value1',
        createdAt: new Date().toISOString(),
        startedAt: new Date().toISOString(),
        user: {
          id: '1',
          name: 'Test User'
        }
      }
    }).as('getTask');

    cy.intercept('GET', '/api/tasks/1/events', {
      statusCode: 200,
      body: [
        {
          id: '1',
          type: 'log',
          message: 'Task started',
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          type: 'code',
          content: 'print("Hello World")',
          language: 'python',
          timestamp: new Date().toISOString()
        },
        {
          id: '3',
          type: 'result',
          result: { value: 42 },
          timestamp: new Date().toISOString()
        }
      ]
    }).as('getEvents');

    cy.intercept('GET', '/api/tasks/1/graph', {
      statusCode: 200,
      body: {
        nodes: [
          { id: 1, label: 'Start' },
          { id: 2, label: 'Process' },
          { id: 3, label: 'End' }
        ],
        edges: [
          { from: 1, to: 2 },
          { from: 2, to: 3 }
        ]
      }
    }).as('getGraph');

    // Visit the task details page
    cy.visit('/tasks/1');
    
    // Wait for API calls to complete
    cy.wait('@getTask');
    cy.wait('@getEvents');
    cy.wait('@getGraph');
  });

  it('should display task information correctly', () => {
    // Check task metadata
    cy.get('[data-testid="task-title"]').should('contain', 'Test Task');
    cy.get('[data-testid="task-description"]').should('contain', 'This is a test task description');
    cy.get('[data-testid="task-status"]').should('contain', 'Running');
    cy.get('[data-testid="task-type"]').should('contain', 'Script');
    
    // Check task details
    cy.get('[data-testid="task-script-path"]').should('contain', '/path/to/script.py');
    cy.get('[data-testid="task-parameters"]').should('contain', '--flag1 value1');
  });

  it('should display the event timeline correctly', () => {
    // Open the timeline tab if needed
    cy.get('[data-testid="tab-timeline"]').click();
    
    // Check that events are displayed
    cy.get('[data-testid="timeline-event"]').should('have.length', 3);
    
    // Check log event
    cy.get('[data-testid="timeline-event"]').eq(0).should('contain', 'Task started');
    
    // Check code event
    cy.get('[data-testid="timeline-event"]').eq(1).should('contain', 'print("Hello World")');
    
    // Check result event
    cy.get('[data-testid="timeline-event"]').eq(2).should('contain', '42');
  });

  it('should display the dependency graph correctly', () => {
    // Open the graph tab if needed
    cy.get('[data-testid="tab-graph"]').click();
    
    // Check that the graph is displayed
    cy.get('[data-testid="dependency-graph"]').should('exist');
    
    // We can't easily test the actual graph rendering with Cypress
    // but we can check if the graph container is visible
    cy.get('[data-testid="dependency-graph"]').should('be.visible');
  });

  it('should allow starting the task', () => {
    // Intercept the start task API call
    cy.intercept('POST', '/api/tasks/1/start', {
      statusCode: 200,
      body: {
        id: '1',
        status: 'running',
        startedAt: new Date().toISOString()
      }
    }).as('startTask');
    
    // Click the start button
    cy.get('[data-testid="start-task-button"]').click();
    
    // Confirm the action in the modal
    cy.get('[data-testid="confirm-button"]').click();
    
    // Verify the API call
    cy.wait('@startTask');
    
    // Check for success message
    cy.contains('Task started successfully').should('be.visible');
    
    // Check that the status is updated
    cy.get('[data-testid="task-status"]').should('contain', 'Running');
  });

  it('should handle real-time updates via WebSocket', () => {
    // Mock a WebSocket message
    cy.window().then((win) => {
      // Create a fake event
      const event = {
        type: 'log',
        message: 'New log message from WebSocket',
        timestamp: new Date().toISOString(),
        taskId: '1'
      };
      
      // Find the WebSocket handler and trigger it
      // Note: This is a simplified approach and may need adjustments
      // based on how WebSockets are implemented
      if (win.socketMessageHandler) {
        win.socketMessageHandler(event);
      } else {
        // Dispatch a custom event if direct access to handler is not available
        const wsEvent = new CustomEvent('ws:message', { detail: event });
        win.dispatchEvent(wsEvent);
      }
    });
    
    // Check that the new log message appears in the timeline
    cy.contains('New log message from WebSocket').should('be.visible');
  });
}); 