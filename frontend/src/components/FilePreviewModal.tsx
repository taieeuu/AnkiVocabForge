import React from 'react';
import { X, FileText, Image as ImageIcon } from 'lucide-react';

interface FilePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  content: string;
  type?: 'text' | 'image';
}

export const FilePreviewModal: React.FC<FilePreviewModalProps> = ({ isOpen, onClose, title, content, type = 'text' }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 dark:bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-950 w-full max-w-4xl rounded-2xl border border-slate-200 dark:border-white/10 shadow-2xl flex flex-col h-[80vh] transition-colors">
        <div className="flex items-center justify-between p-4 px-6 border-b border-slate-100 dark:border-white/5">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-3">
             {type === 'image' ? <ImageIcon size={20} className="text-blue-500" /> : <FileText size={20} className="text-blue-500" />}
             {title}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors">
            <X size={24} />
          </button>
        </div>
        <div className="flex-1 overflow-auto p-6 bg-slate-50 dark:bg-slate-900/50 custom-scrollbar flex items-center justify-center">
           {type === 'image' ? (
             <img src={content} alt={title} className="max-w-full max-h-full object-contain rounded-lg shadow-sm" />
           ) : (
             <pre className="font-mono text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed w-full">
               {content || "Empty file or unable to read content."}
             </pre>
           )}
        </div>
        <div className="p-4 px-6 border-t border-slate-100 dark:border-white/5 bg-white dark:bg-slate-950 rounded-b-2xl flex justify-end">
          <button onClick={onClose} className="px-5 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-lg text-sm font-medium transition-colors">
            Close Preview
          </button>
        </div>
      </div>
    </div>
  );
};

