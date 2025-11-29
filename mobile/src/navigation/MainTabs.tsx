import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MyConsultsScreen } from '../screens/Consults/MyConsultsScreen';
import { DepartmentConsultsScreen } from '../screens/Consults/DepartmentConsultsScreen';
import { HODDashboardScreen } from '../screens/Dashboard/HODDashboardScreen';
import { ProfileScreen } from '../screens/Settings/ProfileScreen';

export type MainTabsParamList = {
  MyConsults: undefined;
  DepartmentConsults: undefined;
  HODDashboard: undefined;
  Profile: undefined;
};

const Tab = createBottomTabNavigator<MainTabsParamList>();

export const MainTabs = () => {
  return (
    <Tab.Navigator>
      <Tab.Screen name="MyConsults" component={MyConsultsScreen} options={{ title: 'My Consults' }} />
      <Tab.Screen name="DepartmentConsults" component={DepartmentConsultsScreen} options={{ title: 'Department' }} />
      <Tab.Screen name="HODDashboard" component={HODDashboardScreen} options={{ title: 'HOD' }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: 'Profile' }} />
    </Tab.Navigator>
  );
};