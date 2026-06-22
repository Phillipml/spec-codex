import { Races } from '@/types/mockup';
import Typography from '../ui/Typography';
import { colors } from '@/theme/colors';
import { FlatList, View, StyleSheet } from 'react-native';
export default function RaceList() {
  return (
    <View style={{ paddingHorizontal: 16 }}>
      <View style={styles.facction}>
        <Typography size="lg" color="alliance">
          Aliança
        </Typography>
        <Typography size="sm" color="secondary">
          Pela Aliança!
        </Typography>
      </View>
      <View>
        <FlatList
          data={Races}
          keyExtractor={(item) => item.name}
          numColumns={2}
          scrollEnabled={false}
          columnWrapperStyle={{
            gap: 18,
          }}
          contentContainerStyle={{
            gap: 18,
          }}
          renderItem={({ item }) => (
            <View
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
            </View>
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
    borderLeftColor: colors.horde,
  },
  raceItem: {
    flex: 1,
    padding: 8,
    backgroundColor: colors.gray,
    borderWidth: 1,
    borderColor: colors.gold,
  },
});
