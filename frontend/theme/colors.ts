export const colors = {
  primary: '#E5E2E1',
  secondary: '#D1C6AB',
  gold: '#EDC200',
  gray: '#2A2A2A',
  background: '#1C1B1B',
  horde: '#8C1616',
  alliance: '#004A94',
} as const;

export type ColorName = keyof typeof colors;

export function colorReturn(color: ColorName): string {
  return colors[color] ?? colors.primary;
}
