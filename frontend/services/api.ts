import { Race, RaceClasses, SpecList } from '@/types/api';

export async function fetchRaces(): Promise<Race[]> {
  const res = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/playable-race/index?format=json`);
  if (!res.ok) {
    throw new Error('Failed to fetch races');
  }
  return res.json();
}
export async function fetchRaceClasses(race_id: number | string): Promise<RaceClasses> {
  const res = await fetch(
    `${process.env.EXPO_PUBLIC_API_URL}/playable-race/${race_id}/playable-classes?format=json`,
  );
  if (!res.ok) {
    throw new Error('Failed to fetch race classes');
  }
  return res.json();
}
export async function fetchClassSpecs(race_id: string, class_id: string): Promise<SpecList> {
  const res = await fetch(
    `${process.env.EXPO_PUBLIC_API_URL}/playable-race/${race_id}/playable-classes/${class_id}/specs/?format=json`,
  );
  if (!res) {
    throw new Error('Failed to fetch class specs');
  }
  return res.json();
}
