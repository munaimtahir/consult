import React, { useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { useAuth } from '../../hooks/useAuth';
import { getPermissionsSummary } from '../../config/permissions';
import { colors } from '../../theme/colors';
import { spacing, borderRadius } from '../../theme/spacing';
import { textStyles } from '../../theme/typography';

export const ProfileScreen = () => {
  const { user, logout, isLoading } = useAuth();

  /**
   * Handle logout.
   */
  const handleLogout = useCallback(() => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: () => logout(),
        },
      ]
    );
  }, [logout]);

  if (!user) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>User data not available</Text>
      </View>
    );
  }

  const permissions = getPermissionsSummary(user);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* Profile Header */}
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user.first_name.charAt(0)}{user.last_name.charAt(0)}
          </Text>
        </View>
        <Text style={styles.name}>
          {user.first_name} {user.last_name}
        </Text>
        <Text style={styles.designation}>{user.designation_display || user.role}</Text>
        <Text style={styles.email}>{user.email}</Text>
      </View>

      {/* User Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account Information</Text>
        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Username</Text>
            <Text style={styles.infoValue}>{user.username}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Role</Text>
            <Text style={styles.infoValue}>{user.role}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Department</Text>
            <Text style={styles.infoValue}>{user.department_name || 'N/A'}</Text>
          </View>
          {user.phone_number && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Phone</Text>
              <Text style={styles.infoValue}>{user.phone_number}</Text>
            </View>
          )}
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>On Call</Text>
            <Text style={[styles.infoValue, user.is_on_call && styles.infoValueHighlight]}>
              {user.is_on_call ? 'Yes' : 'No'}
            </Text>
          </View>
        </View>
      </View>

      {/* Permissions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Permissions</Text>
        <View style={styles.card}>
          <View style={styles.permissionRow}>
            <View style={[styles.permissionIcon, permissions.hodAccess && styles.permissionIconActive]}>
              <Text style={styles.permissionIconText}>{permissions.hodAccess ? '✓' : '✕'}</Text>
            </View>
            <View style={styles.permissionContent}>
              <Text style={styles.permissionLabel}>HOD Dashboard Access</Text>
              <Text style={styles.permissionDescription}>
                View department dashboard and statistics
              </Text>
            </View>
          </View>
          <View style={styles.permissionRow}>
            <View style={[styles.permissionIcon, permissions.departmentView && styles.permissionIconActive]}>
              <Text style={styles.permissionIconText}>{permissions.departmentView ? '✓' : '✕'}</Text>
            </View>
            <View style={styles.permissionContent}>
              <Text style={styles.permissionLabel}>Department Consults View</Text>
              <Text style={styles.permissionDescription}>
                View all consults in your department
              </Text>
            </View>
          </View>
          <View style={styles.permissionRow}>
            <View style={[styles.permissionIcon, permissions.canAssign && styles.permissionIconActive]}>
              <Text style={styles.permissionIconText}>{permissions.canAssign ? '✓' : '✕'}</Text>
            </View>
            <View style={styles.permissionContent}>
              <Text style={styles.permissionLabel}>Assign Consults</Text>
              <Text style={styles.permissionDescription}>
                Assign consults to department members
              </Text>
            </View>
          </View>
          <View style={styles.permissionRow}>
            <View style={[styles.permissionIcon, permissions.globalView && styles.permissionIconActive]}>
              <Text style={styles.permissionIconText}>{permissions.globalView ? '✓' : '✕'}</Text>
            </View>
            <View style={styles.permissionContent}>
              <Text style={styles.permissionLabel}>Global Dashboard Access</Text>
              <Text style={styles.permissionDescription}>
                View system-wide statistics and consults
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* App Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App Information</Text>
        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Version</Text>
            <Text style={styles.infoValue}>1.0.0</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Platform</Text>
            <Text style={styles.infoValue}>Android</Text>
          </View>
        </View>
      </View>

      {/* Logout Button */}
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}
        disabled={isLoading}
      >
        <Text style={styles.logoutButtonText}>
          {isLoading ? 'Logging out...' : 'Logout'}
        </Text>
      </TouchableOpacity>
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
    alignItems: 'center',
    paddingVertical: spacing.xl,
    marginBottom: spacing.lg,
  } as ViewStyle,
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  } as ViewStyle,
  avatarText: {
    ...textStyles.displayMedium,
    color: colors.white,
  } as TextStyle,
  name: {
    ...textStyles.h2,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  } as TextStyle,
  designation: {
    ...textStyles.body,
    color: colors.primary,
    marginBottom: spacing.xs,
  } as TextStyle,
  email: {
    ...textStyles.bodySmall,
    color: colors.textSecondary,
  } as TextStyle,
  section: {
    marginBottom: spacing.xl,
  } as ViewStyle,
  sectionTitle: {
    ...textStyles.h4,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
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
  } as TextStyle,
  infoValue: {
    ...textStyles.body,
    color: colors.textPrimary,
  } as TextStyle,
  infoValueHighlight: {
    color: colors.success,
    fontWeight: '600',
  } as TextStyle,
  permissionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.gray100,
  } as ViewStyle,
  permissionIcon: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.gray200,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  } as ViewStyle,
  permissionIconActive: {
    backgroundColor: colors.success,
  } as ViewStyle,
  permissionIconText: {
    color: colors.white,
    fontWeight: 'bold',
    fontSize: 14,
  } as TextStyle,
  permissionContent: {
    flex: 1,
  } as ViewStyle,
  permissionLabel: {
    ...textStyles.label,
    color: colors.textPrimary,
  } as TextStyle,
  permissionDescription: {
    ...textStyles.caption,
    color: colors.textSecondary,
    marginTop: spacing.xxs,
  } as TextStyle,
  logoutButton: {
    backgroundColor: colors.error,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.lg,
    alignItems: 'center',
    marginTop: spacing.lg,
  } as ViewStyle,
  logoutButtonText: {
    ...textStyles.button,
    color: colors.white,
    fontSize: 18,
  } as TextStyle,
  errorText: {
    ...textStyles.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xl,
  } as TextStyle,
});