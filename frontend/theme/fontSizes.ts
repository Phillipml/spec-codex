export const sizes = {
  sm: 10,
  md: 14,
  lg: 18,
  xl: 36,
} as const;

export type SizesType = keyof typeof sizes;
