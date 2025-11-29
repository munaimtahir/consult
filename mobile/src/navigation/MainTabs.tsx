import React from 'react';
import { Text, StyleSheet, TextStyle } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MyConsultsScreen } from '../screens/Consults/MyConsultsScreen';
import { DepartmentConsultsScreen } from '../screens/Consults/DepartmentConsultsScreen';
import { HODDashboardScreen } from '../screens/Dashboard/HODDashboardScreen';
import { ProfileScreen } from '../screens/Settings/ProfileScreen';
import { MainTabsParamList } from './types';
import { useAuth } from '../hooks/useAuth';
import { canViewDepartmentConsults, canViewHODDashboard } from '../config/permissions';
import { colors } from '../theme/colors';
import { spacing } from '../theme/spacing';

const Tab = createBottomTabNavigator<MainTabsParamList>();

/**
 * Tab bar icon component.
 */
const TabIcon: React.FC<{ emoji: string; focused: boolean }> = ({ emoji, focused }) => (
  <Text style={[styles.icon, focused && styles.iconFocused]}>{emoji}</Text>
);

export const MainTabs = () => {
  const { user } = useAuth();

  const showDepartmentTab = canViewDepartmentConsults(user);
  const showHODTab = canViewHODDashboard(user);

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          paddingTop: spacing.xs,
          height: 60,
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarLabelStyle: {
          fontSize: 12,
          marginBottom: spacing.xs,
        },
        headerStyle: {
          backgroundColor: colors.surface,
        },
        headerTintColor: colors.textPrimary,
      }}
    >
      <Tab.Screen
        name="MyConsults"
        component={MyConsultsScreen}
        options={{
          title: 'My Consults',
          tabBarIcon: ({ focused }) => <TabIcon emoji="📋" focused={focused} />,
        }}
      />
      {showDepartmentTab && (
        <Tab.Screen
          name="DepartmentConsults"
          component={DepartmentConsultsScreen}
          options={{
            title: 'Department',
            tabBarIcon: ({ focused }) => <TabIcon emoji="🏥" focused={focused} />,
          }}
        />
      )}
      {showHODTab && (
        <Tab.Screen
          name="HODDashboard"
          component={HODDashboardScreen}
          options={{
            title: 'Dashboard',
            tabBarIcon: ({ focused }) => <TabIcon emoji="📊" focused={focused} />,
          }}
        />
      )}
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          title: 'Profile',
          tabBarIcon: ({ focused }) => <TabIcon emoji="👤" focused={focused} />,
        }}
      />
    </Tab.Navigator>
  );
};

const styles = StyleSheet.create({
  icon: {
    fontSize: 24,
    opacity: 0.7,
  } as TextStyle,
  iconFocused: {
    opacity: 1,
  } as TextStyle,
});