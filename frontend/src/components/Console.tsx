import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2, Maximize2, Minimize2 } from 'lucide-react';
import type { Log, ConsoleHeight } from '../types';

interface ConsoleProps {
  logs: Log[];
  heightState: ConsoleHeight;
  setHeightState: (height: ConsoleHeight) => void;
  clearLogs: () => void;
}

export const Console: React.FC<ConsoleProps> = ({ logs, heightState, setHeightState, clearLogs }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const heights: Record<ConsoleHeight, string> = { min: 'h-11', mid: 'h-72', max: 'h-[85vh]' };

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [logs]);

  const toggleSize = () => {
    if (heightState === 'min') setHeightState('mid');
    else if (heightState === 'mid') setHeightState('max');
    else setHeightState('min');
  };

  return (
    <div className={`fixed bottom-0 left-0 right-0 bg-slate-950 border-t border-slate-300 dark:border-blue-500/30 shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.3)] transition-all duration-300 flex flex-col z-30 ${heights[heightState]}`}>
      <div 
        className="flex items-center justify-between px-6 h-11 bg-slate-900/90 dark:bg-slate-900/80 backdrop-blur cursor-pointer hover:bg-slate-800/90 transition-colors border-b border-white/5 group"
        onClick={() => setHeightState(heightState === 'min' ? 'mid' : 'min')}
      >
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-slate-700 group-hover:bg-red-500/80 transition-colors" />
            <div className="w-3 h-3 rounded-full bg-slate-700 group-hover:bg-yellow-500/80 transition-colors" />
            <div className="w-3 h-3 rounded-full bg-slate-700 group-hover:bg-green-500/80 transition-colors" />
          </div>
          <span className="text-sm font-mono font-medium text-slate-400 ml-2 flex items-center gap-2">
            <Terminal size={14} /> 
            SYSTEM_LOGS
            {logs.length > 0 && <span className="bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded text-xs">{logs.length}</span>}
          </span>
        </div>
        <div className="flex items-center gap-3">
           <button onClick={(e) => { e.stopPropagation(); clearLogs(); }} className="p-1.5 hover:bg-white/10 rounded text-slate-500 hover:text-red-400 transition-colors">
            <Trash2 size={14} />
          </button>
          <div className="w-px h-4 bg-white/10 mx-1"></div>
          <button onClick={(e) => { e.stopPropagation(); toggleSize(); }} className="p-1.5 hover:bg-white/10 rounded text-slate-500 hover:text-white transition-colors">
            {heightState === 'max' ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 font-mono text-sm space-y-2 custom-scrollbar bg-slate-950">
        {logs.length === 0 && <div className="text-slate-700 select-none">// Waiting for input...</div>}
        {logs.map((log, index) => (
          <div key={index} className="flex gap-4 group hover:bg-white/5 px-3 -mx-3 rounded py-1">
            <span className="text-slate-600 w-20 flex-shrink-0 select-none">{log.time}</span>
            <span className={`break-all ${
              log.type === 'error' ? 'text-red-400' : 
              log.type === 'success' ? 'text-green-400' : 
              log.type === 'warning' ? 'text-yellow-400' : 'text-slate-300'
            }`}>
              <span className={`mr-3 font-bold ${
                 log.type === 'error' ? 'text-red-500' : 
                 log.type === 'success' ? 'text-green-500' : 'text-blue-500'
              }`}>{log.type === 'info' ? 'ℹ' : log.type === 'success' ? '✔' : '✖'}</span>
              {log.msg}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

