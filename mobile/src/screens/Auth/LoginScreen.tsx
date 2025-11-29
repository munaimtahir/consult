import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../hooks/useAuth';
import { colors } from '../../theme/colors';
import { spacing, borderRadius, layout } from '../../theme/spacing';
import { textStyles } from '../../theme/typography';
import { Loading } from '../../components/Loading';

export const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, error, clearError } = useAuth();

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Error', 'Please enter both email and password');
      return;
    }

    setIsSubmitting(true);
    clearError();

    try {
      await login(email.trim(), password);
      // Navigation is handled automatically by RootNavigator
    } catch (err) {
      // Error is already set in the auth hook
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please check your credentials.';
      Alert.alert('Login Failed', errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Logo/Header */}
          <View style={styles.header}>
            <Text style={styles.logoEmoji}>🏥</Text>
            <Text style={styles.title}>Consult System</Text>
            <Text style={styles.subtitle}>Hospital Consultation Management</Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Email</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter your email"
                placeholderTextColor={colors.textTertiary}
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                keyboardType="email-address"
                autoCorrect={false}
                editable={!isSubmitting}
              />
            </View>

            <View style={styles.inputContainer}>
              <Text style={styles.label}>Password</Text>
              <TextInput
                style={styles.input}
                placeholder="Enter your password"
                placeholderTextColor={colors.textTertiary}
                secureTextEntry
                value={password}
                onChangeText={setPassword}
                editable={!isSubmitting}
              />
            </View>

            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            <TouchableOpacity
              style={[styles.loginButton, isSubmitting && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={isSubmitting}
              activeOpacity={0.8}
            >
              {isSubmitting ? (
                <Loading size="small" message="" style={styles.buttonLoading} />
              ) : (
                <Text style={styles.loginButtonText}>Login</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              Having trouble logging in?
            </Text>
            <Text style={styles.footerHint}>
              Contact IT support for assistance
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  } as ViewStyle,
  keyboardView: {
    flex: 1,
  } as ViewStyle,
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: layout.screenPadding,
  } as ViewStyle,
  header: {
    alignItems: 'center',
    marginBottom: spacing.xxxxl,
  } as ViewStyle,
  logoEmoji: {
    fontSize: 64,
    marginBottom: spacing.lg,
  } as TextStyle,
  title: {
    ...textStyles.h1,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  } as TextStyle,
  subtitle: {
    ...textStyles.body,
    color: colors.textSecondary,
    textAlign: 'center',
  } as TextStyle,
  form: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.xxl,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  } as ViewStyle,
  inputContainer: {
    marginBottom: spacing.lg,
  } as ViewStyle,
  label: {
    ...textStyles.label,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  } as TextStyle,
  input: {
    ...textStyles.body,
    backgroundColor: colors.gray100,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    height: layout.inputHeight,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textPrimary,
  } as TextStyle,
  errorContainer: {
    backgroundColor: colors.errorLight,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.lg,
  } as ViewStyle,
  errorText: {
    ...textStyles.bodySmall,
    color: colors.errorDark,
    textAlign: 'center',
  } as TextStyle,
  loginButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    height: layout.buttonHeightLg,
    alignItems: 'center',
    justifyContent: 'center',
  } as ViewStyle,
  loginButtonDisabled: {
    backgroundColor: colors.gray400,
  } as ViewStyle,
  loginButtonText: {
    ...textStyles.button,
    color: colors.white,
    fontSize: 18,
  } as TextStyle,
  buttonLoading: {
    padding: 0,
  } as ViewStyle,
  footer: {
    alignItems: 'center',
    marginTop: spacing.xxxl,
  } as ViewStyle,
  footerText: {
    ...textStyles.bodySmall,
    color: colors.textSecondary,
  } as TextStyle,
  footerHint: {
    ...textStyles.caption,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  } as TextStyle,
});