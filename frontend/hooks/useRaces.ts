import { useQuery } from '@tanstack/react-query';
import { fetchClassSpecs, fetchRaceClasses, fetchRaces } from '../services/api';
import { Race, RaceClasses, SpecList } from '../types/api';

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
export function useClassSpecs(race_id: string, class_id: string) {
  return useQuery<SpecList>({
    queryKey: ['classSpecs', race_id, class_id],
    queryFn: () => fetchClassSpecs(race_id, class_id),
    enabled: !!race_id && !!class_id,
  });
}
