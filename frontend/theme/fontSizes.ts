export const sizes = {
  sm: '0.625rem',
  md: '0.875rem',
  lg: '1.125rem',
  xl: '2.25rem',
} as const;

export type SizesType = keyof typeof sizes;

export function sizeReturn(size: SizesType): string {
  return sizes[size] ?? sizes.md;
}
