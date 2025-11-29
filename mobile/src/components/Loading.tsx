/**
 * Loading indicator component.
 */

import React from 'react';
import {
  View,
  ActivityIndicator,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { colors } from '../theme/colors';
import { spacing } from '../theme/spacing';
import { textStyles } from '../theme/typography';

interface LoadingProps {
  /**
   * Loading message to display.
   */
  message?: string;
  /**
   * Size of the activity indicator.
   */
  size?: 'small' | 'large';
  /**
   * Whether to show as full screen.
   */
  fullScreen?: boolean;
  /**
   * Custom container style.
   */
  style?: ViewStyle;
}

export const Loading: React.FC<LoadingProps> = ({
  message = 'Loading...',
  size = 'large',
  fullScreen = false,
  style,
}) => {
  return (
    <View style={[styles.container, fullScreen && styles.fullScreen, style]}>
      <ActivityIndicator size={size} color={colors.primary} />
      {message && <Text style={styles.message}>{message}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  } as ViewStyle,
  fullScreen: {
    flex: 1,
    backgroundColor: colors.background,
  } as ViewStyle,
  message: {
    ...textStyles.body,
    color: colors.textSecondary,
    marginTop: spacing.md,
  } as TextStyle,
});
