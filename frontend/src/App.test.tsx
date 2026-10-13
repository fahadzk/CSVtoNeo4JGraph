import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';

describe('CSV graph app', () => {
  it('renders the upload workflow', () => {
    render(<App />);
    expect(screen.getByText('CSV to Neo4j Graph')).toBeTruthy();
    expect(screen.getByText('1. Upload CSV')).toBeTruthy();
    expect(screen.getByLabelText(/file/i)).toBeTruthy();
  });
});
