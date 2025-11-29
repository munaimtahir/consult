/**
 * Empty state component for displaying when no data is available.
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

interface EmptyStateProps {
  /**
   * Title to display.
   */
  title: string;
  /**
   * Description message.
   */
  message?: string;
  /**
   * Icon emoji to display.
   */
  icon?: string;
  /**
   * Action button label.
   */
  actionLabel?: string;
  /**
   * Action button callback.
   */
  onAction?: () => void;
  /**
   * Custom container style.
   */
  style?: ViewStyle;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  message,
  icon = '📋',
  actionLabel,
  onAction,
  style,
}) => {
  return (
    <View style={[styles.container, style]}>
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>{icon}</Text>
      </View>
      <Text style={styles.title}>{title}</Text>
      {message && <Text style={styles.message}>{message}</Text>}
      {actionLabel && onAction && (
        <TouchableOpacity style={styles.actionButton} onPress={onAction}>
          <Text style={styles.actionButtonText}>{actionLabel}</Text>
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
    fontSize: 64,
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
  actionButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xxl,
    borderRadius: borderRadius.md,
  } as ViewStyle,
  actionButtonText: {
    ...textStyles.button,
    color: colors.white,
  } as TextStyle,
});
