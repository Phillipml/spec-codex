import { Stack } from 'expo-router';
import { ThemeProvider } from 'expo-router/react-navigation';
import { View } from 'react-native';
import 'react-native-reanimated';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { colors } from '@/theme/colors';
import { navigationTheme } from '@/theme/navigation';

export { ErrorBoundary } from 'expo-router';

export default function RootLayout() {
  return (
    <ThemeProvider value={navigationTheme}>
      <SafeAreaProvider>
        <View style={{ flex: 1, backgroundColor: colors.background }}>
          <Stack
            screenOptions={{
              headerShown: false,
              contentStyle: { backgroundColor: colors.background },
            }}
          >
            <Stack.Screen name="index" options={{ title: 'Home' }} />
          </Stack>
        </View>
      </SafeAreaProvider>
    </ThemeProvider>
  );
}
