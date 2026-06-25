import { colors } from '@/theme/colors';
import { StyleSheet } from 'react-native';
import Typography from '../ui/Typography';
import Logo from '@/assets/images/logo.svg';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function Header() {
  return (
    <SafeAreaView edges={['top']} style={styles.header}>
      <Logo width={80} height={80} />
      <Typography size="lg" color="gold">
        Spec-Codex
      </Typography>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  header: {
    position: 'fixed',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.gold,
  },
});
