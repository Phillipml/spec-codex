import { View, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
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
    return (
      <SafeAreaView>
        <Typography>{error.message}</Typography>
      </SafeAreaView>
    );
  }
  return (
    <View>
      <ScrollView contentContainerStyle={{ paddingBottom: 250 }}>
        <View>
          <RaceList data={data || []} faction="alliance" />
          <RaceList data={data || []} faction="horde" />
        </View>
      </ScrollView>
    </View>
  );
}
