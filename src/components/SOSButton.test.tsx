import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { SOSButton } from './SOSButton';

describe('SOSButton', () => {
  it('renders correctly and is accessible', () => {
    const { getByA11yLabel } = render(<SOSButton onPress={() => {}} />);
    const button = getByA11yLabel('SOS Emergency Button');
    expect(button).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPressMock = jest.fn();
    const { getByA11yLabel } = render(<SOSButton onPress={onPressMock} />);
    const button = getByA11yLabel('SOS Emergency Button');
    fireEvent.press(button);
    expect(onPressMock).toHaveBeenCalled();
  });

  it('is disabled when disabled prop is true', () => {
    const { getByA11yLabel } = render(<SOSButton onPress={() => {}} disabled={true} />);
    const button = getByA11yLabel('SOS Emergency Button');
    expect(button.props.accessibilityState.disabled).toBe(true);
  });
});
