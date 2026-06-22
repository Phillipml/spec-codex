import { useQuery } from '@tanstack/react-query';
import { fetchRaces } from '../services/api';
import { Race } from '../types/api';

export function useRaces() {
  return useQuery<Race[]>({
    queryKey: ['races'],
    queryFn: () => fetchRaces(),
  });
}
