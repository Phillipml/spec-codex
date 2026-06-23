import Typography from '@/components/ui/Typography';
import { useClassSpecs } from '@/hooks/useRaces';
import { useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function ClassSpecs() {
  const { race_id, class_id } = useLocalSearchParams<{ race_id: string; class_id: string }>();
  const { data, isLoading, error } = useClassSpecs(race_id, class_id);
  return (
    <SafeAreaView>
      <Typography>{data?.class.image}</Typography>
    </SafeAreaView>
  );
}
