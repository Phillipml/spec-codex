import { colors } from '@/theme/colors';
import { StyleSheet } from 'react-native';
import { View } from 'react-native';
import { ViewProps } from 'react-native/Libraries/Components/View/ViewPropTypes';

type HeaderProps = ViewProps;
export default function Header({ style, ...props }: HeaderProps) {
  return <View style={[styles.nameHeader, style]} {...props} />;
}
const styles = StyleSheet.create({
  nameHeader: {
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderColor: colors.secondary,
    backgroundColor: colors.gray,
  },
});
