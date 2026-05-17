import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import type { Card } from '../types';

interface CardPreviewProps {
  data: string;
  noteType?: 'basic' | 'cloze';
}

const PosBadge = ({ pos }: { pos?: string }) =>
    pos ? (
        <span className="inline-block align-middle ml-2 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 text-sm px-2 py-0.5 rounded-md font-normal">
            {pos}
        </span>
    ) : null;

const ExampleBlock = ({ ori, trans }: { ori?: string; trans?: string }) =>
    ori ? (
        <div className="border-l-2 border-slate-200 dark:border-slate-600 pl-3 space-y-1">
            <div className="text-slate-700 dark:text-slate-200 text-base">{ori}</div>
            {trans && <div className="text-slate-500 dark:text-slate-400 text-sm">{trans}</div>}
        </div>
    ) : null;

const InfoBlock = ({ label, content, color }: { label: string; content?: string; color: 'amber' | 'purple' }) => {
    if (!content) return null;
    const styles = {
        amber: 'bg-amber-50 dark:bg-amber-900/20 border-amber-100 dark:border-amber-800/30 text-amber-600 dark:text-amber-400',
        purple: 'bg-purple-50 dark:bg-purple-900/20 border-purple-100 dark:border-purple-800/30 text-purple-600 dark:text-purple-400',
    };
    return (
        <div className={`border rounded-lg px-3 py-2 ${styles[color]}`}>
            <div className="text-xs font-semibold uppercase tracking-wide mb-1">{label}</div>
            <div className="text-slate-700 dark:text-slate-300 text-sm font-normal">{content}</div>
        </div>
    );
};

export const CardPreview: React.FC<CardPreviewProps> = ({ data, noteType = 'basic' }) => {
    const cards: Card[] = JSON.parse(data || "[]");
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);
    const [cardType, setCardType] = useState<'card1' | 'card2'>('card1');

    if (cards.length === 0) return <div className="text-slate-500 text-center py-10">No data to preview</div>;

    const currentCard = cards[currentIndex];
    const isGrammarCard = currentCard.grammar !== undefined;

    const nextCard = () => { setIsFlipped(false); setCurrentIndex((prev) => (prev + 1) % cards.length); };
    const prevCard = () => { setIsFlipped(false); setCurrentIndex((prev) => (prev - 1 + cards.length) % cards.length); };
    const toggleFlip = () => setIsFlipped(!isFlipped);

    const exampleSection = (ex1_ori?: string, ex1_trans?: string, ex2_ori?: string, ex2_trans?: string) => (
        (ex1_ori || ex2_ori) ? (
            <div className="space-y-3 pt-1">
                <ExampleBlock ori={ex1_ori} trans={ex1_trans} />
                <ExampleBlock ori={ex2_ori} trans={ex2_trans} />
            </div>
        ) : null
    );

    const renderBasicCard1 = () => {
        const front = (
            <div className="space-y-3">
                <div className="text-3xl font-bold text-slate-800 dark:text-white">
                    {currentCard.word}<PosBadge pos={currentCard.pos} />
                </div>
                {currentCard.hint && <div className="text-slate-500 dark:text-slate-400">{currentCard.hint}</div>}
                {currentCard.audio && <div className="text-sm text-slate-400">🔊 {currentCard.audio}</div>}
            </div>
        );
        const back = (
            <div className="space-y-4">
                <div className="text-3xl font-bold text-slate-800 dark:text-white">
                    {currentCard.word}<PosBadge pos={currentCard.pos} />
                </div>
                {currentCard.hint && <div className="text-slate-500 dark:text-slate-400">{currentCard.hint}</div>}
                {currentCard.audio && <div className="text-sm text-slate-400">🔊 {currentCard.audio}</div>}
                <hr className="border-slate-200 dark:border-slate-600" />
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{currentCard.meaning}</div>
                {currentCard.synonyms && <div className="text-slate-500 dark:text-slate-400 text-sm">{currentCard.synonyms}</div>}
                {exampleSection(currentCard.ex1_ori, currentCard.ex1_trans, currentCard.ex2_ori, currentCard.ex2_trans)}
            </div>
        );
        return isFlipped ? back : front;
    };

    const renderBasicCard2 = () => {
        const front = (
            <div className="space-y-3">
                <div className="text-3xl font-bold text-slate-800 dark:text-white">
                    {currentCard.meaning}<PosBadge pos={currentCard.pos} />
                </div>
                {currentCard.hint && <div className="text-slate-500 dark:text-slate-400">{currentCard.hint}</div>}
            </div>
        );
        const back = (
            <div className="space-y-4">
                <div className="text-3xl font-bold text-slate-800 dark:text-white">
                    {currentCard.meaning}<PosBadge pos={currentCard.pos} />
                </div>
                {currentCard.hint && <div className="text-slate-500 dark:text-slate-400">{currentCard.hint}</div>}
                <hr className="border-slate-200 dark:border-slate-600" />
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{currentCard.word}</div>
                {currentCard.synonyms && <div className="text-slate-500 dark:text-slate-400 text-sm">{currentCard.synonyms}</div>}
                {exampleSection(currentCard.ex1_ori, currentCard.ex1_trans, currentCard.ex2_ori, currentCard.ex2_trans)}
                {currentCard.audio && <div className="text-sm text-slate-400">🔊 {currentCard.audio}</div>}
            </div>
        );
        return isFlipped ? back : front;
    };

    const grammarFront = (heading: string) => (
        <div className="space-y-3">
            <div className="text-3xl font-bold text-slate-800 dark:text-white">{heading}</div>
            {currentCard.pattern && (
                <div className="inline-block font-mono text-base bg-slate-100 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300 px-3 py-1.5 rounded-lg">
                    {currentCard.pattern}
                </div>
            )}
            {currentCard.hint && <div className="text-slate-500 dark:text-slate-400">{currentCard.hint}</div>}
        </div>
    );

    const grammarBack = (heading: string, answer: string) => (
        <div className="space-y-4">
            <div className="text-3xl font-bold text-slate-800 dark:text-white">{heading}</div>
            {currentCard.pattern && (
                <div className="inline-block font-mono text-base bg-slate-100 dark:bg-slate-700/60 text-slate-600 dark:text-slate-300 px-3 py-1.5 rounded-lg">
                    {currentCard.pattern}
                </div>
            )}
            {currentCard.hint && <div className="text-slate-500 dark:text-slate-400">{currentCard.hint}</div>}
            <hr className="border-slate-200 dark:border-slate-600" />
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{answer}</div>
            <InfoBlock label="Usage"    content={currentCard.usage}    color="amber"  />
            <InfoBlock label="Contrast" content={currentCard.contrast} color="purple" />
            {exampleSection(currentCard.ex1_ori, currentCard.ex1_trans, currentCard.ex2_ori, currentCard.ex2_trans)}
        </div>
    );

    const renderGrammarCard1 = () =>
        isFlipped
            ? grammarBack(currentCard.grammar || '', currentCard.meaning || '')
            : grammarFront(currentCard.grammar || '');

    const renderClozeCard = () => {
        const raw = `${currentCard.ex1_ori || ''}\n${currentCard.ex1_trans || ''}${currentCard.ex2_ori ? `\n\n${currentCard.ex2_ori}\n${currentCard.ex2_trans || ''}` : ''}`;
        const displayText = raw
            .replace(/\{\{c1::([^}]+)\}\}/g, '<span class="bg-yellow-200 dark:bg-yellow-800/60 px-1.5 py-0.5 rounded font-bold text-yellow-800 dark:text-yellow-200">[...]</span>')
            .replace(/\n/g, '<br />');
        const revealedText = raw
            .replace(/\{\{c1::([^}]+)\}\}/g, '<span class="bg-green-100 dark:bg-green-900/50 px-1.5 py-0.5 rounded font-bold text-green-700 dark:text-green-300">$1</span>')
            .replace(/\n/g, '<br />');

        if (!isFlipped) {
            return (
                <div className="space-y-3">
                    {currentCard.pos && <PosBadge pos={currentCard.pos} />}
                    <div className="text-lg leading-relaxed text-slate-800 dark:text-slate-200"
                         dangerouslySetInnerHTML={{ __html: displayText }} />
                </div>
            );
        }
        return (
            <div className="space-y-4">
                {currentCard.pos && <PosBadge pos={currentCard.pos} />}
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{currentCard.meaning}</div>
                <hr className="border-slate-200 dark:border-slate-600" />
                <div className="text-lg leading-relaxed text-slate-800 dark:text-slate-200"
                     dangerouslySetInnerHTML={{ __html: revealedText }} />
            </div>
        );
    };

    return (
        <div className="flex flex-col items-center h-full w-full max-w-2xl mx-auto py-4">
            {/* Header */}
            <div className="w-full flex justify-between items-center mb-4 text-slate-500 text-sm">
                <span>Card {currentIndex + 1} of {cards.length}</span>
                <div className="flex gap-2 items-center">
                    {noteType === 'basic' && !isGrammarCard && (
                        <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
                            {(['card1', 'card2'] as const).map((t) => (
                                <button
                                    key={t}
                                    onClick={() => { setCardType(t); setIsFlipped(false); }}
                                    className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                                        cardType === t ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                                    }`}
                                >
                                    {t === 'card1' ? 'Card 1' : 'Card 2'}
                                </button>
                            ))}
                        </div>
                    )}
                    <span className="font-mono bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-xs">
                        {isGrammarCard ? 'Grammar' : noteType === 'basic' ? 'Basic' : 'Cloze'}
                    </span>
                </div>
            </div>

            {/* Card */}
            <div
                className={`w-full bg-white dark:bg-slate-800 border rounded-2xl shadow-xl min-h-[400px] flex flex-col cursor-pointer transition-all ${
                    isFlipped
                        ? 'border-blue-300 dark:border-blue-700 shadow-blue-100/50 dark:shadow-none'
                        : 'border-slate-200 dark:border-slate-700 hover:border-blue-200 dark:hover:border-blue-800'
                }`}
                onClick={toggleFlip}
            >
                <div
                    key={`${currentIndex}-${isFlipped}`}
                    className="flex-1 p-8 card-fade"
                    style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif', fontSize: '20px' }}
                >
                    {isGrammarCard
                        ? renderGrammarCard1()
                        : (noteType === 'basic'
                            ? (cardType === 'card1' ? renderBasicCard1() : renderBasicCard2())
                            : renderClozeCard())
                    }
                </div>

                {/* bottom hint */}
                <div className="px-8 pb-4 text-xs text-slate-300 dark:text-slate-600 select-none text-right">
                    {isFlipped ? 'back' : 'click to reveal'}
                </div>
            </div>

            {/* Controls */}
            <div className="flex gap-4 mt-6">
                <button onClick={prevCard} className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors">
                    <ChevronDown className="rotate-90" />
                </button>
                <button
                    onClick={toggleFlip}
                    className="px-6 py-2 bg-slate-100 dark:bg-slate-800 rounded-full font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-sm"
                >
                    {isFlipped ? 'Show Front' : 'Show Back'}
                </button>
                <button onClick={nextCard} className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors">
                    <ChevronDown className="-rotate-90" />
                </button>
            </div>
        </div>
    );
};
