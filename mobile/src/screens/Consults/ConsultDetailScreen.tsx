import React, { useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  RefreshControl,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useConsultDetail } from '../../hooks/useConsults';
import { Loading } from '../../components/Loading';
import { ErrorState } from '../../components/ErrorState';
import { StatusBadge } from '../../components/StatusBadge';
import { colors } from '../../theme/colors';
import { spacing, borderRadius } from '../../theme/spacing';
import { textStyles } from '../../theme/typography';
import { RootStackParamList } from '../../navigation/types';
import { formatDateTime, getRelativeTime, formatElapsedTime } from '../../utils/date';
import { CONSULT_STATUS } from '../../config/constants';

type RouteProps = RouteProp<RootStackParamList, 'ConsultDetail'>;
type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export const ConsultDetailScreen = () => {
  const route = useRoute<RouteProps>();
  const navigation = useNavigation<NavigationProp>();
  const { consultId } = route.params;

  const {
    consult,
    isLoading,
    isActionLoading,
    error,
    fetchConsult,
    acknowledge,
    complete,
  } = useConsultDetail(consultId);

  /**
   * Fetch consult details on mount.
   */
  useEffect(() => {
    fetchConsult();
  }, [fetchConsult]);

  /**
   * Handle acknowledge action.
   */
  const handleAcknowledge = useCallback(async () => {
    try {
      await acknowledge();
      Alert.alert('Success', 'Consult acknowledged successfully');
    } catch (err) {
      Alert.alert('Error', 'Failed to acknowledge consult');
    }
  }, [acknowledge]);

  /**
   * Handle complete action.
   */
  const handleComplete = useCallback(() => {
    Alert.alert(
      'Complete Consult',
      'Are you sure you want to mark this consult as completed?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Complete',
          onPress: async () => {
            try {
              await complete();
              Alert.alert('Success', 'Consult completed successfully');
            } catch (err) {
              Alert.alert('Error', 'Failed to complete consult');
            }
          },
        },
      ]
    );
  }, [complete]);

  /**
   * Handle add note action.
   */
  const handleAddNote = useCallback(() => {
    navigation.navigate('AddNote', { consultId });
  }, [navigation, consultId]);

  // Show loading state
  if (isLoading && !consult) {
    return <Loading fullScreen message="Loading consult details..." />;
  }

  // Show error state
  if (error && !consult) {
    return <ErrorState message={error} onRetry={fetchConsult} />;
  }

  if (!consult) {
    return <ErrorState message="Consult not found" onRetry={fetchConsult} />;
  }

  const canAcknowledge = consult.status === CONSULT_STATUS.PENDING;
  const canComplete = consult.status === CONSULT_STATUS.IN_PROGRESS || 
                      consult.status === CONSULT_STATUS.ACKNOWLEDGED;
  const isCompleted = consult.status === CONSULT_STATUS.COMPLETED;
  const isCancelled = consult.status === CONSULT_STATUS.CANCELLED;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl
          refreshing={isLoading}
          onRefresh={fetchConsult}
          tintColor={colors.primary}
        />
      }
    >
      {/* Status Header */}
      <View style={[styles.statusHeader, consult.is_overdue && styles.statusHeaderOverdue]}>
        <View style={styles.statusRow}>
          <StatusBadge value={consult.status} type="status" />
          <StatusBadge value={consult.urgency} type="urgency" style={styles.urgencyBadge} />
        </View>
        {consult.is_overdue && (
          <Text style={styles.overdueText}>⚠️ This consult is overdue</Text>
        )}
      </View>

      {/* Patient Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Patient Information</Text>
        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Name</Text>
            <Text style={styles.infoValue}>{consult.patient.name}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>MRN</Text>
            <Text style={styles.infoValue}>{consult.patient.mrn}</Text>
          </View>
          {consult.patient.location && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Location</Text>
              <Text style={styles.infoValue}>{consult.patient.location}</Text>
            </View>
          )}
        </View>
      </View>

      {/* Consult Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Consult Details</Text>
        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>From</Text>
            <Text style={styles.infoValue}>{consult.requesting_department.name}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>To</Text>
            <Text style={styles.infoValue}>{consult.target_department.name}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Requester</Text>
            <Text style={styles.infoValue}>
              {consult.requester.first_name} {consult.requester.last_name}
            </Text>
          </View>
          {consult.assigned_to && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Assigned To</Text>
              <Text style={styles.infoValue}>
                {consult.assigned_to.first_name} {consult.assigned_to.last_name}
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Clinical Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Clinical Information</Text>
        <View style={styles.card}>
          <View style={styles.textBlock}>
            <Text style={styles.textLabel}>Reason for Consult</Text>
            <Text style={styles.textContent}>{consult.reason_for_consult}</Text>
          </View>
          {consult.clinical_question && (
            <View style={styles.textBlock}>
              <Text style={styles.textLabel}>Clinical Question</Text>
              <Text style={styles.textContent}>{consult.clinical_question}</Text>
            </View>
          )}
          {consult.relevant_history && (
            <View style={styles.textBlock}>
              <Text style={styles.textLabel}>Relevant History</Text>
              <Text style={styles.textContent}>{consult.relevant_history}</Text>
            </View>
          )}
        </View>
      </View>

      {/* Timeline */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Timeline</Text>
        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Created</Text>
            <Text style={styles.infoValue}>{formatDateTime(consult.created_at)}</Text>
          </View>
          {consult.acknowledged_at && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Acknowledged</Text>
              <Text style={styles.infoValue}>{formatDateTime(consult.acknowledged_at)}</Text>
            </View>
          )}
          {consult.completed_at && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Completed</Text>
              <Text style={styles.infoValue}>{formatDateTime(consult.completed_at)}</Text>
            </View>
          )}
          {consult.time_elapsed !== null && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Time Elapsed</Text>
              <Text style={styles.infoValue}>{formatElapsedTime(consult.time_elapsed)}</Text>
            </View>
          )}
        </View>
      </View>

      {/* Notes */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Notes ({consult.notes.length})</Text>
          {!isCompleted && !isCancelled && (
            <TouchableOpacity onPress={handleAddNote}>
              <Text style={styles.addNoteLink}>+ Add Note</Text>
            </TouchableOpacity>
          )}
        </View>
        {consult.notes.length === 0 ? (
          <View style={styles.emptyNotes}>
            <Text style={styles.emptyNotesText}>No notes yet</Text>
          </View>
        ) : (
          consult.notes.map((note) => (
            <View key={note.id} style={styles.noteCard}>
              <View style={styles.noteHeader}>
                <Text style={styles.noteAuthor}>{note.author_name}</Text>
                <Text style={styles.noteTime}>{getRelativeTime(note.created_at)}</Text>
              </View>
              <Text style={styles.noteType}>{note.note_type}</Text>
              <Text style={styles.noteContent}>{note.content}</Text>
              {note.recommendations && (
                <View style={styles.noteRecommendations}>
                  <Text style={styles.noteRecommendationsLabel}>Recommendations:</Text>
                  <Text style={styles.noteRecommendationsText}>{note.recommendations}</Text>
                </View>
              )}
            </View>
          ))
        )}
      </View>

      {/* Actions */}
      {!isCompleted && !isCancelled && (
        <View style={styles.actionsContainer}>
          {canAcknowledge && (
            <TouchableOpacity
              style={[styles.actionButton, styles.acknowledgeButton]}
              onPress={handleAcknowledge}
              disabled={isActionLoading}
            >
              <Text style={styles.actionButtonText}>
                {isActionLoading ? 'Processing...' : 'Acknowledge'}
              </Text>
            </TouchableOpacity>
          )}
          {canComplete && (
            <TouchableOpacity
              style={[styles.actionButton, styles.completeButton]}
              onPress={handleComplete}
              disabled={isActionLoading}
            >
              <Text style={styles.actionButtonText}>
                {isActionLoading ? 'Processing...' : 'Complete'}
              </Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={[styles.actionButton, styles.noteButton]}
            onPress={handleAddNote}
            disabled={isActionLoading}
          >
            <Text style={styles.noteButtonText}>Add Note</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  } as ViewStyle,
  contentContainer: {
    padding: spacing.lg,
    paddingBottom: spacing.xxxxl,
  } as ViewStyle,
  statusHeader: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  } as ViewStyle,
  statusHeaderOverdue: {
    borderLeftWidth: 4,
    borderLeftColor: colors.error,
  } as ViewStyle,
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  } as ViewStyle,
  urgencyBadge: {
    marginLeft: spacing.sm,
  } as ViewStyle,
  overdueText: {
    ...textStyles.bodySmall,
    color: colors.error,
    marginTop: spacing.sm,
  } as TextStyle,
  section: {
    marginBottom: spacing.lg,
  } as ViewStyle,
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as ViewStyle,
  sectionTitle: {
    ...textStyles.h4,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  } as TextStyle,
  addNoteLink: {
    ...textStyles.label,
    color: colors.primary,
  } as TextStyle,
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
  } as ViewStyle,
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  } as ViewStyle,
  infoLabel: {
    ...textStyles.bodySmall,
    color: colors.textSecondary,
    flex: 1,
  } as TextStyle,
  infoValue: {
    ...textStyles.body,
    color: colors.textPrimary,
    flex: 2,
    textAlign: 'right',
  } as TextStyle,
  textBlock: {
    marginBottom: spacing.md,
  } as ViewStyle,
  textLabel: {
    ...textStyles.label,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  } as TextStyle,
  textContent: {
    ...textStyles.body,
    color: colors.textPrimary,
  } as TextStyle,
  emptyNotes: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.xl,
    alignItems: 'center',
  } as ViewStyle,
  emptyNotesText: {
    ...textStyles.body,
    color: colors.textSecondary,
  } as TextStyle,
  noteCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.sm,
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
  } as ViewStyle,
  noteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  } as ViewStyle,
  noteAuthor: {
    ...textStyles.label,
    color: colors.textPrimary,
  } as TextStyle,
  noteTime: {
    ...textStyles.caption,
    color: colors.textSecondary,
  } as TextStyle,
  noteType: {
    ...textStyles.captionSmall,
    color: colors.primary,
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
  } as TextStyle,
  noteContent: {
    ...textStyles.body,
    color: colors.textPrimary,
  } as TextStyle,
  noteRecommendations: {
    marginTop: spacing.sm,
    padding: spacing.sm,
    backgroundColor: colors.gray50,
    borderRadius: borderRadius.sm,
  } as ViewStyle,
  noteRecommendationsLabel: {
    ...textStyles.labelSmall,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  } as TextStyle,
  noteRecommendationsText: {
    ...textStyles.bodySmall,
    color: colors.textPrimary,
  } as TextStyle,
  actionsContainer: {
    marginTop: spacing.lg,
  } as ViewStyle,
  actionButton: {
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginBottom: spacing.sm,
  } as ViewStyle,
  acknowledgeButton: {
    backgroundColor: colors.primary,
  } as ViewStyle,
  completeButton: {
    backgroundColor: colors.success,
  } as ViewStyle,
  noteButton: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.primary,
  } as ViewStyle,
  actionButtonText: {
    ...textStyles.button,
    color: colors.white,
  } as TextStyle,
  noteButtonText: {
    ...textStyles.button,
    color: colors.primary,
  } as TextStyle,
});