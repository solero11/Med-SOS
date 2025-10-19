/**
 * SOSButton Component
 * Accessibility:
 * - Uses accessibilityLabel and accessibilityRole for screen readers.
 * - Large touch target and high-contrast color for visibility.
 * - Designed for hands-free activation via wake word integration.
 * Mobile-first layout: Centered, large button, responsive padding.
 */
import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View, Platform } from 'react-native';

interface SOSButtonProps {
  onPress: () => void;
  disabled?: boolean;
}

export const SOSButton: React.FC<SOSButtonProps> = ({ onPress, disabled }) => (
  <View style={styles.container}>
    <TouchableOpacity
      style={[styles.button, disabled ? styles.buttonDisabled : null]}
      onPress={onPress}
      disabled={disabled}
      accessibilityLabel="SOS Emergency Button"
      accessibilityRole="button"
      accessibilityState={{ disabled }}
    >
      <Text style={styles.text}>SOS</Text>
    </TouchableOpacity>
  </View>
);

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 32,
  },
  button: {
    backgroundColor: '#d32f2f',
    borderRadius: 48,
    paddingVertical: 24,
    paddingHorizontal: 48,
    elevation: Platform.OS === 'android' ? 4 : 0,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  buttonDisabled: {
    backgroundColor: '#bdbdbd',
  },
  text: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
    letterSpacing: 2,
  },
});
