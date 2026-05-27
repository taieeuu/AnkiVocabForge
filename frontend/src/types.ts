export type Mode = 'article' | 'vocab' | 'ai' | 'grammar';
export type WorkflowStage = 'input' | 'selection' | 'processing' | 'json_edit' | 'finished';
export type EditViewMode = 'json' | 'preview';
export type ConsoleHeight = 'min' | 'mid' | 'max';
export type LogType = 'info' | 'success' | 'error' | 'warning';

export interface Log {
  time: string;
  type: LogType;
  msg: string;
}

export interface Settings {
  apiKey: string;
  model: string;
  nativeLanguage: string;
  learningLanguage: string;
  audio: {
    enabled: boolean;
    voice: string;
  };
}

export interface ImageData {
  id: number;
  src: string;
  selected: boolean;
  isUserUploaded?: boolean;
}

export interface Card {
  id: number;
  front?: string;
  back?: string;
  sentence?: string;
  // Vocab card fields
  word?: string;
  pos?: string;
  synonyms?: string;
  audio?: string;
  // Grammar card fields
  grammar?: string;
  pattern?: string;
  usage?: string;
  contrast?: string;
  // Common fields
  meaning: string;
  ex1_ori: string;
  ex1_trans: string;
  ex2_ori: string;
  ex2_trans: string;
  hint: string;
  notes?: string;
  mnemonic?: string;
}
