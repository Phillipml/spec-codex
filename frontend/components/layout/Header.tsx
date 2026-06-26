import { colors } from '@/theme/colors';
import { StyleSheet, TouchableOpacity } from 'react-native';
import Typography from '../ui/Typography';
import Logo from '@/assets/images/logo.svg';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import BackButton from '../ui/BackButton';

export default function Header() {
  const router = useRouter();
  return (
    <SafeAreaView edges={['top']} style={styles.header}>
      <BackButton />
      <TouchableOpacity style={styles.logo} onPress={() => router.push({ pathname: '/' })}>
        <Logo width={80} height={80} />
        <Typography size="lg" color="gold">
          Spec-Codex
        </Typography>
      </TouchableOpacity>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  header: {
    position: 'fixed',
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 12,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: colors.gold,
  },
  logo: {
    flexDirection: 'row',
    width: '75%',
    alignItems: 'center',
  },
});
