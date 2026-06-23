import Header from '@/components/layout/Header';
import Typography from '@/components/ui/Typography';
import { useClassSpecs } from '@/hooks/useRaces';
import { useLocalSearchParams } from 'expo-router';
import { Image, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function ClassSpecs() {
  const { race_id, class_id } = useLocalSearchParams<{ race_id: string; class_id: string }>();
  const { data, isLoading, error } = useClassSpecs(race_id, class_id);
  return (
    <SafeAreaView>
      <Header style={{ alignItems: 'center' }}>
        <View style={{ flexDirection: 'row', gap: 8 }}>
          <Typography color="gold" size="lg">
            {data?.name}
          </Typography>
          <Image src={data?.class.image} width={32} height={32} style={{ marginLeft: 8 }} />
        </View>
      </Header>
    </SafeAreaView>
  );
}
