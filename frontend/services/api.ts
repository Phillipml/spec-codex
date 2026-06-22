
export async function fetchRaces(){
    const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/playable-race/index?format=json`);
    if (!response.ok) {
        throw new Error('Failed to fetch races');
    }
    return response.json();
}