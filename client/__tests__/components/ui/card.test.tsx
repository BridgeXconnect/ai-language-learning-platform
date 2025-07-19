import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card';

describe('Card Components', () => {
  describe('Card', () => {
    it('renders with default styling', () => {
      render(<Card data-testid="card">Card Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toBeInTheDocument();
      expect(card).toHaveClass(
        'rounded-lg',
        'border',
        'bg-card',
        'text-card-foreground',
        'shadow-sm'
      );
    });

    it('accepts custom className', () => {
      render(<Card className="custom-class" data-testid="card">Card Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('custom-class');
    });

    it('forwards props to div element', () => {
      render(<Card data-testid="card" id="test-id">Card Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveAttribute('id', 'test-id');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<Card ref={ref}>Card Content</Card>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('CardHeader', () => {
    it('renders with default styling', () => {
      render(<CardHeader data-testid="header">Header Content</CardHeader>);
      const header = screen.getByTestId('header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6');
    });

    it('accepts custom className', () => {
      render(<CardHeader className="custom-header" data-testid="header">Header</CardHeader>);
      const header = screen.getByTestId('header');
      expect(header).toHaveClass('custom-header');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<CardHeader ref={ref}>Header</CardHeader>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('CardTitle', () => {
    it('renders with default styling', () => {
      render(<CardTitle data-testid="title">Title Content</CardTitle>);
      const title = screen.getByTestId('title');
      expect(title).toBeInTheDocument();
      expect(title).toHaveClass(
        'text-2xl',
        'font-semibold',
        'leading-none',
        'tracking-tight'
      );
    });

    it('accepts custom className', () => {
      render(<CardTitle className="custom-title" data-testid="title">Title</CardTitle>);
      const title = screen.getByTestId('title');
      expect(title).toHaveClass('custom-title');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<CardTitle ref={ref}>Title</CardTitle>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('CardDescription', () => {
    it('renders with default styling', () => {
      render(<CardDescription data-testid="description">Description Content</CardDescription>);
      const description = screen.getByTestId('description');
      expect(description).toBeInTheDocument();
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });

    it('accepts custom className', () => {
      render(
        <CardDescription className="custom-desc" data-testid="description">
          Description
        </CardDescription>
      );
      const description = screen.getByTestId('description');
      expect(description).toHaveClass('custom-desc');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<CardDescription ref={ref}>Description</CardDescription>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('CardContent', () => {
    it('renders with default styling', () => {
      render(<CardContent data-testid="content">Content</CardContent>);
      const content = screen.getByTestId('content');
      expect(content).toBeInTheDocument();
      expect(content).toHaveClass('p-6', 'pt-0');
    });

    it('accepts custom className', () => {
      render(<CardContent className="custom-content" data-testid="content">Content</CardContent>);
      const content = screen.getByTestId('content');
      expect(content).toHaveClass('custom-content');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<CardContent ref={ref}>Content</CardContent>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('CardFooter', () => {
    it('renders with default styling', () => {
      render(<CardFooter data-testid="footer">Footer Content</CardFooter>);
      const footer = screen.getByTestId('footer');
      expect(footer).toBeInTheDocument();
      expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'pt-0');
    });

    it('accepts custom className', () => {
      render(<CardFooter className="custom-footer" data-testid="footer">Footer</CardFooter>);
      const footer = screen.getByTestId('footer');
      expect(footer).toHaveClass('custom-footer');
    });

    it('forwards ref correctly', () => {
      const ref = jest.fn();
      render(<CardFooter ref={ref}>Footer</CardFooter>);
      expect(ref).toHaveBeenCalled();
    });
  });

  describe('Full Card Example', () => {
    it('renders complete card structure', () => {
      render(
        <Card data-testid="full-card">
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>This is the card content</p>
          </CardContent>
          <CardFooter>
            <button>Action Button</button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByTestId('full-card')).toBeInTheDocument();
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText('This is the card content')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Action Button' })).toBeInTheDocument();
    });
  });
});