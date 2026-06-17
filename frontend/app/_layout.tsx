import { Stack } from 'expo-router';
import { View } from 'react-native';
import 'react-native-reanimated';
import { SafeAreaProvider } from 'react-native-safe-area-context';

const APP_BG = '#000'; // sua cor

export { ErrorBoundary } from 'expo-router';

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <View style={{ flex: 1, backgroundColor: APP_BG }}>
        <Stack
          screenOptions={{
            contentStyle: { backgroundColor: APP_BG },
            headerStyle: { backgroundColor: APP_BG },
            headerTintColor: '#fff',
          }}
        >
          <Stack.Screen name="index" options={{ title: 'Home' }} />
        </Stack>
      </View>
    </SafeAreaProvider>
  );
}