describe('Dashboard Page', () => {
  beforeEach(() => {
    // Mock auth state before each test by setting token in localStorage
    cy.window().then((win) => {
      win.localStorage.setItem('token', 'fake-jwt-token');
      win.localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    // Mock the user data API call
    cy.intercept('GET', '/api/profile', {
      statusCode: 200,
      body: {
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      }
    }).as('profileRequest');

    // Mock the tasks API call
    cy.intercept('GET', '/api/tasks', {
      statusCode: 200,
      body: [
        {
          id: '1',
          title: 'Sample Task 1',
          description: 'This is a sample task',
          status: 'in_progress',
          createdAt: '2023-01-01T00:00:00Z'
        },
        {
          id: '2',
          title: 'Sample Task 2',
          description: 'This is another sample task',
          status: 'completed',
          createdAt: '2023-01-02T00:00:00Z'
        }
      ]
    }).as('tasksRequest');

    // Visit the dashboard
    cy.visit('/dashboard');
    
    // Wait for the API requests to complete
    cy.wait('@profileRequest');
    cy.wait('@tasksRequest');
  });

  it('should display the dashboard with user info', () => {
    // Check that we have the user's name displayed
    cy.get('header').should('contain', 'Test User');
  });

  it('should display the task list', () => {
    // Check that we have the task list with the correct number of tasks
    cy.get('[data-testid="task-list"]').should('exist');
    cy.get('[data-testid="task-item"]').should('have.length', 2);
    cy.get('[data-testid="task-item"]').first().should('contain', 'Sample Task 1');
  });

  it('should navigate to task details when clicking on a task', () => {
    // Click on the first task
    cy.get('[data-testid="task-item"]').first().click();
    
    // Check that we're on the task details page
    cy.url().should('include', '/tasks/1');
  });

  it('should allow creating a new task', () => {
    // Mock the create task API call
    cy.intercept('POST', '/api/tasks', {
      statusCode: 201,
      body: {
        id: '3',
        title: 'New Task',
        description: 'This is a new task',
        status: 'not_started',
        createdAt: '2023-01-03T00:00:00Z'
      }
    }).as('createTaskRequest');
    
    // Click the "New Task" button
    cy.get('[data-testid="new-task-button"]').click();
    
    // Fill in the form
    cy.get('input[name="title"]').type('New Task');
    cy.get('textarea[name="description"]').type('This is a new task');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for the API request to complete
    cy.wait('@createTaskRequest');
    
    // Check that the new task appears in the list (we'd need to mock the GET tasks again)
    cy.get('[data-testid="task-item"]').should('contain', 'New Task');
  });

  it('should allow logging out', () => {
    // Click the logout button
    cy.get('[data-testid="logout-button"]').click();
    
    // Check that we're redirected to the login page
    cy.url().should('include', '/login');
    
    // Check that the token is removed from localStorage
    cy.window().then((win) => {
      expect(win.localStorage.getItem('token')).to.be.null;
      expect(win.localStorage.getItem('user')).to.be.null;
    });
  });
}); 