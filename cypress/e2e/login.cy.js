describe('Login Page', () => {
  beforeEach(() => {
    // Visit the login page before each test
    cy.visit('/login');
  });

  it('should display the login form', () => {
    // Check that the login page has the expected elements
    cy.get('h1').should('contain', 'Login');
    cy.get('form').should('exist');
    cy.get('input[name="email"]').should('exist');
    cy.get('input[name="password"]').should('exist');
    cy.get('button[type="submit"]').should('exist').and('contain', 'Login');
  });

  it('should show validation errors for empty fields', () => {
    // Submit the form without filling any fields
    cy.get('button[type="submit"]').click();
    
    // Check for validation error messages
    cy.get('form').should('contain', 'Email is required');
    cy.get('form').should('contain', 'Password is required');
  });

  it('should show error for invalid credentials', () => {
    // Fill in invalid credentials
    cy.get('input[name="email"]').type('wrong@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Check for error message
    cy.get('[role="alert"]').should('contain', 'Invalid credentials');
  });

  it('should redirect to dashboard on successful login', () => {
    // Intercept the login API call and mock a successful response
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        user: {
          id: '1',
          name: 'Test User',
          email: 'test@example.com'
        },
        token: 'fake-jwt-token'
      }
    }).as('loginRequest');
    
    // Fill in valid credentials
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Wait for the login API call
    cy.wait('@loginRequest');
    
    // Check that we're redirected to the dashboard
    cy.url().should('include', '/dashboard');
  });
}); 