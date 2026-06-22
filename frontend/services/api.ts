import { Race } from '@/types/api';

export async function fetchRaces(): Promise<Race[]> {
  const response = await fetch(
    `${process.env.EXPO_PUBLIC_API_URL}/playable-race/index?format=json`,
  );
  if (!response.ok) {
    throw new Error('Failed to fetch races');
  }
  return response.json();
}
