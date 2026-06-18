import { colors } from '@/theme/colors';
import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Logo from '@/assets/images/logo.svg';

export default function HomeScreen() {
  return (
    <SafeAreaView>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
        <Logo width={80} height={80} />
        <Text style={styles.title}>Spec Codex</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    color: colors.gold,
    fontSize: 24,
    fontWeight: '600',
  },
});
