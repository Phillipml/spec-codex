export interface Race {
  id: number;
  name: string;
  faction: 'Aliança' | 'Horda';
}
interface Class {
  class_id: number;
  name: string;
  image: string;
}
export interface RaceClasses extends Race {
  playable_classes: Class[];
}
