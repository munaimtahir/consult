import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { AuthStack } from './AuthStack';
import { MainTabs } from './MainTabs';
import { ConsultDetailScreen } from '../screens/Consults/ConsultDetailScreen';
import { AddNoteScreen } from '../screens/Consults/AddNoteScreen';
import { RootStackParamList } from './types';
import { useAuth } from '../hooks/useAuth';
import { Loading } from '../components/Loading';
import { colors } from '../theme/colors';

const Stack = createNativeStackNavigator<RootStackParamList>();

export const RootNavigator = () => {
  const { isLoading, isAuthenticated } = useAuth();

  // Show loading screen while checking auth status
  if (isLoading) {
    return <Loading fullScreen message="Loading..." />;
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      {isAuthenticated ? (
        <>
          <Stack.Screen name="Main" component={MainTabs} />
          <Stack.Screen
            name="ConsultDetail"
            component={ConsultDetailScreen}
            options={{
              headerShown: true,
              title: 'Consult Details',
              headerStyle: { backgroundColor: colors.surface },
              headerTintColor: colors.primary,
            }}
          />
          <Stack.Screen
            name="AddNote"
            component={AddNoteScreen}
            options={{
              headerShown: true,
              title: 'Add Note',
              presentation: 'modal',
              headerStyle: { backgroundColor: colors.surface },
              headerTintColor: colors.primary,
            }}
          />
        </>
      ) : (
        <Stack.Screen name="Auth" component={AuthStack} />
      )}
    </Stack.Navigator>
  );
};