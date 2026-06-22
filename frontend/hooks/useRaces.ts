import { useQuery } from "@tanstack/react-query";
import { fetchRaces } from "../services/api";

export function useRaces(){
    return useQuery({
        queryKey:['races'],
        queryFn: () => fetchRaces(),
    })
}