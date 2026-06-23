export interface Race {
  id: string | number;
  name: string;
  faction: 'Aliança' | 'Horda';
}
interface Class {
  class_id: string | number;
  name: string;
  image: string;
}
export interface RaceClasses extends Race {
  playable_classes: Class[];
}
