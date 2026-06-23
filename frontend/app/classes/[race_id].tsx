import Typography from '@/components/ui/Typography';
import { useRaceClasses } from '@/hooks/useRaces';
import { colors } from '@/theme/colors';
import { useLocalSearchParams } from 'expo-router';
import { Image, ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function RaceClasses() {
  const { race_id } = useLocalSearchParams<{ race_id: string }>();
  const { data, isLoading, error } = useRaceClasses(Number(race_id));
  const factionImage = {
    Horda: require('@/assets/images/horde.png'),
    Aliança: require('@/assets/images/alliance.png'),
  };
  if (isLoading) {
    return <Typography>Carregando..</Typography>;
  }
  if (error) {
    return (
      <View>
        <Typography>{error.message}</Typography>
      </View>
    );
  }
  return (
    <SafeAreaView>
      <View style={styles.nameHeader}>
        <Typography color="gold" size="lg" style={{ textAlign: 'center' }}>
          {data?.name}
        </Typography>
      </View>
      <ScrollView style={{ paddingHorizontal: 16 }}>
        <Image source={factionImage[data?.faction || 'Aliança']} style={styles.classImg} />
        <Typography size="lg" color="secondary" style={{ paddingVertical: 16 }}>
          Escolha seu caminho
        </Typography>
        <View style={styles.classList}>
          {data?.playable_classes.map((item) => (
            <View key={item.class_id} style={styles.specItem}>
              <Image
                src={item.image}
                width={56}
                height={56}
                style={{ borderWidth: 1, borderColor: colors.gold, borderRadius: 4 }}
              />
              <Typography style={{ marginTop: 8, color: colors.secondary }}>{item.name}</Typography>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  nameHeader: {
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderColor: colors.secondary,
    backgroundColor: colors.gray,
  },
  classList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 16,
    paddingBottom: 120,
  },
  specItem: {
    width: '44%',
    height: 120,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: colors.gold,
    padding: 8,
    backgroundColor: colors.gray,
  },
  classImg: {
    width: '100%',
    height: 250,
    borderWidth: 1,
    borderRadius: 15,
    borderColor: colors.secondary,
    marginTop: 16,
  },
});
