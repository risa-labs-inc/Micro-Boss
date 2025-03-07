describe('Login Page', () => {
  beforeEach(() => {
    // Visit the login page before each test
    cy.visit('/login');
  });

  it('should display the login page correctly', () => {
    // Check for header
    cy.get('h1').should('contain', 'Login');
    
    // Check for the form elements
    cy.get('form').should('exist');
    cy.get('input[name="email"]').should('exist');
    cy.get('input[name="password"]').should('exist');
    cy.get('button[type="submit"]').should('exist');
    
    // Check for the register link
    cy.contains('a', 'Register').should('have.attr', 'href', '/register');
  });

  it('should validate form inputs', () => {
    // Try to submit empty form
    cy.get('button[type="submit"]').click();
    
    // Check for validation errors
    cy.contains('Email is required').should('be.visible');
    cy.contains('Password is required').should('be.visible');
    
    // Enter invalid email
    cy.get('input[name="email"]').type('invalid-email');
    cy.get('button[type="submit"]').click();
    
    // Check for email validation error
    cy.contains('Invalid email format').should('be.visible');
  });

  it('should handle login with valid credentials', () => {
    // Intercept API call
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        token: 'fake-jwt-token',
        user: {
          id: '1',
          name: 'Test User',
          email: 'test@example.com'
        }
      }
    }).as('loginRequest');
    
    // Fill in login form with valid credentials
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Verify request
    cy.wait('@loginRequest').its('request.body').should('deep.include', {
      email: 'test@example.com',
      password: 'password123'
    });
    
    // Verify user is redirected to dashboard
    cy.url().should('include', '/dashboard');
  });

  it('should handle login failure', () => {
    // Intercept API call with error response
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 401,
      body: { 
        message: 'Invalid credentials' 
      }
    }).as('loginFailure');
    
    // Fill in login form with invalid credentials
    cy.get('input[name="email"]').type('wrong@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Verify request
    cy.wait('@loginFailure');
    
    // Verify error message is displayed
    cy.contains('Invalid credentials').should('be.visible');
    
    // Verify user is not redirected
    cy.url().should('include', '/login');
  });
}); 