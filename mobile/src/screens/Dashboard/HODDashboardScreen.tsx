import React, { useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useDashboard } from '../../hooks/useDashboard';
import { useAuth } from '../../hooks/useAuth';
import { Loading } from '../../components/Loading';
import { ErrorState } from '../../components/ErrorState';
import { SummaryCard } from '../../components/SummaryCard';
import { colors } from '../../theme/colors';
import { spacing, borderRadius } from '../../theme/spacing';
import { textStyles } from '../../theme/typography';
import { RootStackParamList } from '../../navigation/types';
import { getRelativeTime } from '../../utils/date';
import { formatStatus } from '../../utils/format';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

export const HODDashboardScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  const { user } = useAuth();
  const { data, isLoading, isRefreshing, error, fetchDashboard, refresh } = useDashboard();

  /**
   * Fetch dashboard data on mount.
   */
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  /**
   * Handle consult press.
   */
  const handleConsultPress = useCallback((consultId: number) => {
    navigation.navigate('ConsultDetail', { consultId });
  }, [navigation]);

  // Show loading state
  if (isLoading && !data) {
    return <Loading fullScreen message="Loading dashboard..." />;
  }

  // Show error state
  if (error && !data) {
    return <ErrorState message={error} onRetry={() => fetchDashboard()} />;
  }

  if (!data) {
    return <ErrorState message="Dashboard data not available" onRetry={() => fetchDashboard()} />;
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={refresh}
          tintColor={colors.primary}
        />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Department Dashboard</Text>
        <Text style={styles.headerSubtitle}>{user?.department_name || 'Your Department'}</Text>
      </View>

      {/* Summary Cards */}
      <View style={styles.summarySection}>
        <Text style={styles.sectionTitle}>{"Today's Overview"}</Text>
        <View style={styles.summaryGrid}>
          <SummaryCard
            title="Total"
            value={data.summary.total_today}
            icon="📋"
            variant="primary"
            style={styles.summaryCard}
          />
          <SummaryCard
            title="Pending"
            value={data.summary.pending}
            icon="⏳"
            variant="warning"
            style={styles.summaryCard}
          />
          <SummaryCard
            title="In Progress"
            value={data.summary.in_progress}
            icon="🔄"
            variant="default"
            style={styles.summaryCard}
          />
          <SummaryCard
            title="Completed"
            value={data.summary.completed}
            icon="✅"
            variant="success"
            style={styles.summaryCard}
          />
          <SummaryCard
            title="Delayed"
            value={data.summary.delayed}
            icon="⚠️"
            variant="error"
            style={styles.summaryCard}
          />
        </View>
      </View>

      {/* Delayed Consults */}
      {data.delayed_list.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            ⚠️ Delayed Consults ({data.delayed_list.length})
          </Text>
          <View style={styles.delayedList}>
            {data.delayed_list.map((consult) => (
              <TouchableOpacity
                key={consult.id}
                style={styles.delayedItem}
                onPress={() => handleConsultPress(consult.id)}
              >
                <View style={styles.delayedItemContent}>
                  <Text style={styles.delayedPatientName}>{consult.patient_name}</Text>
                  <Text style={styles.delayedStatus}>{formatStatus(consult.status)}</Text>
                </View>
                <View style={styles.delayedItemMeta}>
                  <Text style={styles.delayedTime}>
                    Created: {getRelativeTime(consult.created_at)}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* Activity Summary */}
      {data.activity.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{"Today's Activity"}</Text>
          <View style={styles.activityList}>
            {data.activity.map((item, index) => (
              <View key={index} style={styles.activityItem}>
                <View style={styles.activityAvatar}>
                  <Text style={styles.activityAvatarText}>
                    {item.user.charAt(0).toUpperCase()}
                  </Text>
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityUser}>{item.user}</Text>
                  <Text style={styles.activityCount}>
                    {item.acknowledged} consult{item.acknowledged !== 1 ? 's' : ''} acknowledged
                  </Text>
                </View>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Empty Activity State */}
      {data.activity.length === 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{"Today's Activity"}</Text>
          <View style={styles.emptyActivity}>
            <Text style={styles.emptyActivityText}>No activity recorded today</Text>
          </View>
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
  header: {
    marginBottom: spacing.xl,
  } as ViewStyle,
  headerTitle: {
    ...textStyles.h2,
    color: colors.textPrimary,
  } as TextStyle,
  headerSubtitle: {
    ...textStyles.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  } as TextStyle,
  summarySection: {
    marginBottom: spacing.xl,
  } as ViewStyle,
  sectionTitle: {
    ...textStyles.h4,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  } as TextStyle,
  summaryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -spacing.xs,
  } as ViewStyle,
  summaryCard: {
    width: '48%',
    marginHorizontal: '1%',
    marginBottom: spacing.sm,
  } as ViewStyle,
  section: {
    marginBottom: spacing.xl,
  } as ViewStyle,
  delayedList: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  } as ViewStyle,
  delayedItem: {
    padding: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
    borderLeftWidth: 4,
    borderLeftColor: colors.error,
  } as ViewStyle,
  delayedItemContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
  } as ViewStyle,
  delayedPatientName: {
    ...textStyles.label,
    color: colors.textPrimary,
  } as TextStyle,
  delayedStatus: {
    ...textStyles.caption,
    color: colors.error,
  } as TextStyle,
  delayedItemMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  } as ViewStyle,
  delayedTime: {
    ...textStyles.caption,
    color: colors.textSecondary,
  } as TextStyle,
  activityList: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
  } as ViewStyle,
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  } as ViewStyle,
  activityAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  } as ViewStyle,
  activityAvatarText: {
    ...textStyles.label,
    color: colors.white,
    fontSize: 18,
  } as TextStyle,
  activityContent: {
    flex: 1,
  } as ViewStyle,
  activityUser: {
    ...textStyles.label,
    color: colors.textPrimary,
  } as TextStyle,
  activityCount: {
    ...textStyles.caption,
    color: colors.textSecondary,
    marginTop: spacing.xxs,
  } as TextStyle,
  emptyActivity: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.xl,
    alignItems: 'center',
  } as ViewStyle,
  emptyActivityText: {
    ...textStyles.body,
    color: colors.textSecondary,
  } as TextStyle,
});