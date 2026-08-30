import React from 'react';
import { Sparkles } from 'lucide-react';

export default function PromptSuggestions({ onSelect }) {
    const suggestions = [
        "How is our pipeline looking?",
        "How are our ongoing projects?",
        "Give me a leadership update."
    ];
    
    return (
        <div className="flex flex-wrap gap-2 mt-4 justify-center">
            {suggestions.map((s, i) => (
                <button
                    key={i}
                    onClick={() => onSelect(s)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs font-medium text-gray-600 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                >
                    <Sparkles size={12} />
                    {s}
                </button>
            ))}
        </div>
    );
}
