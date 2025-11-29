/**
 * Navigation type definitions.
 */

import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';

/**
 * Root stack parameter list.
 */
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Main: NavigatorScreenParams<MainTabsParamList>;
  ConsultDetail: { consultId: number };
  AddNote: { consultId: number };
};

/**
 * Auth stack parameter list.
 */
export type AuthStackParamList = {
  Login: undefined;
};

/**
 * Main tabs parameter list.
 */
export type MainTabsParamList = {
  MyConsults: undefined;
  DepartmentConsults: undefined;
  HODDashboard: undefined;
  Profile: undefined;
};

/**
 * Root stack screen props.
 */
export type RootStackScreenProps<T extends keyof RootStackParamList> =
  NativeStackScreenProps<RootStackParamList, T>;

/**
 * Auth stack screen props.
 */
export type AuthStackScreenProps<T extends keyof AuthStackParamList> =
  CompositeScreenProps<
    NativeStackScreenProps<AuthStackParamList, T>,
    RootStackScreenProps<keyof RootStackParamList>
  >;

/**
 * Main tabs screen props.
 */
export type MainTabsScreenProps<T extends keyof MainTabsParamList> =
  CompositeScreenProps<
    BottomTabScreenProps<MainTabsParamList, T>,
    RootStackScreenProps<keyof RootStackParamList>
  >;

/**
 * Global declaration to extend React Navigation types.
 */
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
