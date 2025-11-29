/**
 * Consult card component for displaying consult list items.
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
import { ConsultListItem } from '../api/types';
import { colors } from '../theme/colors';
import { spacing, borderRadius } from '../theme/spacing';
import { textStyles } from '../theme/typography';
import { StatusBadge } from './StatusBadge';
import { getRelativeTime } from '../utils/date';
import { truncateText } from '../utils/format';

interface ConsultCardProps {
  /**
   * Consult data to display.
   */
  consult: ConsultListItem;
  /**
   * Callback when the card is pressed.
   */
  onPress: () => void;
  /**
   * Custom container style.
   */
  style?: ViewStyle;
}

export const ConsultCard: React.FC<ConsultCardProps> = ({
  consult,
  onPress,
  style,
}) => {
  return (
    <TouchableOpacity
      style={[styles.container, consult.is_overdue && styles.containerOverdue, style]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.patientInfo}>
          <Text style={styles.patientName} numberOfLines={1}>
            {consult.patient_name}
          </Text>
          <Text style={styles.mrn}>MRN: {consult.patient_mrn}</Text>
        </View>
        <StatusBadge value={consult.urgency} type="urgency" size="small" />
      </View>

      {/* Location */}
      {consult.patient_location && (
        <Text style={styles.location} numberOfLines={1}>
          📍 {consult.patient_location}
        </Text>
      )}

      {/* Reason */}
      <Text style={styles.reason} numberOfLines={2}>
        {truncateText(consult.reason_for_consult, 100)}
      </Text>

      {/* Department info */}
      <View style={styles.departmentRow}>
        <Text style={styles.departmentLabel}>From:</Text>
        <Text style={styles.departmentValue} numberOfLines={1}>
          {consult.requesting_department_name}
        </Text>
        <Text style={styles.departmentLabel}>To:</Text>
        <Text style={styles.departmentValue} numberOfLines={1}>
          {consult.target_department_name}
        </Text>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <StatusBadge value={consult.status} type="status" size="small" />
        <View style={styles.timestampContainer}>
          {consult.is_overdue && (
            <Text style={styles.overdueText}>⚠️ Overdue</Text>
          )}
          <Text style={styles.timestamp}>
            {getRelativeTime(consult.created_at)}
          </Text>
        </View>
      </View>

      {/* Assigned to */}
      {consult.assigned_to_name && (
        <Text style={styles.assignedTo}>
          👨‍⚕️ {consult.assigned_to_name}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginHorizontal: spacing.lg,
    marginVertical: spacing.sm,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  } as ViewStyle,
  containerOverdue: {
    borderLeftWidth: 4,
    borderLeftColor: colors.error,
  } as ViewStyle,
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  } as ViewStyle,
  patientInfo: {
    flex: 1,
    marginRight: spacing.sm,
  } as ViewStyle,
  patientName: {
    ...textStyles.h4,
    color: colors.textPrimary,
  } as TextStyle,
  mrn: {
    ...textStyles.caption,
    color: colors.textSecondary,
    marginTop: spacing.xxs,
  } as TextStyle,
  location: {
    ...textStyles.bodySmall,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  } as TextStyle,
  reason: {
    ...textStyles.body,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  } as TextStyle,
  departmentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  } as ViewStyle,
  departmentLabel: {
    ...textStyles.caption,
    color: colors.textSecondary,
    marginRight: spacing.xs,
  } as TextStyle,
  departmentValue: {
    ...textStyles.bodySmall,
    color: colors.textPrimary,
    flex: 1,
    marginRight: spacing.sm,
  } as TextStyle,
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as ViewStyle,
  timestampContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  } as ViewStyle,
  overdueText: {
    ...textStyles.caption,
    color: colors.error,
    marginRight: spacing.sm,
  } as TextStyle,
  timestamp: {
    ...textStyles.caption,
    color: colors.textSecondary,
  } as TextStyle,
  assignedTo: {
    ...textStyles.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  } as TextStyle,
});
