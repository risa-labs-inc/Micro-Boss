import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Footer from '../Footer';

describe('Footer Component', () => {
  it('renders the copyright text with current year', () => {
    render(<Footer />);
    const currentYear = new Date().getFullYear().toString();
    const copyrightText = screen.getByText((content) => 
      content.includes(`© ${currentYear} Microboss. All rights reserved.`)
    );
    expect(copyrightText).toBeInTheDocument();
  });

  it('renders all navigation links', () => {
    render(<Footer />);
    
    // Check each link exists
    const aboutLink = screen.getByRole('link', { name: /about/i });
    const docsLink = screen.getByRole('link', { name: /documentation/i });
    const termsLink = screen.getByRole('link', { name: /terms/i });
    const privacyLink = screen.getByRole('link', { name: /privacy/i });
    
    expect(aboutLink).toBeInTheDocument();
    expect(docsLink).toBeInTheDocument();
    expect(termsLink).toBeInTheDocument();
    expect(privacyLink).toBeInTheDocument();
    
    // Check they have the correct href attributes
    expect(aboutLink).toHaveAttribute('href', '/about');
    expect(docsLink).toHaveAttribute('href', '/docs');
    expect(termsLink).toHaveAttribute('href', '/terms');
    expect(privacyLink).toHaveAttribute('href', '/privacy');
  });

  it('has the appropriate styling classes', () => {
    render(<Footer />);
    
    // Check the footer has the right classes
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveClass('bg-gray-100');
    expect(footer).toHaveClass('border-t');
    expect(footer).toHaveClass('border-gray-200');
    
    // Check links have the right classes
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveClass('text-gray-600');
      expect(link).toHaveClass('text-sm');
    });
  });
}); 