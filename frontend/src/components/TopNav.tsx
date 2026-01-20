import React from 'react';
import { Settings, Bot, Sun, Moon } from 'lucide-react';

interface TopNavProps {
  openSettings: () => void;
  modelName: string;
  isDark: boolean;
  toggleTheme: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({ openSettings, modelName, isDark, toggleTheme }) => (
  <nav className="h-18 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-white/10 flex items-center justify-between px-6 fixed top-0 w-full z-40 transition-colors duration-300">
    <div className="flex items-center gap-4">
      <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
        <span className="text-white font-bold text-lg">AG</span>
      </div>
      <div>
        <h1 className="text-lg font-bold text-slate-800 dark:text-slate-100 tracking-tight">Anki Generator Pro</h1>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono uppercase tracking-wide">System Ready</span>
        </div>
      </div>
    </div>

    <div className="flex items-center gap-4">
      <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-white/5">
         <Bot size={16} className="text-blue-500 dark:text-blue-400" />
         <span className="text-sm font-mono text-slate-600 dark:text-slate-300">{modelName}</span>
      </div>
      
      <div className="h-8 w-px bg-slate-200 dark:bg-white/10 mx-2"></div>

      <button 
        onClick={toggleTheme}
        className="p-2.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl transition-colors"
        title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
      >
        {isDark ? <Sun size={22} /> : <Moon size={22} />}
      </button>

      <button 
        onClick={openSettings}
        className="p-2.5 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl transition-colors"
      >
        <Settings size={22} />
      </button>
    </div>
  </nav>
);

