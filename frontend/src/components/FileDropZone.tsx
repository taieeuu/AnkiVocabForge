import React, { useRef } from 'react';
import { Upload, X, Check, Eye, FileText, Image as ImageIcon } from 'lucide-react';

interface FileDropZoneProps {
  label: string;
  subLabel: string;
  accept: string;
  file?: File | null;
  files?: File[];
  setFile?: (file: File | null) => void;
  setFiles?: (files: File[] | ((prev: File[]) => File[])) => void;
  onPreview?: (file: File) => void;
  multiple?: boolean;
  icon?: React.ComponentType<{ size?: number; className?: string }>;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({ 
  label, 
  subLabel, 
  accept, 
  file, 
  files, 
  setFile, 
  setFiles, 
  onPreview, 
  multiple = false, 
  icon: Icon = Upload 
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  // Helper to handle drops or selection
  const handleFiles = (incomingFiles: FileList | null) => {
    if (!incomingFiles || incomingFiles.length === 0) return;

    if (multiple) {
      const newFiles = Array.from(incomingFiles);
      setFiles && setFiles(prev => [...prev, ...newFiles]);
    } else {
      // 單一文件模式：只接受第一個文件
      if (incomingFiles.length > 1) {
        console.warn(`Only one file is allowed. Using the first file: ${incomingFiles[0].name}`);
      }
      setFile && setFile(incomingFiles[0]);
    }
  };

  const removeFile = (indexToRemove: number) => {
    if (multiple) {
      setFiles && setFiles(prev => prev.filter((_, i) => i !== indexToRemove));
    } else {
      setFile && setFile(null);
    }
    if (inputRef.current) inputRef.current.value = '';
  };

  const hasFiles = multiple ? (files && files.length > 0) : !!file;

  const handleContainerClick = () => {
    inputRef.current?.click();
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="flex justify-between items-center mb-2">
        <label className="text-base font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
           {label}
           {multiple && hasFiles && <span className="text-xs bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-full">{files?.length} files</span>}
        </label>
        <span className="text-xs text-slate-500 bg-slate-100 dark:bg-slate-900 px-2 py-0.5 rounded font-mono">{accept}</span>
      </div>

      <div 
        onClick={handleContainerClick}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`
        relative border-2 border-dashed rounded-2xl transition-all cursor-pointer text-center group flex flex-col
        ${hasFiles
          ? 'border-green-500/50 bg-green-50/50 dark:bg-green-900/10' 
          : 'border-slate-200 dark:border-slate-800 hover:border-blue-500 dark:hover:border-blue-500/50 hover:bg-slate-50 dark:hover:bg-slate-900/50 bg-slate-50/50 dark:bg-transparent justify-center items-center h-32'
        }
      `}>
        
        {hasFiles ? (
           <div 
              className={`w-full ${multiple ? 'p-2 max-h-32 overflow-y-auto custom-scrollbar' : 'p-6 flex flex-col items-center justify-center h-full'}`}
              onClick={(e) => {
                 e.stopPropagation(); 
              }}
           >
              {multiple ? (
                 <div className="space-y-2">
                   {files?.map((f, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-white dark:bg-slate-950/50 p-2 rounded-lg border border-slate-100 dark:border-white/5 animate-in slide-in-from-bottom-2 duration-200">
                          <div className="flex items-center gap-3 overflow-hidden">
                             <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg flex-shrink-0 flex items-center justify-center">
                                {f.type.includes('image') ? <ImageIcon size={14} /> : <FileText size={14} />}
                             </div>
                             <p className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">{f.name}</p>
                          </div>
                          <button 
                              onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                              className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                          >
                              <X size={14} />
                          </button>
                      </div>
                   ))}
                   <div 
                      onClick={(e) => {
                          e.stopPropagation();
                          handleContainerClick();
                      }}
                      className="pt-2 text-xs text-slate-400 hover:text-blue-500 transition-colors cursor-pointer"
                   >
                      Click or drop to add more
                   </div>
                 </div>
              ) : (
                <div 
                  className="flex flex-col items-center animate-in zoom-in duration-300 w-full"
                  onClick={handleContainerClick} 
                >
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mb-2">
                    <Check size={20} />
                  </div>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200 truncate max-w-[180px] mb-2">{file?.name}</p>
                  
                  {accept.includes('.txt') && (
                    <button 
                        onClick={(e) => { e.stopPropagation(); onPreview && onPreview(file as File); }}
                        className="z-10 flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-lg text-xs font-medium shadow-sm hover:text-blue-500 dark:hover:text-blue-400 hover:shadow-md transition-all border border-slate-100 dark:border-white/5"
                        title="Preview content"
                    >
                        <Eye size={14} /> Preview Content
                    </button>
                  )}

                  <div className="absolute top-2 right-2 z-10">
                    <button 
                        onClick={(e) => { e.stopPropagation(); removeFile(0); }}
                        className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-white dark:hover:bg-slate-800 rounded-full transition-colors"
                        title="Remove File"
                    >
                        <X size={16} />
                    </button>
                  </div>
                </div>
              )}
           </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full w-full">
            <Icon size={24} className="text-slate-400 group-hover:text-blue-500 mb-2 transition-colors" />
            <p className="text-sm text-slate-500 dark:text-slate-400 group-hover:text-slate-800 dark:group-hover:text-slate-200">
              {subLabel}
            </p>
          </div>
        )}

        <input 
          ref={inputRef}
          type="file" 
          accept={accept} 
          multiple={multiple}
          className="hidden" 
          onChange={(e) => handleFiles(e.target.files)} 
        />
      </div>
    </div>
  );
};

