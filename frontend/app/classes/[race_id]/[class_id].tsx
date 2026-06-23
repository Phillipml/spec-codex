import Header from '@/components/layout/Header';
import Loading from '@/components/ui/Loading';
import Typography from '@/components/ui/Typography';
import { useClassSpecs } from '@/hooks/useRaces';
import { colors } from '@/theme/colors';
import { useLocalSearchParams } from 'expo-router';
import { Image, StyleSheet, View, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function ClassSpecs() {
  const { race_id, class_id } = useLocalSearchParams<{ race_id: string; class_id: string }>();
  const { data, isLoading, error } = useClassSpecs(race_id, class_id);
  if (isLoading) {
    return <Loading />;
  }
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
      <ScrollView style={{ paddingHorizontal: 16 }}>
        <View style={{ marginVertical: 32, gap: 8 }}>
          <Typography size="lg">Escolha sua especialização</Typography>
          <Typography color="secondary">
            Domine a arte de um {data?.class.name} escolhendo o melhor caminho
          </Typography>
        </View>
        <View style={{ paddingBottom: 100 }}>
          {data?.class.specializations.map((item) => (
            <View style={styles.card}>
              <Image src={item.image} width={52} height={52} />
              <Typography size="xl" color="secondary" style={{ width: '70%', textAlign: 'center' }}>
                {item.name}
              </Typography>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-evenly',
    marginVertical: 16,
    height: 120,
    padding: 8,
    backgroundColor: colors.gray,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: colors.secondary,
  },
});
