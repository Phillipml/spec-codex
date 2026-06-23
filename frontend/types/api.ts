export interface Race {
  id: string | number;
  name: string;
  faction: 'Aliança' | 'Horda';
}
interface ClassOrSpec {
  id: string | number;
  name: string;
  image: string;
}
interface ClassSpecs extends ClassOrSpec {
  specializations: ClassOrSpec[];
}

export interface RaceClasses extends Race {
  playable_classes: ClassOrSpec[];
}
export interface SpecList extends Race {
  class: ClassSpecs;
}
