import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from '../Button';

describe('Button Component', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies primary variant classes by default', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByTestId('button');
    expect(button).toHaveClass('bg-blue-500');
    expect(button).toHaveClass('text-white');
  });

  it('applies secondary variant classes when specified', () => {
    render(<Button variant="secondary">Click me</Button>);
    const button = screen.getByTestId('button');
    expect(button).toHaveClass('bg-gray-500');
    expect(button).toHaveClass('text-white');
  });

  it('applies success variant classes when specified', () => {
    render(<Button variant="success">Click me</Button>);
    const button = screen.getByTestId('button');
    expect(button).toHaveClass('bg-green-500');
    expect(button).toHaveClass('text-white');
  });

  it('applies danger variant classes when specified', () => {
    render(<Button variant="danger">Click me</Button>);
    const button = screen.getByTestId('button');
    expect(button).toHaveClass('bg-red-500');
    expect(button).toHaveClass('text-white');
  });
}); 