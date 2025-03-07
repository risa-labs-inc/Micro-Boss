describe('Task Form', () => {
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

    // Visit the new task page
    cy.visit('/tasks/new');
  });

  it('should display the task creation form correctly', () => {
    // Check for the page title
    cy.get('h1').should('contain', 'Create New Task');
    
    // Check for form elements
    cy.get('form').should('exist');
    cy.get('input[name="title"]').should('exist');
    cy.get('textarea[name="description"]').should('exist');
    cy.get('select[name="type"]').should('exist');
    cy.get('button[type="submit"]').should('exist').and('contain', 'Create Task');
    cy.get('button[type="button"]').should('exist').and('contain', 'Cancel');
  });

  it('should validate form inputs', () => {
    // Submit form without filling required fields
    cy.get('button[type="submit"]').click();
    
    // Check for validation error messages
    cy.contains('Title is required').should('be.visible');
    cy.contains('Description is required').should('be.visible');
    cy.contains('Task type is required').should('be.visible');
    
    // Fill in too short title and check for validation
    cy.get('input[name="title"]').type('A');
    cy.get('button[type="submit"]').click();
    cy.contains('Title must be at least 3 characters').should('be.visible');
  });

  it('should handle form submission correctly', () => {
    // Intercept the API call
    cy.intercept('POST', '/api/tasks', {
      statusCode: 201,
      body: {
        id: '1',
        title: 'New Test Task',
        description: 'This is a test task description',
        type: 'script',
        status: 'pending',
        createdAt: new Date().toISOString()
      }
    }).as('createTask');
    
    // Fill in the form
    cy.get('input[name="title"]').type('New Test Task');
    cy.get('textarea[name="description"]').type('This is a test task description');
    cy.get('select[name="type"]').select('script');
    
    // Add additional options based on selected type
    cy.get('input[name="scriptPath"]').type('/path/to/script.py');
    cy.get('textarea[name="parameters"]').type('--flag1 value1 --flag2 value2');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Verify the API call
    cy.wait('@createTask').its('request.body').should('deep.include', {
      title: 'New Test Task',
      description: 'This is a test task description',
      type: 'script'
    });
    
    // Check for success message
    cy.contains('Task created successfully').should('be.visible');
    
    // Check that we are redirected to the task details page
    cy.url().should('include', '/tasks/1');
  });

  it('should navigate back to tasks list when clicking cancel', () => {
    // Click cancel button
    cy.get('button[type="button"]').contains('Cancel').click();
    
    // Check that we are redirected to the tasks list
    cy.url().should('include', '/tasks');
  });

  it('should dynamically show/hide fields based on task type', () => {
    // Initially, no additional fields should be visible
    cy.get('input[name="scriptPath"]').should('not.exist');
    cy.get('textarea[name="parameters"]').should('not.exist');
    cy.get('textarea[name="dockerfileContent"]').should('not.exist');
    
    // Select script type
    cy.get('select[name="type"]').select('script');
    
    // Script-specific fields should be visible
    cy.get('input[name="scriptPath"]').should('be.visible');
    cy.get('textarea[name="parameters"]').should('be.visible');
    cy.get('textarea[name="dockerfileContent"]').should('not.exist');
    
    // Change to docker type
    cy.get('select[name="type"]').select('docker');
    
    // Docker-specific fields should be visible
    cy.get('input[name="scriptPath"]').should('not.exist');
    cy.get('textarea[name="parameters"]').should('not.exist');
    cy.get('textarea[name="dockerfileContent"]').should('be.visible');
  });
}); 