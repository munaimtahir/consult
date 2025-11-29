import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useConsultDetail } from '../../hooks/useConsults';
import { Loading } from '../../components/Loading';
import { colors } from '../../theme/colors';
import { spacing, borderRadius, layout } from '../../theme/spacing';
import { textStyles } from '../../theme/typography';
import { RootStackParamList } from '../../navigation/types';
import { NOTE_TYPES, NoteType } from '../../config/constants';

type RouteProps = RouteProp<RootStackParamList, 'AddNote'>;
type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

/**
 * Note type options.
 */
const NOTE_TYPE_OPTIONS: Array<{ key: NoteType; label: string }> = [
  { key: NOTE_TYPES.PROGRESS, label: 'Progress' },
  { key: NOTE_TYPES.RECOMMENDATION, label: 'Recommendation' },
  { key: NOTE_TYPES.ASSESSMENT, label: 'Assessment' },
  { key: NOTE_TYPES.PLAN, label: 'Plan' },
];

export const AddNoteScreen = () => {
  const route = useRoute<RouteProps>();
  const navigation = useNavigation<NavigationProp>();
  const { consultId } = route.params;

  const [content, setContent] = useState('');
  const [recommendations, setRecommendations] = useState('');
  const [noteType, setNoteType] = useState<NoteType>(NOTE_TYPES.PROGRESS);
  const [followUpRequired, setFollowUpRequired] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { addNote } = useConsultDetail(consultId);

  /**
   * Handle submit.
   */
  const handleSubmit = async () => {
    if (!content.trim()) {
      Alert.alert('Error', 'Please enter note content');
      return;
    }

    setIsSubmitting(true);

    try {
      await addNote({
        content: content.trim(),
        note_type: noteType,
        recommendations: recommendations.trim() || undefined,
        follow_up_required: followUpRequired,
      });

      Alert.alert('Success', 'Note added successfully', [
        {
          text: 'OK',
          onPress: () => navigation.goBack(),
        },
      ]);
    } catch (err) {
      Alert.alert('Error', 'Failed to add note. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Note Type Selector */}
        <View style={styles.section}>
          <Text style={styles.label}>Note Type</Text>
          <View style={styles.typeContainer}>
            {NOTE_TYPE_OPTIONS.map((option) => (
              <TouchableOpacity
                key={option.key}
                style={[
                  styles.typeButton,
                  noteType === option.key && styles.typeButtonSelected,
                ]}
                onPress={() => setNoteType(option.key)}
              >
                <Text
                  style={[
                    styles.typeButtonText,
                    noteType === option.key && styles.typeButtonTextSelected,
                  ]}
                >
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Content Input */}
        <View style={styles.section}>
          <Text style={styles.label}>Note Content *</Text>
          <TextInput
            style={styles.textArea}
            placeholder="Enter your note..."
            placeholderTextColor={colors.textTertiary}
            value={content}
            onChangeText={setContent}
            multiline
            numberOfLines={6}
            textAlignVertical="top"
            editable={!isSubmitting}
          />
        </View>

        {/* Recommendations Input */}
        <View style={styles.section}>
          <Text style={styles.label}>Recommendations (Optional)</Text>
          <TextInput
            style={styles.textAreaSmall}
            placeholder="Enter recommendations..."
            placeholderTextColor={colors.textTertiary}
            value={recommendations}
            onChangeText={setRecommendations}
            multiline
            numberOfLines={3}
            textAlignVertical="top"
            editable={!isSubmitting}
          />
        </View>

        {/* Follow-up Toggle */}
        <TouchableOpacity
          style={styles.checkboxContainer}
          onPress={() => setFollowUpRequired(!followUpRequired)}
        >
          <View style={[styles.checkbox, followUpRequired && styles.checkboxChecked]}>
            {followUpRequired && <Text style={styles.checkmark}>✓</Text>}
          </View>
          <Text style={styles.checkboxLabel}>Follow-up required</Text>
        </TouchableOpacity>

        {/* Submit Button */}
        <TouchableOpacity
          style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <Loading size="small" message="" style={styles.buttonLoading} />
          ) : (
            <Text style={styles.submitButtonText}>Add Note</Text>
          )}
        </TouchableOpacity>

        {/* Cancel Button */}
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => navigation.goBack()}
          disabled={isSubmitting}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  } as ViewStyle,
  scrollContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xxxxl,
  } as ViewStyle,
  section: {
    marginBottom: spacing.lg,
  } as ViewStyle,
  label: {
    ...textStyles.label,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  } as TextStyle,
  typeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  } as ViewStyle,
  typeButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
    backgroundColor: colors.gray100,
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
  } as ViewStyle,
  typeButtonSelected: {
    backgroundColor: colors.primary,
  } as ViewStyle,
  typeButtonText: {
    ...textStyles.labelSmall,
    color: colors.textSecondary,
  } as TextStyle,
  typeButtonTextSelected: {
    color: colors.white,
  } as TextStyle,
  textArea: {
    ...textStyles.body,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    height: 150,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textPrimary,
  } as TextStyle,
  textAreaSmall: {
    ...textStyles.body,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    height: 80,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textPrimary,
  } as TextStyle,
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.xl,
  } as ViewStyle,
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: borderRadius.sm,
    borderWidth: 2,
    borderColor: colors.gray400,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  } as ViewStyle,
  checkboxChecked: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  } as ViewStyle,
  checkmark: {
    color: colors.white,
    fontSize: 14,
    fontWeight: 'bold',
  } as TextStyle,
  checkboxLabel: {
    ...textStyles.body,
    color: colors.textPrimary,
  } as TextStyle,
  submitButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    height: layout.buttonHeightLg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  } as ViewStyle,
  submitButtonDisabled: {
    backgroundColor: colors.gray400,
  } as ViewStyle,
  submitButtonText: {
    ...textStyles.button,
    color: colors.white,
    fontSize: 18,
  } as TextStyle,
  buttonLoading: {
    padding: 0,
  } as ViewStyle,
  cancelButton: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    height: layout.buttonHeightLg,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  } as ViewStyle,
  cancelButtonText: {
    ...textStyles.button,
    color: colors.textSecondary,
    fontSize: 18,
  } as TextStyle,
});