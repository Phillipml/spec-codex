import Typography from '@/components/ui/Typography';
import { useRaceClasses } from '@/hooks/useRaces';
import { useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function RaceClasses() {
  const { race_id } = useLocalSearchParams<{ race_id: string }>();
  const { data, isLoading, error } = useRaceClasses(Number(race_id));
  return (
    <SafeAreaView>
      <Typography>{data?.name}</Typography>
    </SafeAreaView>
  );
}
