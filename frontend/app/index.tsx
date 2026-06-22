import { colors } from '@/theme/colors';
import { StyleSheet, View, ScrollView, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Logo from '@/assets/images/logo.svg';
import Typography from '@/components/ui/Typography';
import RaceList from '@/components/layout/RaceList';
import { useRaces } from '@/hooks/useRaces';

export default function HomeScreen() {
  const { data, isLoading, error } = useRaces();
  if (isLoading) {
    return <Text>Loading...</Text>;
  }
  if (error) {
    return <View>Error: {error.message}</View>;
  }
  return (
    <SafeAreaView>
      <ScrollView>
        <View style={styles.header}>
          <Logo width={80} height={80} />
          <Typography size="lg" color="gold">
            Spec-Codex
          </Typography>
        </View>
        <RaceList data={data || []} faction="alliance" />
        <RaceList data={data || []} faction="horde" />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.gold,
  },
  facction: {
    marginTop: 12,
    marginBottom: 32,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderLeftWidth: 1,
    borderLeftColor: colors.horde,
  },
  raceItem: {
    flex: 1,
    padding: 8,
    backgroundColor: colors.gray,
    borderWidth: 1,
    borderColor: colors.gold,
  },
});
