import { Typography } from '../ui/Typography';
import { colors } from '@/theme/colors';
import { FlatList, View, StyleSheet, TouchableOpacity } from 'react-native';
import { Race } from '@/types/api';
import { useRouter } from 'expo-router';

type RaceListType = {
  data: Race[];
  faction: 'alliance' | 'horde';
};
export default function RaceList({ data, faction }: RaceListType) {
  const router = useRouter();
  const factionMap = { alliance: 'Aliança', horde: 'Horda' } as const;
  const raceByFaction = data.filter((item) => item.faction === factionMap[faction]);
  return (
    <View style={[{ paddingHorizontal: 16 }, faction === 'horde' ? { paddingTop: 12 } : null]}>
      <View
        style={[
          styles.facction,
          faction === 'alliance'
            ? {
                borderLeftColor: colors.alliance,
                borderBottomWidth: 2,
                borderBottomColor: colors.alliance,
              }
            : { borderLeftColor: colors.horde, borderTopWidth: 2, borderTopColor: colors.horde },
        ]}
      >
        <Typography size="lg" color={faction}>
          {faction === 'alliance' ? 'Aliança' : 'Horda'}
        </Typography>
        <Typography size="md" color="secondary">
          {faction === 'alliance' ? 'Pela Aliança!' : 'Pela Horda!'}
        </Typography>
      </View>
      <View>
        <FlatList
          data={raceByFaction}
          keyExtractor={(item) => item.name}
          numColumns={3}
          scrollEnabled={false}
          columnWrapperStyle={{
            gap: 18,
          }}
          contentContainerStyle={{
            gap: 18,
          }}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() =>
                router.push({ pathname: '/classes/[race_id]', params: { race_id: item.id } })
              }
              style={{
                flex: 1,
                height: 90,
                padding: 8,
                backgroundColor: colors.gray,
                borderWidth: 1,
                borderColor: colors.gold,
                justifyContent: 'center',
                alignItems: 'center',
                borderRadius: 10,
              }}
            >
              <Typography style={{ textAlign: 'center' }}>{item.name}</Typography>
            </TouchableOpacity>
          )}
        />
      </View>
    </View>
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
  },
  raceItem: {
    flex: 1,
    padding: 8,
    backgroundColor: colors.gray,
    borderWidth: 1,
    borderColor: colors.gold,
  },
});
