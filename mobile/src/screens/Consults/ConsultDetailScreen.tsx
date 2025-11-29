import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const ConsultDetailScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>ConsultDetailScreen (placeholder)</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  text: { fontSize: 18 },
});