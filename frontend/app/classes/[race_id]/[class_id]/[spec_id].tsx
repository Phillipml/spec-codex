import Loading from '@/components/ui/Loading';
import Typography from '@/components/ui/Typography';
import { useSpecSkills } from '@/hooks/useRaces';
import { useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function SkillsList() {
  const { race_id, class_id, spec_id } = useLocalSearchParams<{
    race_id: string;
    class_id: string;
    spec_id: string;
  }>();
  const { data, isLoading, error } = useSpecSkills(race_id, class_id, spec_id);
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
    <SafeAreaView>
      <Typography size="xl">{data?.class.name}</Typography>
    </SafeAreaView>
  );
}
