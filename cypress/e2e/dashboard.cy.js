describe('Dashboard Page', () => {
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
    cy.intercept('GET', '/api/tasks', {
      statusCode: 200,
      body: [
        {
          id: '1',
          title: 'Task 1',
          description: 'Description 1',
          status: 'pending',
          createdAt: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Task 2',
          description: 'Description 2',
          status: 'running',
          createdAt: new Date().toISOString()
        },
        {
          id: '3',
          title: 'Task 3',
          description: 'Description 3',
          status: 'completed',
          createdAt: new Date().toISOString()
        }
      ]
    }).as('getTasks');

    cy.intercept('GET', '/api/stats', {
      statusCode: 200,
      body: {
        total: 5,
        pending: 2,
        running: 1,
        completed: 2,
        failed: 0
      }
    }).as('getStats');

    // Visit the dashboard
    cy.visit('/dashboard');
    
    // Wait for API calls to complete
    cy.wait('@getTasks');
    cy.wait('@getStats');
  });

  it('should display the dashboard correctly', () => {
    // Check for the page title
    cy.get('h1').should('contain', 'Dashboard');
    
    // Check for the user greeting
    cy.contains('Welcome, Test User').should('be.visible');
    
    // Check for statistics section
    cy.get('[data-testid="stats-card"]').should('have.length', 4);
    cy.contains('Total Tasks: 5').should('be.visible');
    cy.contains('Pending: 2').should('be.visible');
    cy.contains('Running: 1').should('be.visible');
    cy.contains('Completed: 2').should('be.visible');
    
    // Check for the task list
    cy.get('[data-testid="task-item"]').should('have.length', 3);
  });

  it('should filter tasks correctly', () => {
    // Click on the filter dropdown
    cy.get('[data-testid="filter-dropdown"]').click();
    
    // Select "Completed" filter
    cy.contains('Completed').click();
    
    // Check that only completed tasks are displayed
    cy.get('[data-testid="task-item"]').should('have.length', 1);
    cy.get('[data-testid="task-item"]').should('contain', 'Task 3');
  });

  it('should navigate to task details page when clicking on a task', () => {
    // Click on the first task
    cy.get('[data-testid="task-item"]').first().click();
    
    // Check that we navigate to the task details page
    cy.url().should('include', '/tasks/1');
  });

  it('should navigate to create task page when clicking new task button', () => {
    // Click on the new task button
    cy.get('[data-testid="new-task-button"]').click();
    
    // Check that we navigate to the create task page
    cy.url().should('include', '/tasks/new');
  });

  it('should handle logout correctly', () => {
    // Click on user dropdown
    cy.get('[data-testid="user-dropdown"]').click();
    
    // Click on logout
    cy.contains('Logout').click();
    
    // Check localStorage is cleared
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.be.null;
      expect(win.localStorage.getItem('user')).to.be.null;
    });
    
    // Check we are redirected to login page
    cy.url().should('include', '/login');
  });
}); 