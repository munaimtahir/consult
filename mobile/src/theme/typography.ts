/**
 * Typography styles for the Consult mobile app.
 */

import { TextStyle, Platform } from 'react-native';

/**
 * Font family definitions.
 */
export const fontFamily = {
  regular: Platform.select({
    ios: 'System',
    android: 'Roboto',
    default: 'System',
  }),
  medium: Platform.select({
    ios: 'System',
    android: 'Roboto-Medium',
    default: 'System',
  }),
  bold: Platform.select({
    ios: 'System',
    android: 'Roboto-Bold',
    default: 'System',
  }),
};

/**
 * Font sizes.
 */
export const fontSize = {
  /** 10px - Caption small */
  xxs: 10,
  
  /** 12px - Caption */
  xs: 12,
  
  /** 14px - Body small */
  sm: 14,
  
  /** 16px - Body */
  md: 16,
  
  /** 18px - Body large */
  lg: 18,
  
  /** 20px - Heading small */
  xl: 20,
  
  /** 24px - Heading medium */
  xxl: 24,
  
  /** 28px - Heading large */
  xxxl: 28,
  
  /** 32px - Display small */
  xxxxl: 32,
  
  /** 36px - Display medium */
  xxxxxl: 36,
};

/**
 * Font weights.
 */
export const fontWeight = {
  regular: '400' as TextStyle['fontWeight'],
  medium: '500' as TextStyle['fontWeight'],
  semibold: '600' as TextStyle['fontWeight'],
  bold: '700' as TextStyle['fontWeight'],
};

/**
 * Line height multipliers.
 */
export const lineHeight = {
  tight: 1.2,
  normal: 1.4,
  relaxed: 1.6,
  loose: 1.8,
};

/**
 * Pre-defined text styles.
 */
export const textStyles = {
  // Display
  displayLarge: {
    fontSize: fontSize.xxxxxl,
    fontWeight: fontWeight.bold,
    lineHeight: fontSize.xxxxxl * lineHeight.tight,
  } as TextStyle,
  
  displayMedium: {
    fontSize: fontSize.xxxxl,
    fontWeight: fontWeight.bold,
    lineHeight: fontSize.xxxxl * lineHeight.tight,
  } as TextStyle,
  
  // Headings
  h1: {
    fontSize: fontSize.xxxl,
    fontWeight: fontWeight.bold,
    lineHeight: fontSize.xxxl * lineHeight.tight,
  } as TextStyle,
  
  h2: {
    fontSize: fontSize.xxl,
    fontWeight: fontWeight.bold,
    lineHeight: fontSize.xxl * lineHeight.tight,
  } as TextStyle,
  
  h3: {
    fontSize: fontSize.xl,
    fontWeight: fontWeight.semibold,
    lineHeight: fontSize.xl * lineHeight.normal,
  } as TextStyle,
  
  h4: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.semibold,
    lineHeight: fontSize.lg * lineHeight.normal,
  } as TextStyle,
  
  // Body
  bodyLarge: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.regular,
    lineHeight: fontSize.lg * lineHeight.normal,
  } as TextStyle,
  
  body: {
    fontSize: fontSize.md,
    fontWeight: fontWeight.regular,
    lineHeight: fontSize.md * lineHeight.normal,
  } as TextStyle,
  
  bodySmall: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.regular,
    lineHeight: fontSize.sm * lineHeight.normal,
  } as TextStyle,
  
  // Labels
  label: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: fontSize.sm * lineHeight.normal,
  } as TextStyle,
  
  labelSmall: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.medium,
    lineHeight: fontSize.xs * lineHeight.normal,
  } as TextStyle,
  
  // Caption
  caption: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.regular,
    lineHeight: fontSize.xs * lineHeight.normal,
  } as TextStyle,
  
  captionSmall: {
    fontSize: fontSize.xxs,
    fontWeight: fontWeight.regular,
    lineHeight: fontSize.xxs * lineHeight.normal,
  } as TextStyle,
  
  // Button
  button: {
    fontSize: fontSize.md,
    fontWeight: fontWeight.medium,
    lineHeight: fontSize.md * lineHeight.normal,
  } as TextStyle,
  
  buttonSmall: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
    lineHeight: fontSize.sm * lineHeight.normal,
  } as TextStyle,
};
