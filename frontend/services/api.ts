import { Race } from '@/types/api';

export async function fetchRaces(): Promise<Race[]> {
  const res = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/playable-race/index?format=json`);
  if (!res.ok) {
    throw new Error('Failed to fetch races');
  }
  return res.json();
}
export async function fetchRaceClasses() {
  const res = await fetch(
    `${process.env.EXPO_PUBLIC_API_URL}/playable-race/10/playable-classes?format=json`,
  );
  if (!res.ok) {
    throw new Error('Filed to fetch race classes');
  }
  res.json();
}
