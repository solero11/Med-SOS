/**
 * ListeningIndicator Component
 * Accessibility:
 * - Visual indicator for listening state (waveform/avatar).
 * - Can be paired with screen reader announcements when listening starts.
 * Mobile-first layout: Centered, animated, responsive size.
 * Hands-free usage: Activated by wake word or SOS button.
 */
import React from 'react';
import { View, Animated, Easing, StyleSheet } from 'react-native';

interface ListeningIndicatorProps {
  listening: boolean;
}

export const ListeningIndicator: React.FC<ListeningIndicatorProps> = ({ listening }) => {
  const animation = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (listening) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(animation, {
            toValue: 1,
            duration: 800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(animation, {
            toValue: 0,
            duration: 800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      animation.setValue(0);
    }
  }, [listening, animation]);

  const scale = animation.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 1.3],
  });

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.wave, { transform: [{ scale }] }]} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 16,
  },
  wave: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#1976d2',
    opacity: 0.7,
  },
});
