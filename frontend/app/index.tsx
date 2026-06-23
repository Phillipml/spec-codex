import { colors } from '@/theme/colors';
import { StyleSheet, View, ScrollView, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Logo from '@/assets/images/logo.svg';
import { Typography } from '@/components/ui/Typography';
import RaceList from '@/components/layout/RaceList';
import { useRaces } from '@/hooks/useRaces';
import Loading from '@/components/ui/Loading';

export default function HomeScreen() {
  const { data, isLoading, error } = useRaces();
  if (isLoading) {
    return <Loading />;
  }
  if (error) {
    return <View>Error: {error.message}</View>;
  }
  return (
    <SafeAreaView>
      <View style={styles.header}>
        <Logo width={80} height={80} />
        <Typography size="lg" color="gold">
          Spec-Codex
        </Typography>
      </View>
      <ScrollView>
        <View style={{ paddingBottom: 150 }}>
          <RaceList data={data || []} faction="alliance" />
          <RaceList data={data || []} faction="horde" />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  header: {
    position: 'sticky',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.gold,
  },
});
