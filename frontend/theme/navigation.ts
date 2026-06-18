import { DarkTheme, Theme } from 'expo-router/react-navigation'
import { colors } from './colors'

export const navigationTheme: Theme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: colors.gold,
    background: colors.background,
    card: colors.gray,
    text: colors.text,
    border: colors.gray,
    notification: colors.gold,
  },
}
