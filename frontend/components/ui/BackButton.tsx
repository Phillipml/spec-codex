import { TouchableOpacity, StyleProp, ViewStyle } from 'react-native';
import Icon from '@/assets/images/backIcon.svg';
import { usePathname, useRouter } from 'expo-router';
import { colors } from '@/theme/colors';

interface BackIconProps {
  style?: StyleProp<ViewStyle>;
}

export default function BackButton({ style }: BackIconProps) {
  const router = useRouter();
  const pathname = usePathname();
  const isHome = pathname === '/';

  return (
    <TouchableOpacity
      onPress={() => router.back()}
      style={[
        {
          width: 40,
          height: 40,
          backgroundColor: colors.gold,
          justifyContent: 'center',
          alignItems: 'center',
          borderRadius: 50,
          opacity: isHome ? 0 : 1,
        },
        style,
      ]}
    >
      <Icon width={20} height={20} />
    </TouchableOpacity>
  );
}
