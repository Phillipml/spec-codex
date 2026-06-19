import { colors } from '@/theme/colors';
import { StyleSheet, FlatList, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Logo from '@/assets/images/logo.svg';
import Typography from '@/components/ui/Typography';

const RACES = ['elfo', 'Orc', 'Dractyr', 'Anão', 'Noturno'];
export default function HomeScreen() {
  return (
    <SafeAreaView>
      <View style={styles.header}>
        <Logo width={80} height={80} />
        <Typography size="lg" color="gold">
          Spec-Codex
        </Typography>
      </View>
      <View style={{ paddingHorizontal: 16 }}>
        <View style={styles.facction}>
          <Typography size="lg" color="horde">
            Horda
          </Typography>
          <Typography size="sm" color="secondary">
            Pela Horda!
          </Typography>
        </View>
        <View>
          <FlatList
            data={RACES}
            keyExtractor={(item) => item}
            scrollEnabled={false}
            contentContainerStyle={{
              flexDirection: 'row',
              gap: 8,
              borderWidth: 1,
              flexWrap: 'nowrap',
            }}
            renderItem={({ item }) => (
              <View>
                <Typography
                  size="sm"
                  style={{
                    width: '50%',
                    padding: 8,
                    backgroundColor: colors.gray,
                    borderWidth: 1,
                    borderColor: colors.gold,
                  }}
                >
                  {item}
                </Typography>
              </View>
            )}
          />
        </View>
      </View>
    </SafeAreaView>
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
