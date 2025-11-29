/**
 * Error state component for displaying error messages.
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { colors } from '../theme/colors';
import { spacing, borderRadius } from '../theme/spacing';
import { textStyles } from '../theme/typography';

interface ErrorStateProps {
  /**
   * Error message to display.
   */
  message: string;
  /**
   * Optional retry callback.
   */
  onRetry?: () => void;
  /**
   * Custom container style.
   */
  style?: ViewStyle;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message,
  onRetry,
  style,
}) => {
  return (
    <View style={[styles.container, style]}>
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>⚠️</Text>
      </View>
      <Text style={styles.title}>Something went wrong</Text>
      <Text style={styles.message}>{message}</Text>
      {onRetry && (
        <TouchableOpacity style={styles.retryButton} onPress={onRetry}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
    backgroundColor: colors.background,
  } as ViewStyle,
  iconContainer: {
    marginBottom: spacing.lg,
  } as ViewStyle,
  icon: {
    fontSize: 48,
  } as TextStyle,
  title: {
    ...textStyles.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  } as TextStyle,
  message: {
    ...textStyles.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
  } as TextStyle,
  retryButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
    borderRadius: borderRadius.md,
  } as ViewStyle,
  retryButtonText: {
    ...textStyles.button,
    color: colors.white,
  } as TextStyle,
});
