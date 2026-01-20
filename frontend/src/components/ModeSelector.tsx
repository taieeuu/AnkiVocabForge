import React from 'react';
import { FileText, BookOpen, Bot, LibrarySquare } from 'lucide-react';
import type { Mode } from '../types';

interface ModeSelectorProps {
  activeMode: Mode;
  setMode: (mode: Mode) => void;
  disabled: boolean;
}

export const ModeSelector: React.FC<ModeSelectorProps> = ({ activeMode, setMode, disabled }) => {
  const modes = [
    { id: 'article', label: 'Article', icon: FileText, sub: 'PDF/圖片 解析 + 單字' },
    { id: 'vocab', label: 'Vocab', icon: BookOpen, sub: '純單字列表' },
    { id: 'ai', label: 'AI Gen', icon: Bot, sub: 'AI 自動生成' },
    { id: 'grammar', label: 'Grammar', icon: LibrarySquare, sub: '文法特訓' },
  ];

  return (
    <div className={`grid grid-cols-2 md:grid-cols-4 gap-4 mb-10 ${disabled ? 'opacity-50 pointer-events-none grayscale' : ''}`}>
      {modes.map((m) => {
        const Icon = m.icon;
        const isActive = activeMode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => !disabled && setMode(m.id as Mode)}
            className={`relative group flex flex-col items-center justify-center p-5 rounded-2xl border transition-all duration-300 overflow-hidden ${
              isActive
                ? 'bg-blue-50 dark:bg-blue-600/10 border-blue-500/50 shadow-sm dark:shadow-[0_0_20px_-5px_rgba(37,99,235,0.3)]'
                : 'bg-white dark:bg-slate-900/50 border-slate-200 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-slate-800/80 hover:border-slate-300 dark:hover:border-white/10'
            }`}
          >
            <div className={`mb-3 p-3 rounded-xl transition-colors ${
              isActive ? 'bg-blue-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 group-hover:text-slate-700 dark:group-hover:text-slate-200'
            }`}>
              <Icon size={24} />
            </div>
            <div className="text-center">
              <span className={`block text-base font-bold ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-700 dark:text-slate-300'}`}>
                {m.label}
              </span>
              <span className="text-xs text-slate-500 mt-1 block">{m.sub}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
};

