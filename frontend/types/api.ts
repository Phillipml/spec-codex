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
interface Skill {
  id: number;
  name: string;
  image: string;
  description: string;
  cast_time: string;
  range?: string;
  cooldown?: string;
}
interface SpecDetailed {
  id: string | number;
  name: string;
  image: string;
  description: string;
  type: string;
  skills: Skill[];
}

interface SpecSkills extends ClassOrSpec {
  specialization: SpecDetailed[];
}

export interface RaceClasses extends Race {
  playable_classes: ClassOrSpec[];
}
export interface SpecList extends Race {
  class: ClassOrSpec;
}
export interface SkillsList extends Race {
  class: SpecSkills;
}
