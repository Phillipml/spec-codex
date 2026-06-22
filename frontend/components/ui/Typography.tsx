import { ColorName, colorReturn } from '@/theme/colors';
import { sizes, SizesType } from '@/theme/fontSizes';
import { Text, TextProps } from 'react-native';

type Props = TextProps & {
  size?: SizesType;
  color?: ColorName;
};
export function Typography({ size = 'md', color = 'primary', style, ...props }: Props) {
  return <Text style={[{ fontSize: sizes[size], color: colorReturn(color) }, style]} {...props} />;
}

export default Typography;
