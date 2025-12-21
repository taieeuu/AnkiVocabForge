import React, { useState, useEffect } from 'react';
import { 
  Play, 
  LibrarySquare, 
  Bot, 
  BookOpen, 
  Check,
  RefreshCw,
  ArrowLeft,
  CheckCircle,
  Grid,
  Plus,
  Files,
  Target,
  Tag,        
  Trash2,
  Eye,
  FileJson,
  Download,
  Save,
  LayoutTemplate,
  CreditCard,
  AlertCircle
} from 'lucide-react';
import type { Mode, WorkflowStage, EditViewMode, ConsoleHeight, LogType, Log, Settings as SettingsType, ImageData } from './types';
import { TopNav, ModeSelector, SettingsModal, FilePreviewModal, Console, FileDropZone, CardPreview } from './components';
import { getApiUrl } from './utils/api';

export default function App() {
  const [isDark, setIsDark] = useState<boolean>(false);
  const [mode, setMode] = useState<Mode>('article');
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [consoleHeight, setConsoleHeight] = useState<ConsoleHeight>('min');
  
  // Workflow State: 'input' -> 'selection' -> 'processing' -> 'json_edit' -> 'finished'
  const [workflowStage, setWorkflowStage] = useState<WorkflowStage>('input');
  const [editViewMode, setEditViewMode] = useState<EditViewMode>('json');
  const [jsonError, setJsonError] = useState<string | null>(null);
  
  // Data States
  const [noteType, setNoteType] = useState<'basic' | 'cloze'>('basic');
  const [deckName, setDeckName] = useState<string>('Japanese_N4');
  const [noteName, setNoteName] = useState<string>('Basic');
  const [deckTags, setDeckTags] = useState<string>(''); 
  const [userGoal, setUserGoal] = useState<string>('');
  
  // Files
  const [articleFiles, setArticleFiles] = useState<File[]>([]);
  const [vocabFile, setVocabFile] = useState<File | null>(null);
  const [grammarFile, setGrammarFile] = useState<File | null>(null);
  
  // Preview States
  const [previewContent, setPreviewContent] = useState<string>('');
  const [previewTitle, setPreviewTitle] = useState<string>('');
  const [previewType, setPreviewType] = useState<'text' | 'image'>('text');
  const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(false);
  
  // Image Selection State
  const [extractedImages, setExtractedImages] = useState<ImageData[]>([]);
  
  const [aiTopic, setAiTopic] = useState<string>('');
  const [generatedJson, setGeneratedJson] = useState<string>('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionFiles, setSessionFiles] = useState<any[]>([]);

  // Settings State
  const [settings, setSettings] = useState<SettingsType>({
    apiKey: '',
    model: 'gpt-4o-mini',
    language: 'Chinese',
    sourceLanguage: 'English',
    audio: { enabled: false, voice: 'alloy' }
  });

  // 保存设置
  const saveSettings = async (newSettings: SettingsType): Promise<boolean> => {
    try {
      setSettings(newSettings);
      addLog('Settings updated', 'success');
      return true;
    } catch (e) {
      addLog('Failed to save settings', 'error');
      console.error('Save settings error:', e);
      return false;
    }
  };

  // Logs State
  const [logs, setLogs] = useState<Log[]>([
    { time: '10:00:01', type: 'info', msg: 'System initialized v2.6.1' },
  ]);

  const addLog = (msg: string, type: LogType = 'info') => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => [...prev, { time, msg, type }]);
  };

  useEffect(() => {
    setWorkflowStage('input');
    setArticleFiles([]);
    setVocabFile(null);
    setGrammarFile(null);
    setAiTopic('');
    setGeneratedJson('');
    setExtractedImages([]);
    setUserGoal('');
    setEditViewMode('json');
    setJsonError(null);
    setSessionId(null); // 切換模式時重置 sessionId
    setSessionFiles([]);
  }, [mode]);

  const handleJsonChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setGeneratedJson(value);
    try {
      JSON.parse(value);
      setJsonError(null);
    } catch (e) {
      setJsonError((e as Error).message);
    }
  };

  const handlePreview = (file: File) => {
      if (!file) return;
      setPreviewType('text');
      const reader = new FileReader();
      reader.onload = (e) => {
          setPreviewContent(e.target?.result as string);
          setPreviewTitle(file.name);
          setIsPreviewOpen(true);
      };
      reader.readAsText(file);
  };

  const handleViewImage = (e: React.MouseEvent, img: ImageData) => {
      e.stopPropagation();
      setPreviewType('image');
      setPreviewContent(img.src);
      setPreviewTitle(`Image View - ID: ${img.id}`);
      setIsPreviewOpen(true);
  };

  const handleDeleteImage = (e: React.MouseEvent, id: number) => {
      e.stopPropagation();
      setExtractedImages(prev => prev.filter(img => img.id !== id));
      addLog(`Image ID ${id} removed from selection.`, 'info');
  };

  const handleUploadAdditionalImage = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const newImage = {
          id: Date.now(),
          src: URL.createObjectURL(file),
          selected: true,
          isUserUploaded: true
      };
      setExtractedImages(prev => [...prev, newImage]);
      addLog(`User added new image: ${file.name}`, 'success');
  };

  const validateInputs = (): { valid: boolean; message: string } => {
    if (!settings.apiKey || settings.apiKey.includes('***') || settings.apiKey.trim() === '') {
      return { valid: false, message: 'Please set your OpenAI API Key in Settings' };
    }
    
    if (mode === 'article') {
      if (articleFiles.length === 0) {
        return { valid: false, message: 'Please upload Article Source files (PDF or Images)' };
      }
      if (!vocabFile) {
        return { valid: false, message: 'Please upload Vocabulary List file (.txt)' };
      }
    } else if (mode === 'vocab') {
      if (!vocabFile) {
        return { valid: false, message: 'Please upload Vocabulary List file (.txt)' };
      }
    } else if (mode === 'grammar') {
      if (!grammarFile) {
        return { valid: false, message: 'Please upload Grammar file (.txt)' };
      }
    } else if (mode === 'ai') {
      if (!aiTopic || aiTopic.trim() === '') {
        return { valid: false, message: 'Please enter a Topic for AI generation' };
      }
    }
    
    return { valid: true, message: '' };
  };

  const handleAnalyzeSource = async () => {
    if (workflowStage !== 'input') return;
    
    const validation = validateInputs();
    if (!validation.valid) {
      setConsoleHeight('mid');
      addLog(`✖ ${validation.message}`, 'error');
      window.alert(validation.message);
      return;
    }

    if (mode === 'article') {
        setConsoleHeight('mid');
        addLog(`Analyzing ${articleFiles.length} source files...`, 'info');
        
        try {
            const allImages: ImageData[] = [];
            let currentSessionId = sessionId; // 使用現有的 sessionId 或 null
            
            for (const file of articleFiles) {
                addLog(`Processing ${file.name}...`, 'info');
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('settings', JSON.stringify({
                    apiKey: settings.apiKey && !settings.apiKey.includes('***') ? settings.apiKey : '',
                    model: settings.model,
                    language: settings.language
                }));
                // 如果是第一個文件且還沒有 sessionId，不傳遞；否則傳遞現有的 sessionId
                if (currentSessionId) {
                    formData.append('sessionId', currentSessionId);
                }
                
                const response = await fetch(getApiUrl('/api/analyze/images'), {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to analyze ${file.name}`);
                }
                
                const data = await response.json();
                // 保存 sessionId（第一次或後續都使用同一個）
                if (data.sessionId) {
                    currentSessionId = data.sessionId;
                    setSessionId(data.sessionId);
                }
                
                if (data.success && data.images) {
                    const convertedImages = data.images.map((img: any, idx: number) => ({
                        id: allImages.length + idx + 1,
                        src: img.src.startsWith('http') ? img.src : `${window.location.origin}${img.src}`,
                        path: img.path,
                        selected: img.selected !== false,
                        isUserUploaded: false
                    }));
                    
                    allImages.push(...convertedImages);
                    addLog(`Extracted ${data.images.length} images from ${file.name}`, 'success');
                }
            }
            
            if (allImages.length === 0) {
                addLog('Warning: No images extracted from files', 'warning');
            } else {
                setExtractedImages(allImages);
                addLog(`Total: ${allImages.length} images extracted from ${articleFiles.length} files.`, 'success');
            setWorkflowStage('selection');
            setConsoleHeight('min');
            }
        } catch (error: unknown) {
            let errorMessage = 'Unknown error';
            let detailedMessage = '';
            
            if (error instanceof Error) {
                errorMessage = error.message;
                if (errorMessage.includes('API') || errorMessage.includes('api') || errorMessage.includes('key') || errorMessage.includes('401') || errorMessage.includes('403')) {
                    detailedMessage = 'This error is likely due to missing or invalid OpenAI API Key. Please check your API Key in Settings.';
                } else if (errorMessage.includes('Failed to analyze')) {
                    detailedMessage = errorMessage;
                }
            }
            
            const fullErrorMsg = detailedMessage 
                ? `✖ Error analyzing files: ${errorMessage}\n   Details: ${detailedMessage}`
                : `✖ Error analyzing files: ${errorMessage}`;
            
            addLog(fullErrorMsg, 'error');
            console.error('Analysis error:', error);
            
            if (detailedMessage.includes('API Key')) {
                window.alert('OpenAI API Key Error\n\n' + detailedMessage + '\n\nPlease check your API Key in Settings.');
            }
        }
    } else {
        startGeneration();
    }
  };

  const startGeneration = async () => {
    setWorkflowStage('processing');
    setConsoleHeight('mid');
    
    addLog(`Starting [${mode.toUpperCase()}] pipeline...`, 'info');
    addLog(`GPT Model: ${settings.model}`, 'info');
    if (userGoal) addLog(`With user goal: "${userGoal.substring(0, 30)}..."`, 'info');
    addLog(`Note Name: "${noteName}"`, 'info');
    if (deckTags) addLog(`Tags: [${deckTags}]`, 'info');
    if (settings.audio.enabled) addLog(`Audio Generation: ON (${settings.audio.voice})`, 'info');
    
    try {
      let apiEndpoint = '';
      let requestBody: any = {
        deckName: deckName,
        noteName: noteName,
        userGoal: userGoal,
        tags: deckTags,
        sessionId: sessionId, // 傳遞現有的 sessionId（如果有的話）
        settings: {
          apiKey: settings.apiKey && !settings.apiKey.includes('***') ? settings.apiKey : '',
          model: settings.model,
          language: settings.language,
          sourceLang: settings.sourceLanguage,
          audio: settings.audio
        }
      };

      if (mode === 'article') {
        apiEndpoint = '/api/generate/article';
        const selectedCount = extractedImages.filter(i => i.selected).length;
        addLog(`Sending ${selectedCount} selected images to GPT-4o Vision...`, 'info');
        addLog('Reading vocab list...', 'info');
        
        let vocabContent = '';
        if (vocabFile) {
          vocabContent = await vocabFile.text();
          addLog(`Reading vocab list: ${vocabFile.name}...`, 'info');
        }
        
        requestBody.images = extractedImages.filter(i => i.selected);
        requestBody.vocabList = vocabFile ? {
          content: vocabContent,
          filename: vocabFile.name
        } : null;
        
    } else if (mode === 'vocab') {
        apiEndpoint = '/api/generate/vocab';
        addLog(`Reading vocab list: ${vocabFile?.name}...`, 'info');
        
        let vocabContent = '';
        if (vocabFile) {
          vocabContent = await vocabFile.text();
    }

        requestBody.vocabList = vocabFile ? {
          content: vocabContent,
          filename: vocabFile.name
        } : null;
        
      } else if (mode === 'ai') {
        apiEndpoint = '/api/generate/ai';
        requestBody.topic = aiTopic;
        requestBody.count = 10;
        
      } else if (mode === 'grammar') {
        apiEndpoint = '/api/generate/grammar';
        addLog(`Reading grammar file: ${grammarFile?.name}...`, 'info');
        
        let grammarContent = '';
        if (grammarFile) {
          grammarContent = await grammarFile.text();
        }
        
        requestBody.grammarFile = grammarContent;
      }

      addLog(`Using GPT Model: ${settings.model}`, 'info');
      addLog(`Generating content...`, 'info');
      
      const response = await fetch(getApiUrl(apiEndpoint), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        let detailedMessage = '';
        
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.details || errorMessage;
          
          if (errorData.details) {
            const details = errorData.details.toLowerCase();
            if (details.includes('api') || details.includes('key') || details.includes('401') || details.includes('403') || details.includes('unauthorized') || details.includes('forbidden')) {
              detailedMessage = 'This error is likely due to missing or invalid OpenAI API Key. Please check your API Key in Settings.';
            } else {
              detailedMessage = errorData.details;
            }
            addLog(`Details: ${detailedMessage}`, 'error');
          }
        } catch (e) {
          errorMessage = `${response.status} ${response.statusText}`;
          if (response.status === 401 || response.status === 403) {
            detailedMessage = 'This error is likely due to missing or invalid OpenAI API Key. Please check your API Key in Settings.';
          }
        }
        
        const fullErrorMsg = detailedMessage 
          ? `✖ Generation failed: ${errorMessage}\n   Details: ${detailedMessage}`
          : `✖ Generation failed: ${errorMessage}`;
        
        addLog(fullErrorMsg, 'error');
        
        if (detailedMessage.includes('API Key')) {
          window.alert('OpenAI API Key Error\n\n' + detailedMessage + '\n\nPlease check your API Key in Settings.');
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (data.success && data.cards) {
        const cardsJson = JSON.stringify(data.cards, null, 2);
        setGeneratedJson(cardsJson);
        if (data.sessionId) {
          setSessionId(data.sessionId);
          addLog(`Session ID: ${data.sessionId}`, 'info');
          setTimeout(() => handleListFiles(data.sessionId), 500); // 傳遞 sessionId 參數
        }
      setWorkflowStage('json_edit');
        addLog(`Generation complete. Generated ${data.cards.length} cards.`, 'success');
        if (data.message) {
          addLog(data.message, 'info');
        }
      setConsoleHeight('min'); 
      } else {
        const errorMsg = data.error || data.details || 'Generation failed';
        throw new Error(errorMsg);
      }
      
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      addLog(`Error: ${errorMessage}`, 'error');
      console.error('Generation error:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        addLog('Network error: Please check if backend is running on port 5000', 'error');
      }
      setConsoleHeight('mid');
    }
  };

  const toggleImageSelection = (id: number) => {
    setExtractedImages(prev => prev.map(img => 
        img.id === id ? { ...img, selected: !img.selected } : img
    ));
  };

  const handlePack = async () => {
    addLog('Validating JSON structure...', 'info');
    try {
      const cards = JSON.parse(generatedJson);
      
      const response = await fetch(getApiUrl('/api/generate/package'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cards: cards,
          deckName: deckName,
          noteName: noteName,
          tags: deckTags,
          sessionId: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Packaging failed');
      }

      const data = await response.json();
      addLog(`Packaging complete: ${data.message}`, 'success');
      setWorkflowStage('finished');
      // 如果沒有 sessionId，使用返回的 sessionId
      if (data.sessionId && !sessionId) {
        setSessionId(data.sessionId);
      }
      if (sessionId || data.sessionId) {
        await handleListFiles(sessionId || data.sessionId); // 傳遞 sessionId 參數
      }
    } catch (error) {
      addLog(`Packaging error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
  };

  const handleDownload = async (filePath?: string, fileName?: string) => {
    if (!sessionId) {
      addLog('No session ID available', 'error');
      return;
    }

    try {
      addLog('Preparing download...', 'info');
      
      let downloadUrl: string;
      if (filePath) {
        downloadUrl = getApiUrl(`/api/files/download/${sessionId}/${filePath}`);
      } else {
        downloadUrl = getApiUrl(`/api/files/download/${sessionId}`);
      }

      const link = document.createElement('a');
      link.href = downloadUrl;
      // 如果提供了檔案名稱，使用它；否則讓瀏覽器自動決定
      if (fileName) {
        link.download = fileName;
      } else {
        link.download = '';
      }
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      addLog('Download started', 'success');

      setTimeout(async () => {
        try {
          const cleanupResponse = await fetch(getApiUrl(`/api/files/cleanup/${sessionId}`), {
            method: 'DELETE'
          });
          if (cleanupResponse.ok) {
            addLog(`Session ${sessionId} will be cleaned up in 5 seconds`, 'info');
          }
        } catch (error) {
          console.error('Cleanup error:', error);
        }
      }, 1000);

    } catch (error) {
      addLog(`Download error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    }
  };

  const handleListFiles = async (sessionIdParam?: string) => {
    const idToUse = sessionIdParam || sessionId;
    if (!idToUse) {
      addLog('No session ID available', 'error');
      return [];
    }
  
    try {
      const response = await fetch(getApiUrl(`/api/files/list/${idToUse}`));
      if (!response.ok) {
        throw new Error('Failed to list files');
      }
      const data = await response.json();
      setSessionFiles(data.files || []);
      addLog(`Found ${data.files.length} files in session`, 'info');
      return data.files;
    } catch (error) {
      addLog(`List files error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return [];
    }
  };

  return (
    <div className={isDark ? 'dark' : ''}>
      <div className="flex flex-col h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-200 font-sans selection:bg-blue-500/30 overflow-hidden transition-colors duration-300">
        
        <TopNav 
          openSettings={() => setIsSettingsOpen(true)} 
          modelName={settings.model} 
          isDark={isDark}
          toggleTheme={() => setIsDark(!isDark)}
        />

        <main className="flex-1 overflow-y-auto pt-28 pb-40 px-6 md:px-12 custom-scrollbar">
          <div className="max-w-4xl mx-auto animate-in slide-in-from-bottom-4 duration-500">
            
            {/* Step 1: Mode Selection */}
            <section className="mb-8">
               <div className="flex items-center justify-between mb-5">
                <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                    STEP 1: Operation Mode
                </h2>
                {workflowStage !== 'input' && (
                    <button 
                        onClick={() => setWorkflowStage('input')}
                        className="text-xs text-blue-500 hover:text-blue-400 font-medium flex items-center gap-1"
                    >
                        <RefreshCw size={12} /> Reset
                    </button>
                )}
               </div>
              <ModeSelector activeMode={mode} setMode={setMode} disabled={workflowStage !== 'input'} />
            </section>

            {/* Dynamic Card */}
            <section>
              <div className="flex items-center justify-between mb-5">
                  <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                    {workflowStage === 'input' ? 'STEP 2: Configuration' : 
                     workflowStage === 'selection' ? 'STEP 2.5: Select Context' :
                     workflowStage === 'processing' ? 'Processing...' :
                     workflowStage === 'json_edit' ? 'STEP 3: Review & Edit' : 'STEP 4: Download'}
                  </h2>
              </div>
              
              <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-white/5 rounded-3xl p-1.5 shadow-xl shadow-slate-200/50 dark:shadow-black/20 transition-all">
                <div className="bg-white dark:bg-slate-950/50 rounded-2xl p-8 md:p-10 border border-slate-100 dark:border-white/5 min-h-[400px] flex flex-col">
                  
                  {/* STAGE: INPUT */}
                  {workflowStage === 'input' && (
                    <div className="space-y-8 flex-1 animate-in fade-in slide-in-from-right-4 duration-300">
                        {/* Deck & Note Name Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-3">
                                <label className="text-base font-medium text-slate-700 dark:text-slate-300">Target Deck Name</label>
                                <input 
                                    type="text" 
                                    value={deckName}
                                    onChange={(e) => setDeckName(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-3 text-slate-900 dark:text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-400 text-lg"
                                />
                            </div>
                            <div className="space-y-3">
                                <label className="text-base font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
                                    <CreditCard size={16} /> Anki Note Name
                                </label>
                                <input 
                                    type="text" 
                                    value={noteName}
                                    onChange={(e) => setNoteName(e.target.value)}
                                    placeholder="e.g. Basic (and reversed card)"
                                    className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-3 text-slate-900 dark:text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-400 text-lg"
                                />
                            </div>
                        </div>

                        {/* Note Type & Tags Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-3">
                                <label className="text-base font-medium text-slate-700 dark:text-slate-300">Note Type</label>
                                <div className="flex bg-slate-100 dark:bg-slate-900 p-1.5 rounded-xl border border-slate-200 dark:border-slate-800">
                                    {['basic', 'cloze'].map((type) => (
                                        <button
                                        key={type}
                                        onClick={() => setNoteType(type as 'basic' | 'cloze')}
                                        className={`flex-1 py-2.5 text-base rounded-lg transition-all font-medium ${
                                            noteType === type 
                                            ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm border border-slate-200 dark:border-slate-700' 
                                            : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                                        }`}
                                        >
                                        {type === 'basic' ? 'Basic' : 'Cloze'}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="space-y-3">
                                <label className="text-base font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
                                    <Tag size={16} /> Default Tags
                                </label>
                                <input 
                                    type="text" 
                                    value={deckTags}
                                    onChange={(e) => setDeckTags(e.target.value)}
                                    placeholder="N4, Vocabulary, Chapter1 (space separated)"
                                    className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-3 text-slate-900 dark:text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-400 text-base"
                                />
                            </div>
                        </div>

                        {/* Goal Input */}
                        <div className="space-y-3">
                            <label className="text-base font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
                                <Target size={18} className="text-blue-500" />
                                Generation Goal / Instructions <span className="text-slate-400 font-normal text-sm ml-2">(Optional)</span>
                            </label>
                            <textarea 
                                rows={2}
                                value={userGoal}
                                onChange={(e) => setUserGoal(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-3 text-slate-900 dark:text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all resize-none placeholder:text-slate-400 text-base leading-relaxed"
                                placeholder="E.g., Focus on N3 grammar, include example sentences in business context..."
                            ></textarea>
                        </div>

                        <div className="border-t border-slate-100 dark:border-white/5 pt-8">
                            {/* Mode Specific Inputs */}
                            {mode === 'article' && (
                                <div className="flex flex-col md:flex-row gap-6">
                                    <FileDropZone 
                                        label="Article Source" 
                                        subLabel="Drop PDF(s) or Images" 
                                        accept=".pdf, .png, .jpg, .jpeg" 
                                        multiple={true}
                                        files={articleFiles} 
                                        setFiles={setArticleFiles} 
                                        icon={Files as React.ComponentType<{ size?: number; className?: string }>}
                                    />
                                    <FileDropZone 
                                        label="Unknown Words" 
                                        subLabel="Drop .txt here" 
                                        accept=".txt" 
                                        file={vocabFile} 
                                        setFile={setVocabFile}
                                        onPreview={handlePreview}
                                        icon={BookOpen as React.ComponentType<{ size?: number; className?: string }>}
                                    />
                                </div>
                            )}

                            {mode === 'vocab' && (
                                <FileDropZone 
                                    label="Vocabulary List" 
                                    subLabel="Drop .txt list here" 
                                    accept=".txt" 
                                    file={vocabFile} 
                                    setFile={setVocabFile}
                                    onPreview={handlePreview}
                                    icon={BookOpen as React.ComponentType<{ size?: number; className?: string }>}
                                />
                            )}

                             {mode === 'grammar' && (
                                <FileDropZone 
                                    label="Grammar Points" 
                                    subLabel="Drop grammar .txt here" 
                                    accept=".txt" 
                                    file={grammarFile} 
                                    setFile={setGrammarFile}
                                    onPreview={handlePreview}
                                    icon={LibrarySquare as React.ComponentType<{ size?: number; className?: string }>}
                                />
                            )}

                            {mode === 'ai' && (
                                <div className="space-y-3">
                                    <label className="text-base font-medium text-slate-700 dark:text-slate-300">Generation Prompt / Topic</label>
                                    <textarea 
                                        rows={5}
                                        value={aiTopic}
                                        onChange={(e) => setAiTopic(e.target.value)}
                                        className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl px-5 py-4 text-slate-900 dark:text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all resize-none placeholder:text-slate-400 text-base"
                                        placeholder="Enter the topic or context you want to learn..."
                                    ></textarea>
                                </div>
                            )}
                        </div>

                        <button 
                            onClick={handleAnalyzeSource}
                            className="w-full mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-2xl shadow-xl shadow-blue-500/30 dark:shadow-blue-500/20 active:scale-[0.99] transition-all flex items-center justify-center gap-3"
                        >
                            {mode === 'article' ? (
                                <>
                                    <Grid size={22} fill="currentColor" />
                                    <span className="tracking-wide text-lg">ANALYZE SOURCE</span>
                                </>
                            ) : (
                                <>
                                    <Play size={22} fill="currentColor" />
                                    <span className="tracking-wide text-lg">START GENERATION</span>
                                </>
                            )}
                        </button>
                    </div>
                  )}

                  {/* STAGE: SELECTION */}
                  {workflowStage === 'selection' && (
                    <div className="flex-1 flex flex-col animate-in fade-in slide-in-from-right-4 duration-300">
                        <div className="mb-4 flex justify-between items-end">
                             <div>
                                <h3 className="text-lg font-bold text-slate-800 dark:text-white">Select Images to Analyze</h3>
                                <p className="text-slate-500 text-sm">Review extracted content. Add new images or remove unwanted ones.</p>
                             </div>
                             <div className="text-sm font-medium text-blue-500">
                                {extractedImages.filter(i => i.selected).length} selected
                             </div>
                        </div>

                        <div className="flex-1 overflow-y-auto custom-scrollbar bg-slate-50 dark:bg-slate-900/50 rounded-xl p-4 mb-6 border border-slate-200 dark:border-white/5">
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {/* Add Image Button */}
                                <div className="relative aspect-[4/3] rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all flex flex-col items-center justify-center cursor-pointer group">
                                    <Plus size={32} className="text-slate-400 group-hover:text-blue-500 mb-2" />
                                    <span className="text-sm text-slate-500 group-hover:text-blue-500 font-medium">Add Image</span>
                                    <input 
                                        type="file" 
                                        accept="image/*" 
                                        className="absolute inset-0 opacity-0 cursor-pointer"
                                        onChange={handleUploadAdditionalImage}
                                    />
                                </div>

                                {/* Extracted Images */}
                                {extractedImages.map((img) => (
                                    <div 
                                        key={img.id}
                                        onClick={() => toggleImageSelection(img.id)}
                                        className={`
                                            relative aspect-[4/3] rounded-lg overflow-hidden cursor-pointer border-2 transition-all group
                                            ${img.selected 
                                                ? 'border-blue-500 ring-2 ring-blue-500/20 shadow-lg' 
                                                : 'border-transparent hover:border-slate-300 dark:hover:border-slate-600 opacity-60 hover:opacity-100'
                                            }
                                        `}
                                    >
                                        <img src={img.src} alt={`Extracted ${img.id}`} className="w-full h-full object-cover" />
                                        
                                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 pointer-events-none">
                                        </div>

                                        <div className="absolute top-2 right-2 flex gap-1 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button 
                                                onClick={(e) => handleViewImage(e, img)}
                                                className="p-1.5 bg-white/90 dark:bg-slate-900/90 text-slate-700 dark:text-slate-300 rounded-lg hover:text-blue-500 hover:scale-110 transition-all shadow-sm"
                                                title="View Full Size"
                                            >
                                                <Eye size={14} />
                                            </button>
                                            <button 
                                                onClick={(e) => handleDeleteImage(e, img.id)}
                                                className="p-1.5 bg-white/90 dark:bg-slate-900/90 text-slate-700 dark:text-slate-300 rounded-lg hover:text-red-500 hover:scale-110 transition-all shadow-sm"
                                                title="Remove Image"
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        </div>

                                        <div className={`absolute bottom-2 right-2 transition-transform duration-200 ${img.selected ? 'scale-100' : 'scale-0 group-hover:scale-100'}`}>
                                            <div className={`rounded-full p-1 ${img.selected ? 'bg-blue-500 text-white' : 'bg-white/80 text-slate-400'}`}>
                                                <CheckCircle size={20} fill={img.selected ? "currentColor" : "none"} />
                                            </div>
                                        </div>

                                        {img.isUserUploaded && (
                                            <div className="absolute top-2 left-2 px-2 py-0.5 bg-green-500/90 text-white text-[10px] font-bold rounded uppercase tracking-wider shadow-sm">
                                                New
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <button 
                                onClick={() => setWorkflowStage('input')}
                                className="px-6 py-3 rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium transition-colors"
                            >
                                Back
                            </button>
                            <button 
                                onClick={startGeneration}
                                disabled={extractedImages.filter(i => i.selected).length === 0}
                                className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-500/20 active:scale-[0.99] transition-all flex items-center justify-center gap-2"
                            >
                                <Bot size={20} />
                                GENERATE FROM SELECTED ({extractedImages.filter(i => i.selected).length})
                            </button>
                        </div>
                    </div>
                  )}

                  {/* STAGE: PROCESSING */}
                  {workflowStage === 'processing' && (
                    <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in duration-500">
                        <div className="relative w-24 h-24 mb-8">
                            <div className="absolute inset-0 border-4 border-slate-200 dark:border-slate-800 rounded-full"></div>
                            <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
                            <Bot className="absolute inset-0 m-auto text-blue-500 animate-pulse" size={40} />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">Generating Content...</h3>
                        <p className="text-slate-500 dark:text-slate-400">Please check the console below for detailed progress.</p>
                    </div>
                  )}

                  {/* STAGE: JSON EDIT / PREVIEW */}
                  {workflowStage === 'json_edit' && (
                     <div className="flex-1 flex flex-col h-full animate-in fade-in slide-in-from-right-4 duration-300">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                                {editViewMode === 'json' ? <FileJson size={20} className="text-yellow-500" /> : <LayoutTemplate size={20} className="text-purple-500" />}
                                <span className="font-mono text-sm">generated_output.json</span>
                            </div>
                            
                            <div className="flex bg-slate-100 dark:bg-slate-900 p-1 rounded-lg border border-slate-200 dark:border-slate-800">
                                <button 
                                    onClick={() => setEditViewMode('json')}
                                    className={`px-3 py-1 text-xs font-medium rounded transition-all flex items-center gap-2 ${editViewMode === 'json' ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                                >
                                    <FileJson size={14} /> JSON Source
                                </button>
                                <button 
                                    onClick={() => setEditViewMode('preview')}
                                    className={`px-3 py-1 text-xs font-medium rounded transition-all flex items-center gap-2 ${editViewMode === 'preview' ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                                >
                                    <LayoutTemplate size={14} /> Card Preview
                                </button>
                            </div>
                        </div>
                        
                        {editViewMode === 'json' ? (
                            <>
                                <textarea 
                                    value={generatedJson}
                                    onChange={handleJsonChange}
                                    className={`flex-1 w-full bg-slate-50 dark:bg-slate-900 border ${jsonError ? 'border-red-500 focus:border-red-500' : 'border-slate-200 dark:border-slate-800 focus:border-blue-500'} rounded-xl p-4 font-mono text-sm text-slate-800 dark:text-blue-100 outline-none resize-none custom-scrollbar mb-2 leading-relaxed`}
                                    spellCheck="false"
                                ></textarea>
                                {jsonError && (
                                    <div className="flex items-center gap-2 text-red-500 text-sm mb-4 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-100 dark:border-red-900/30 animate-in fade-in slide-in-from-top-2">
                                        <AlertCircle size={16} />
                                        <span>Invalid JSON: {jsonError}</span>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="flex-1 w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 mb-6">
                                <CardPreview data={generatedJson} noteType={noteType} />
                            </div>
                        )}

                        <div className="flex gap-4">
                            <button 
                                onClick={() => setWorkflowStage('input')}
                                className="px-6 py-3 rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium transition-colors"
                            >
                                放棄並重新開始
                            </button>
                            <button 
                                onClick={handlePack}
                                disabled={!!jsonError}
                                className={`flex-1 font-bold py-3 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 ${
                                    jsonError 
                                    ? 'bg-slate-300 dark:bg-slate-700 text-slate-500 cursor-not-allowed shadow-none' 
                                    : 'bg-green-600 hover:bg-green-500 text-white shadow-green-500/20 active:scale-[0.99]'
                                }`}
                            >
                                <Save size={20} />
                                生成編輯版 .apkg
                            </button>
                        </div>
                     </div>
                  )}

                   {/* STAGE: FINISHED */}
                   {workflowStage === 'finished' && (
                     <div className="flex-1 flex flex-col items-center justify-center text-center animate-in zoom-in duration-300">
                        <div className="w-24 h-24 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center mb-6 shadow-lg shadow-green-500/20">
                            <Check size={48} strokeWidth={3} />
                        </div>
                        <h3 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">完成！</h3>
                        <p className="text-slate-500 dark:text-slate-400 mb-8 max-w-md">
                            您的 Anki 卡片包已成功生成。編輯版的 .apkg 檔案已準備好，可以匯入到 Anki 應用程式中。
                        </p>
                        
                        {sessionFiles.length > 0 && (
                          <div className="w-full max-w-md mb-6">
                            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 text-left">已生成的檔案：</h4>
                            <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                              {sessionFiles
                                .filter((f: any) => f.isApkg)
                                .map((file: any, idx: number) => (
                                  <div 
                                    key={idx}
                                    className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-slate-200 dark:border-white/5"
                                  >
                                    <div className="flex-1 text-left">
                                      <p className="text-sm font-medium text-slate-800 dark:text-white">{file.name}</p>
                                      <p className="text-xs text-slate-500 dark:text-slate-400">
                                        {(file.size / 1024).toFixed(2)} KB
                                      </p>
                                    </div>
                                    <button
                                      onClick={() => handleDownload(file.path, file.name)}
                                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
                                    >
                                      <Download size={16} />
                                      下載
                                    </button>
                                  </div>
                                ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="flex gap-4 w-full max-w-md">
                             <button 
                                onClick={() => setWorkflowStage('input')}
                                className="flex-1 px-6 py-3 rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium transition-colors flex items-center justify-center gap-2"
                            >
                                <ArrowLeft size={18} /> 建立新卡片組
                            </button>
                            <button 
                                onClick={() => handleDownload()}
                                className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-500/20 active:scale-[0.99] transition-all flex items-center justify-center gap-2"
                            >
                                <Download size={20} />
                                下載完整專案 (ZIP)
                            </button>
                        </div>
                     </div>
                  )}

                </div>
              </div>
            </section>

          </div>
        </main>

        <SettingsModal 
          isOpen={isSettingsOpen} 
          onClose={() => setIsSettingsOpen(false)} 
          settings={settings}
          setSettings={setSettings}
          onSave={saveSettings}
        />

        <FilePreviewModal 
          isOpen={isPreviewOpen} 
          onClose={() => setIsPreviewOpen(false)} 
          title={previewTitle}
          content={previewContent}
          type={previewType}
        />

        <Console 
          logs={logs} 
          heightState={consoleHeight}
          setHeightState={setConsoleHeight}
          clearLogs={() => setLogs([])}
        />

      </div>
    </div>
  );
}
