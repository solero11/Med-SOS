import React from 'react';
import { render } from '@testing-library/react-native';
import { ListeningIndicator } from './ListeningIndicator';

describe('ListeningIndicator', () => {
  it('renders correctly when listening is true', () => {
    const { getByTestId } = render(<ListeningIndicator listening={true} />);
    const indicator = getByTestId('listening-indicator');
    expect(indicator).toBeTruthy();
  });

  it('renders correctly when listening is false', () => {
    const { getByTestId } = render(<ListeningIndicator listening={false} />);
    const indicator = getByTestId('listening-indicator');
    expect(indicator).toBeTruthy();
  });
});
