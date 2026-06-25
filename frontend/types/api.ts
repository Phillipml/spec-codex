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
interface Skill extends ClassOrSpec {
  description: string;
  cast_time: string;
  power_cost: string;
  range?: string;
  cooldown?: string;
}

export interface RaceClasses extends Race {
  playable_classes: ClassOrSpec[];
}
export interface SpecList extends Race {
  class: ClassSpecs;
}
interface SpecDetailed extends ClassOrSpec {
  description: string;
  type: 'Tanque' | 'Cura' | 'Dano';
  skills: Skill[];
}
interface ClassSpec extends ClassOrSpec {
  specialization: SpecDetailed;
}
export interface SkillsList extends Race {
  class: ClassSpec;
}
