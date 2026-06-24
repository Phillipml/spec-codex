import Loading from '@/components/ui/Loading';
import Typography from '@/components/ui/Typography';
import { useSpecSkills } from '@/hooks/useRaces';
import { colors } from '@/theme/colors';
import { useLocalSearchParams } from 'expo-router';
import { Image, ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function SkillsList() {
  const { race_id, class_id, spec_id } = useLocalSearchParams<{
    race_id: string;
    class_id: string;
    spec_id: string;
  }>();
  const { data, isLoading, error } = useSpecSkills(race_id, class_id, spec_id);
  function typeSpecColor(): string {
    const SpecStyleMap = {
      Dano: colors.horde,
      Tanque: colors.alliance,
      Cura: colors.gold,
    };
    const color = SpecStyleMap[data?.class.specialization.type || 'Cura'];
    return color;
  }

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
      <View style={[styles.header, { borderColor: typeSpecColor() }]}>
        <Image
          src={data?.class.image}
          width={80}
          height={80}
          style={{ borderWidth: 2, borderRadius: 4, borderColor: typeSpecColor() }}
        />
        <View style={{ justifyContent: 'center' }}>
          <Typography color="gold" size="lg">
            {data?.name}
          </Typography>
          <Typography color="secondary" size="lg">
            {data?.class.name}
          </Typography>
        </View>
      </View>
      <ScrollView style={{ padding: 16 }}>
        <View
          style={[
            styles.specCard,
            {
              borderColor: typeSpecColor(),
            },
          ]}
        >
          <Image
            src={data?.class.specialization.image}
            width={62}
            height={62}
            style={{ borderWidth: 4, borderRadius: 50, borderColor: typeSpecColor() }}
          />
          <View style={{ flex: 1, flexShrink: 1 }}>
            <View
              style={{ flexDirection: 'row', justifyContent: 'space-between', paddingBottom: 16 }}
            >
              <Typography size="lg" color="gold">
                {data?.class.specialization.name}
              </Typography>
              <View
                style={{
                  flexDirection: 'row',
                  backgroundColor: typeSpecColor(),
                  borderRadius: 10,
                  padding: 4,
                }}
              >
                <Typography size="lg" color="background">
                  {data?.class.specialization.type}
                </Typography>
              </View>
            </View>

            <Typography color="secondary">{data?.class.specialization.description}</Typography>
          </View>
        </View>
        <View style={{ paddingBottom: 180 }}>
          <Typography color="gold" size="xl" style={{ textAlign: 'center', paddingTop: 16 }}>
            Skills
          </Typography>
          {data?.class.specialization.skills.map((item, index) => (
            <View
              key={item.id}
              style={[
                styles.skillWrapper,
                {
                  backgroundColor: index % 2 === 0 ? colors.gray : colors.background,
                },
              ]}
            >
              <View style={styles.skillHeader}>
                <Image src={item.image} width={32} height={32} style={{ borderRadius: 50 }} />
                <View>
                  <Typography size="lg">{item.name}</Typography>
                  <Typography size="sm" color="secondary">
                    {item.cast_time}
                  </Typography>
                </View>
              </View>
              <View style={styles.skillDetailed}>
                <Typography size="lg">Descrição:</Typography>
                <Typography size="sm">{item.description}</Typography>
              </View>
              <View
                style={[
                  styles.skillInfo,
                  {
                    borderTopWidth: item.cooldown || item.power_cost || item.range ? 1 : 0,
                  },
                ]}
              >
                {[
                  { label: 'Cooldown', value: item.cooldown },
                  { label: 'Custo de poder', value: item.power_cost },
                  { label: 'Range', value: item.range },
                ]
                  .filter(({ value }) => value)
                  .map(({ label, value }) => (
                    <View key={label} style={styles.skillInfoRow}>
                      <Typography style={{ color: colors.gold }}>{label}: </Typography>
                      <Typography size="sm">{value}</Typography>
                    </View>
                  ))}
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  header: {
    backgroundColor: colors.gray,
    flexDirection: 'row',
    gap: 16,
    padding: 16,
    borderBottomWidth: 2,
  },
  specCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    borderWidth: 2,
    borderRadius: 4,
  },
  skillWrapper: {
    padding: 8,
    marginBottom: 16,
    borderRadius: 4,
    borderBottomWidth: 2,
    borderColor: colors.gold,
  },
  skillHeader: {
    flexDirection: 'row',
    flex: 1,
    flexShrink: 1,
    gap: 8,
    paddingVertical: 4,
  },
  skillDetailed: { borderTopWidth: 1, borderColor: colors.gold, borderRadius: 4 },
  skillInfo: {
    marginTop: 4,
    borderColor: colors.secondary,
    borderRadius: 4,
  },
  skillInfoRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: 8,
  },
});
