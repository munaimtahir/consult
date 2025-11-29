/**
 * Status badge component for displaying consult status.
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { colors, getStatusColor, getUrgencyColor } from '../theme/colors';
import { spacing, borderRadius } from '../theme/spacing';
import { textStyles } from '../theme/typography';
import { formatStatus, formatUrgency } from '../utils/format';

interface StatusBadgeProps {
  /**
   * Status or urgency value.
   */
  value: string;
  /**
   * Type of badge (status or urgency).
   */
  type?: 'status' | 'urgency';
  /**
   * Size variant.
   */
  size?: 'small' | 'medium';
  /**
   * Custom container style.
   */
  style?: ViewStyle;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  value,
  type = 'status',
  size = 'medium',
  style,
}) => {
  const backgroundColor = type === 'status' ? getStatusColor(value) : getUrgencyColor(value);
  const label = type === 'status' ? formatStatus(value) : formatUrgency(value);
  
  return (
    <View
      style={[
        styles.container,
        size === 'small' && styles.containerSmall,
        { backgroundColor },
        style,
      ]}
    >
      <Text style={[styles.text, size === 'small' && styles.textSmall]}>
        {label}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
    alignSelf: 'flex-start',
  } as ViewStyle,
  containerSmall: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xxs,
  } as ViewStyle,
  text: {
    ...textStyles.labelSmall,
    color: colors.white,
    textTransform: 'uppercase',
  } as TextStyle,
  textSmall: {
    ...textStyles.captionSmall,
  } as TextStyle,
});
