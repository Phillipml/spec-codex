import { useQuery } from '@tanstack/react-query';
import { fetchClassSpecs, fetchRaceClasses, fetchRaces, fetchSpecSkills } from '../services/api';
import { Race, RaceClasses, SkillsList, SpecList } from '../types/api';

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
export function useSpecSkills(race_id: string, class_id: string, spec_id: string) {
  return useQuery<SkillsList>({
    queryKey: ['skills', race_id, class_id, spec_id],
    queryFn: () => fetchSpecSkills(race_id, class_id, spec_id),
    enabled: !!race_id && !!class_id && !!spec_id,
  });
}
