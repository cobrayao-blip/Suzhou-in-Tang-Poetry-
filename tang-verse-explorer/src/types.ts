export interface Poem {
  id: string;
  title: string;
  author: string;
  content: string;
  volume: number;
  metadata?: PoemMetadata;
}

export interface PoemMetadata {
  imagery: string[];
  places: Place[];
  relationships: Relationship[];
  suzhouElements: string[];
  summary: string;
  coordinates?: { lat: number; lng: number };
}

export interface Place {
  name: string;
  description: string;
  isSuzhouRelated: boolean;
  coordinates?: { lat: number; lng: number };
}

export interface Relationship {
  person: string;
  relation: string;
}

export interface SpatialHub {
  name: string;
  poemCount: number;
  imagery: string[];
  people: string[];
  relatedSpaces: string[];
  description: string;
}

export interface Relation {
  p1: string;
  p2: string;
  type: string;
  detail: string;
  intensity: number;
}

export interface ThemeConfig {
  name: string;
  bg: string;
  sidebar: string;
  card: string;
  text: string;
  accent: string;
  accentText: string;
  border: string;
  font: string;
}
