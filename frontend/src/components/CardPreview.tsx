import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import type { Card } from '../types';

interface CardPreviewProps {
  data: string;
  noteType?: 'basic' | 'cloze';
}

export const CardPreview: React.FC<CardPreviewProps> = ({ data, noteType = 'basic' }) => {
    const cards: Card[] = JSON.parse(data || "[]");
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);
    const [cardType, setCardType] = useState<'card1' | 'card2'>('card1'); // For Basic: Card 1 or Card 2 (Reverse)

    if (cards.length === 0) return <div className="text-slate-500 text-center py-10">No data to preview</div>;

    const currentCard = cards[currentIndex];

    const nextCard = () => {
        setIsFlipped(false);
        setCurrentIndex((prev) => (prev + 1) % cards.length);
    };

    const prevCard = () => {
        setIsFlipped(false);
        setCurrentIndex((prev) => (prev - 1 + cards.length) % cards.length);
    };

    const toggleFlip = () => {
        setIsFlipped(!isFlipped);
    };

    // Render Basic Card 1 (Word -> Meaning)
    const renderBasicCard1 = () => {
        if (!isFlipped) {
            // Front: Word, Pos, Hint, Audio
    return (
                <div className="p-8">
                    <div className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
                        {currentCard.word} <span className="text-gray-500 text-xl">({currentCard.pos})</span>
                    </div>
                    <br />
                    <div className="text-slate-600 dark:text-slate-300">{currentCard.hint}</div>
                    {currentCard.audio && (
                        <div className="mt-4 text-sm text-slate-500">🔊 Audio: {currentCard.audio}</div>
                    )}
                </div>
            );
        } else {
            // Back: Word, Pos, Hint, Audio + Meaning, Synonyms, Ex1, Ex2
            return (
                <div className="p-8">
                    <div className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
                        {currentCard.word} <span className="text-gray-500 text-xl">({currentCard.pos})</span>
                    </div>
                    <br />
                    <div className="text-slate-600 dark:text-slate-300">{currentCard.hint}</div>
                    {currentCard.audio && (
                        <div className="mt-4 text-sm text-slate-500">🔊 Audio: {currentCard.audio}</div>
                    )}
                    <hr className="my-4 border-slate-300 dark:border-slate-600" id="answer" />
                    <div className="text-2xl font-bold text-slate-800 dark:text-white mb-4">
                        {currentCard.meaning}
                    </div>
                    <br />
                    <div className="text-slate-500 dark:text-slate-400 mb-4">
                        {currentCard.synonyms}
                    </div>
                    <br />
                    <div className="mb-4">
                        <div className="text-slate-700 dark:text-slate-200">{currentCard.ex1_ori}</div>
                        <div className="text-slate-500 dark:text-slate-400">{currentCard.ex1_trans}</div>
                    </div>
                    <br />
                    <div>
                        <div className="text-slate-700 dark:text-slate-200">{currentCard.ex2_ori}</div>
                        <div className="text-slate-500 dark:text-slate-400">{currentCard.ex2_trans}</div>
                    </div>
                </div>
            );
        }
    };

    // Render Basic Card 2 (Reverse: Meaning -> Word)
    const renderBasicCard2 = () => {
        if (!isFlipped) {
            // Front: Meaning, Pos, Hint
            return (
                <div className="p-8">
                    <div className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
                        {currentCard.meaning} <span className="text-gray-500 text-xl">({currentCard.pos})</span>
                    </div>
                    <br />
                    <div className="text-slate-600 dark:text-slate-300">{currentCard.hint}</div>
                </div>
            );
        } else {
            // Back: Meaning, Pos, Hint + Word, Synonyms, Ex1, Ex2, Audio
            return (
                <div className="p-8">
                    <div className="text-3xl font-bold text-slate-800 dark:text-white mb-2">
                        {currentCard.meaning} <span className="text-gray-500 text-xl">({currentCard.pos})</span>
                    </div>
                    <br />
                    <div className="text-slate-600 dark:text-slate-300">{currentCard.hint}</div>
                    <hr className="my-4 border-slate-300 dark:border-slate-600" id="answer" />
                    <div className="text-2xl font-bold text-slate-800 dark:text-white mb-4">
                        {currentCard.word}
                    </div>
                    <br />
                    <div className="text-slate-500 dark:text-slate-400 mb-4">
                        {currentCard.synonyms}
                    </div>
                    <br />
                    <div className="mb-4">
                        <div className="text-slate-700 dark:text-slate-200">{currentCard.ex1_ori}</div>
                        <div className="text-slate-500 dark:text-slate-400">{currentCard.ex1_trans}</div>
                    </div>
                    <br />
                    <div className="mb-4">
                        <div className="text-slate-700 dark:text-slate-200">{currentCard.ex2_ori}</div>
                        <div className="text-slate-500 dark:text-slate-400">{currentCard.ex2_trans}</div>
                    </div>
                    <br />
                    {currentCard.audio && (
                        <div className="text-sm text-slate-500">🔊 Audio: {currentCard.audio}</div>
                    )}
                </div>
            );
        }
    };

    // Render Cloze Card
    const renderClozeCard = () => {
        // Build cloze text from examples
        let clozeText = '';
        if (currentCard.ex1_ori && currentCard.ex1_ori.includes('{{c1::')) {
            // Already has cloze format
            clozeText = `${currentCard.ex1_ori}\n${currentCard.ex1_trans}`;
            if (currentCard.ex2_ori) {
                clozeText += `\n\n${currentCard.ex2_ori}\n${currentCard.ex2_trans}`;
            }
        } else {
            // Build from examples
            clozeText = `${currentCard.ex1_ori}\n${currentCard.ex1_trans}`;
            if (currentCard.ex2_ori) {
                clozeText += `\n\n${currentCard.ex2_ori}\n${currentCard.ex2_trans}`;
            }
        }
        
        // Replace cloze syntax with visible format for preview (front)
        const displayText = clozeText
            .replace(/\{\{c1::([^}]+)\}\}/g, '<span class="bg-yellow-200 dark:bg-yellow-900 px-2 py-1 rounded font-bold">[...]</span>')
            .replace(/\n/g, '<br />');
        
        // Revealed text (back)
        const revealedText = clozeText
            .replace(/\{\{c1::([^}]+)\}\}/g, '<span class="bg-green-100 dark:bg-green-900 px-2 py-1 rounded font-bold">$1</span>')
            .replace(/\n/g, '<br />');

        if (!isFlipped) {
            // Front: Cloze text with blank
            return (
                <div className="p-8">
                    <div className="text-gray-500 dark:text-gray-400 font-normal mb-2">{currentCard.pos}</div>
                    <div 
                        className="text-lg leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-line"
                        dangerouslySetInnerHTML={{ __html: displayText }}
                    />
                </div>
            );
        } else {
            // Back: Cloze text + Meaning
            return (
                <div className="p-8">
                    <div className="text-gray-500 dark:text-gray-400 font-normal mb-2">{currentCard.pos}</div>
                    <div className="text-lg font-bold text-slate-800 dark:text-white mb-4">
                        {currentCard.meaning}
                    </div>
                    <hr className="my-4 border-slate-300 dark:border-slate-600" id="answer" />
                    <div 
                        className="text-lg leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-line"
                        dangerouslySetInnerHTML={{ __html: revealedText }}
                    />
                </div>
            );
        }
    };

    return (
        <div className="flex flex-col items-center h-full w-full max-w-2xl mx-auto py-4">
            <div className="w-full flex justify-between items-center mb-4 text-slate-500 text-sm">
                <span>Card {currentIndex + 1} of {cards.length}</span>
                <div className="flex gap-2">
                    {noteType === 'basic' && (
                        <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded p-1">
                            <button
                                onClick={() => { setCardType('card1'); setIsFlipped(false); }}
                                className={`px-2 py-1 rounded text-xs ${cardType === 'card1' ? 'bg-white dark:bg-slate-700' : ''}`}
                            >
                                Card 1
                            </button>
                            <button
                                onClick={() => { setCardType('card2'); setIsFlipped(false); }}
                                className={`px-2 py-1 rounded text-xs ${cardType === 'card2' ? 'bg-white dark:bg-slate-700' : ''}`}
                            >
                                Card 2 (Reverse)
                            </button>
                        </div>
                    )}
                    <span className="font-mono bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                        {noteType === 'basic' ? 'Basic' : 'Cloze'}
                    </span>
                </div>
            </div>

            {/* Card Body */}
            <div 
                className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xl min-h-[400px] flex flex-col cursor-pointer transition-all hover:border-blue-300 dark:hover:border-blue-700 relative overflow-hidden"
                onClick={toggleFlip}
            >
                <div className="flex-1 flex flex-col p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif', fontSize: '22px' }}>
                    {noteType === 'basic' ? (
                        cardType === 'card1' ? renderBasicCard1() : renderBasicCard2()
                    ) : (
                        renderClozeCard()
                    )}
                </div>
            </div>

            {/* Controls */}
            <div className="flex gap-4 mt-6">
                <button onClick={prevCard} className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400">
                    <ChevronDown className="rotate-90" />
                </button>
                <button 
                    onClick={toggleFlip}
                    className="px-6 py-2 bg-slate-200 dark:bg-slate-800 rounded-full font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
                >
                    {isFlipped ? 'Show Front' : 'Show Back'}
                </button>
                <button onClick={nextCard} className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400">
                    <ChevronDown className="-rotate-90" />
                </button>
            </div>
        </div>
    );
};

