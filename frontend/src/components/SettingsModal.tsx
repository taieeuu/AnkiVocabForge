import React from 'react';
import { Settings, X, Volume2 } from 'lucide-react';
import type { Settings as SettingsType } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: SettingsType;
  setSettings: (settings: SettingsType) => void;
  onSave?: (settings: SettingsType) => Promise<boolean>;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, settings, setSettings, onSave }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 dark:bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-950 w-full max-w-2xl rounded-2xl border border-slate-200 dark:border-white/10 shadow-2xl flex flex-col max-h-[85vh] transition-colors">
        <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-white/5">
          <h2 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-3">
            <Settings size={22} className="text-blue-500" /> 系統設定
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>

        <div className="p-8 overflow-y-auto custom-scrollbar space-y-8">
          {/* AI Config */}
          <div className="space-y-5">
            <label className="text-sm font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">AI Configuration</label>
            <div>
              <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">OpenAI API Key</div>
              <input 
                type="password" 
                value={settings.apiKey}
                onChange={(e) => setSettings({...settings, apiKey: e.target.value})}
                className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-800 dark:text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none font-mono text-base transition-all"
              />
            </div>
            <div>
              <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">Model</div>
              <select 
                value={settings.model}
                onChange={(e) => setSettings({...settings, model: e.target.value})}
                className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none text-base"
              >
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4o-mini">gpt-4o-mini</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">Source Language</div>
                <select 
                  value={settings.sourceLanguage}
                  onChange={(e) => setSettings({...settings, sourceLanguage: e.target.value})}
                  className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none text-base"
                >
                  <option value="English">English</option>
                  <option value="Japanese">日本語</option>
                  <option value="Chinese">中文</option>
                  <option value="Korean">한국어</option>
                  <option value="Spanish">Español</option>
                  <option value="French">Français</option>
                  <option value="German">Deutsch</option>
                </select>
              </div>
              <div>
                <div className="text-base text-slate-700 dark:text-slate-300 mb-2.5">Target Language</div>
                <select 
                  value={settings.language}
                  onChange={(e) => setSettings({...settings, language: e.target.value})}
                  className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3 text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none text-base"
                >
                  <option value="Chinese">繁體中文</option>
                  <option value="English">English</option>
                  <option value="Japanese">日本語</option>
                  <option value="Korean">한국어</option>
                  <option value="Spanish">Español</option>
                  <option value="French">Français</option>
                  <option value="German">Deutsch</option>
                </select>
              </div>
            </div>
          </div>

          {/* Audio / TTS Config */}
          <div className="space-y-5 pt-6 border-t border-slate-100 dark:border-white/5">
            <label className="text-sm font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider flex items-center gap-2">
                <Volume2 size={16} /> Audio / TTS Settings
            </label>
            <div className="flex items-center gap-4">
                <button 
                    onClick={() => setSettings({...settings, audio: { ...settings.audio, enabled: !settings.audio.enabled }})}
                    className={`px-4 py-2.5 rounded-xl border font-medium transition-all ${
                        settings.audio.enabled 
                        ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 text-blue-600 dark:text-blue-400' 
                        : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-500'
                    }`}
                >
                    {settings.audio.enabled ? 'Enabled' : 'Disabled'}
                </button>
                <div className="flex-1">
                    <select 
                        disabled={!settings.audio.enabled}
                        value={settings.audio.voice}
                        onChange={(e) => setSettings({...settings, audio: { ...settings.audio, voice: e.target.value }})}
                        className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-2.5 text-slate-800 dark:text-slate-200 focus:border-blue-500 outline-none text-base disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <option value="alloy">Alloy (Neutral)</option>
                        <option value="echo">Echo (Male)</option>
                        <option value="shimmer">Shimmer (Female)</option>
                    </select>
                </div>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-slate-100 dark:border-white/5 bg-slate-50 dark:bg-slate-900/50 rounded-b-2xl flex justify-end gap-4">
          <button onClick={onClose} className="px-6 py-2.5 text-base text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition-colors">取消</button>
          <button 
            onClick={async () => {
              if (onSave) {
                const success = await onSave(settings);
                if (success) {
                  onClose();
                }
              } else {
                onClose();
              }
            }} 
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-base font-medium shadow-lg shadow-blue-500/20 dark:shadow-blue-900/20 transition-all active:scale-95"
          >
            儲存變更
          </button>
        </div>
      </div>
    </div>
  );
};

