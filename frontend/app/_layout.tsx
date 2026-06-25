import { Stack } from 'expo-router';
import { ThemeProvider } from 'expo-router/react-navigation';
import { View } from 'react-native';
import 'react-native-reanimated';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { colors } from '@/theme/colors';
import { navigationTheme } from '@/theme/navigation';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/query-client';
import Header from '@/components/layout/Header';

export { ErrorBoundary } from 'expo-router';

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider value={navigationTheme}>
        <SafeAreaProvider>
          <View style={{ flex: 1, backgroundColor: colors.background }}>
            <Stack
              screenOptions={{
                headerShown: true,
                header: () => <Header />,
                contentStyle: { backgroundColor: colors.background, padding: 0 },
              }}
            >
              <Stack.Screen name="index" options={{ title: 'Home' }} />
              <Stack.Screen name="classes/[race_id]" options={{ title: 'Race Classes' }} />
              <Stack.Screen
                name="classes/[race_id]/[class_id]"
                options={{ title: 'Race Classes' }}
              />
              <Stack.Screen
                name="classes/[race_id]/[class_id]/[spec_id]"
                options={{ title: 'Race Classes' }}
              />
            </Stack>
          </View>
        </SafeAreaProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
