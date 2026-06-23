import { useQuery } from '@tanstack/react-query';
import { fetchRaceClasses, fetchRaces } from '../services/api';
import { Race, RaceClasses } from '../types/api';

export function useRaces() {
  return useQuery<Race[]>({
    queryKey: ['races'],
    queryFn: () => fetchRaces(),
  });
}

export function useRaceClasses(race_id: number) {
  return useQuery<RaceClasses>({
    queryKey: ['raceClasses', race_id],
    queryFn: () => fetchRaceClasses(race_id),
    enabled: !!race_id,
  });
}
