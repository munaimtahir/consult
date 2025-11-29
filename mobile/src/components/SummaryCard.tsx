/**
 * Summary card component for displaying dashboard statistics.
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
import { formatNumber } from '../utils/format';

interface SummaryCardProps {
  /**
   * Card title.
   */
  title: string;
  /**
   * Numeric value to display.
   */
  value: number;
  /**
   * Icon emoji.
   */
  icon?: string;
  /**
   * Card color variant.
   */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error';
  /**
   * Callback when the card is pressed.
   */
  onPress?: () => void;
  /**
   * Custom container style.
   */
  style?: ViewStyle;
}

const variantColors = {
  default: {
    background: colors.surface,
    text: colors.textPrimary,
    value: colors.primary,
  },
  primary: {
    background: colors.primaryLight,
    text: colors.white,
    value: colors.white,
  },
  success: {
    background: colors.successLight,
    text: colors.white,
    value: colors.white,
  },
  warning: {
    background: colors.warningLight,
    text: colors.white,
    value: colors.white,
  },
  error: {
    background: colors.errorLight,
    text: colors.white,
    value: colors.white,
  },
};

export const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  icon,
  variant = 'default',
  onPress,
  style,
}) => {
  const colorScheme = variantColors[variant];
  
  const content = (
    <View style={[styles.container, { backgroundColor: colorScheme.background }, style]}>
      {icon && (
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>{icon}</Text>
        </View>
      )}
      <Text style={[styles.value, { color: colorScheme.value }]}>
        {formatNumber(value)}
      </Text>
      <Text style={[styles.title, { color: colorScheme.text }]}>
        {title}
      </Text>
    </View>
  );

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
        {content}
      </TouchableOpacity>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 100,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  } as ViewStyle,
  iconContainer: {
    marginBottom: spacing.xs,
  } as ViewStyle,
  icon: {
    fontSize: 24,
  } as TextStyle,
  value: {
    ...textStyles.displayMedium,
    marginBottom: spacing.xs,
  } as TextStyle,
  title: {
    ...textStyles.labelSmall,
    textAlign: 'center',
    textTransform: 'uppercase',
  } as TextStyle,
});
