import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  FlatList,
  RefreshControl,
  StyleSheet,
  ViewStyle,
  Text,
  TouchableOpacity,
  TextStyle,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useDepartmentConsults } from '../../hooks/useConsults';
import { useAuth } from '../../hooks/useAuth';
import { ConsultCard } from '../../components/ConsultCard';
import { Loading } from '../../components/Loading';
import { ErrorState } from '../../components/ErrorState';
import { EmptyState } from '../../components/EmptyState';
import { colors } from '../../theme/colors';
import { spacing, borderRadius } from '../../theme/spacing';
import { textStyles } from '../../theme/typography';
import { RootStackParamList } from '../../navigation/types';
import { CONSULT_STATUS, ConsultStatus } from '../../config/constants';
import { ConsultListItem } from '../../api/types';

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

/**
 * Filter chip options.
 */
const FILTER_OPTIONS: Array<{ key: ConsultStatus | 'ALL'; label: string }> = [
  { key: 'ALL', label: 'All' },
  { key: CONSULT_STATUS.PENDING, label: 'Pending' },
  { key: CONSULT_STATUS.ACKNOWLEDGED, label: 'Acknowledged' },
  { key: CONSULT_STATUS.IN_PROGRESS, label: 'In Progress' },
  { key: CONSULT_STATUS.COMPLETED, label: 'Completed' },
];

export const DepartmentConsultsScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  const { user } = useAuth();
  const [selectedFilter, setSelectedFilter] = useState<ConsultStatus | 'ALL'>('ALL');
  
  const {
    consults,
    isLoading,
    isRefreshing,
    isLoadingMore,
    error,
    hasMore,
    fetchConsults,
    refresh,
    loadMore,
  } = useDepartmentConsults();

  /**
   * Fetch consults on mount and when filter changes.
   */
  useEffect(() => {
    const status = selectedFilter === 'ALL' ? undefined : selectedFilter;
    fetchConsults({ status }, true);
  }, [selectedFilter]);

  /**
   * Handle consult card press.
   */
  const handleConsultPress = useCallback((consult: ConsultListItem) => {
    navigation.navigate('ConsultDetail', { consultId: consult.id });
  }, [navigation]);

  /**
   * Handle refresh.
   */
  const handleRefresh = useCallback(() => {
    const status = selectedFilter === 'ALL' ? undefined : selectedFilter;
    refresh({ status });
  }, [selectedFilter, refresh]);

  /**
   * Handle load more.
   */
  const handleLoadMore = useCallback(() => {
    if (hasMore && !isLoadingMore) {
      const status = selectedFilter === 'ALL' ? undefined : selectedFilter;
      loadMore({ status });
    }
  }, [hasMore, isLoadingMore, selectedFilter, loadMore]);

  /**
   * Render department header.
   */
  const renderHeader = () => (
    <View style={styles.headerContainer}>
      <Text style={styles.headerTitle}>
        {user?.department_name || 'Department'} Consults
      </Text>
    </View>
  );

  /**
   * Render filter chips.
   */
  const renderFilters = () => (
    <View style={styles.filtersContainer}>
      {FILTER_OPTIONS.map((option) => (
        <TouchableOpacity
          key={option.key}
          style={[
            styles.filterChip,
            selectedFilter === option.key && styles.filterChipSelected,
          ]}
          onPress={() => setSelectedFilter(option.key)}
        >
          <Text
            style={[
              styles.filterChipText,
              selectedFilter === option.key && styles.filterChipTextSelected,
            ]}
          >
            {option.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  /**
   * Render list item.
   */
  const renderItem = ({ item }: { item: ConsultListItem }) => (
    <ConsultCard
      consult={item}
      onPress={() => handleConsultPress(item)}
    />
  );

  /**
   * Render footer (loading more indicator).
   */
  const renderFooter = () => {
    if (!isLoadingMore) return null;
    return <Loading size="small" message="Loading more..." />;
  };

  // Show loading state on initial load
  if (isLoading && consults.length === 0) {
    return (
      <View style={styles.container}>
        {renderHeader()}
        {renderFilters()}
        <Loading fullScreen message="Loading department consults..." />
      </View>
    );
  }

  // Show error state
  if (error && consults.length === 0) {
    return (
      <View style={styles.container}>
        {renderHeader()}
        {renderFilters()}
        <ErrorState message={error} onRetry={handleRefresh} />
      </View>
    );
  }

  // Show empty state
  if (!isLoading && consults.length === 0) {
    return (
      <View style={styles.container}>
        {renderHeader()}
        {renderFilters()}
        <EmptyState
          icon="🏥"
          title="No Department Consults"
          message={
            selectedFilter === 'ALL'
              ? 'No consults for your department yet.'
              : `No consults with status "${selectedFilter}".`
          }
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {renderHeader()}
      {renderFilters()}
      <FlatList
        data={consults}
        renderItem={renderItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={colors.primary}
          />
        }
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.5}
        ListFooterComponent={renderFooter}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  } as ViewStyle,
  headerContainer: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  } as ViewStyle,
  headerTitle: {
    ...textStyles.h4,
    color: colors.textPrimary,
  } as TextStyle,
  filtersContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  } as ViewStyle,
  filterChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    backgroundColor: colors.gray100,
    marginRight: spacing.sm,
  } as ViewStyle,
  filterChipSelected: {
    backgroundColor: colors.primary,
  } as ViewStyle,
  filterChipText: {
    ...textStyles.labelSmall,
    color: colors.textSecondary,
  } as TextStyle,
  filterChipTextSelected: {
    color: colors.white,
  } as TextStyle,
  listContent: {
    paddingVertical: spacing.sm,
  } as ViewStyle,
});