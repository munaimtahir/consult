/**
 * Spacing scale for the Consult mobile app.
 * Uses an 8-point grid system.
 */

export const spacing = {
  /** 0px */
  none: 0,
  
  /** 2px - Extra extra small */
  xxs: 2,
  
  /** 4px - Extra small */
  xs: 4,
  
  /** 8px - Small */
  sm: 8,
  
  /** 12px - Medium small */
  md: 12,
  
  /** 16px - Medium */
  lg: 16,
  
  /** 20px - Medium large */
  xl: 20,
  
  /** 24px - Large */
  xxl: 24,
  
  /** 32px - Extra large */
  xxxl: 32,
  
  /** 40px - 2x Extra large */
  xxxxl: 40,
  
  /** 48px - 3x Extra large */
  xxxxxl: 48,
};

/**
 * Border radius values.
 */
export const borderRadius = {
  /** 0px - No radius */
  none: 0,
  
  /** 4px - Small */
  sm: 4,
  
  /** 8px - Medium */
  md: 8,
  
  /** 12px - Large */
  lg: 12,
  
  /** 16px - Extra large */
  xl: 16,
  
  /** 24px - 2x Extra large */
  xxl: 24,
  
  /** 9999px - Full (circle/pill) */
  full: 9999,
};

/**
 * Common layout dimensions.
 */
export const layout = {
  /** Screen horizontal padding */
  screenPadding: spacing.lg,
  
  /** Card padding */
  cardPadding: spacing.lg,
  
  /** List item padding */
  listItemPadding: spacing.md,
  
  /** Button height (small) */
  buttonHeightSm: 36,
  
  /** Button height (medium) */
  buttonHeightMd: 44,
  
  /** Button height (large) */
  buttonHeightLg: 52,
  
  /** Input height */
  inputHeight: 48,
  
  /** Header height */
  headerHeight: 56,
  
  /** Tab bar height */
  tabBarHeight: 56,
  
  /** Bottom safe area minimum */
  bottomSafeArea: 20,
};
