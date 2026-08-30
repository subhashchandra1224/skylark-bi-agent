import React from 'react';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import KPIBlock from './KPIBlock';
import DataWarning from './DataWarning';

export default function Message({ message }) {
    const isUser = message.role === 'user';
    
    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center mr-3 mt-1">
                    <Bot size={18} className="text-white" />
                </div>
            )}
            
            <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-5 py-4 shadow-sm
                ${isUser ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-gray-100 rounded-tl-none'}
            `}>
                <div className={`leading-relaxed text-sm ${isUser ? 'text-white' : 'text-gray-800'}`}>
                    {isUser ? (
                        <div className="whitespace-pre-wrap">{message.content}</div>
                    ) : (
                        <div className="prose prose-sm prose-indigo max-w-none">
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                    )}
                </div>
                
                {!isUser && message.metrics && Object.keys(message.metrics).length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-100">
                        <KPIBlock metrics={message.metrics} />
                    </div>
                )}
                
                {!isUser && message.warnings && message.warnings.length > 0 && (
                    <div className="mt-4">
                        <DataWarning warnings={message.warnings} />
                    </div>
                )}
                
                {!isUser && message.sources && message.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-100 flex items-center gap-2 text-xs text-gray-400">
                        <span className="font-medium">Sources:</span>
                        {message.sources.map((src, i) => (
                            <span key={i} className="px-2 py-1 bg-gray-50 rounded-md border border-gray-100">
                                {src}
                            </span>
                        ))}
                    </div>
                )}
            </div>
            
            {isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-700 flex items-center justify-center ml-3 mt-1">
                    <User size={18} className="text-white" />
                </div>
            )}
        </div>
    );
}
