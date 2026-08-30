import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import Message from './Message';
import PromptSuggestions from './PromptSuggestions';
import { sendMessage } from '../services/api';

export default function Chat() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello. I am the Skylark BI Agent. I can help you analyze pipeline health, project execution, and generate leadership updates based on Monday.com data.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (text) => {
        const query = text || input;
        if (!query.trim()) return;

        const userMsg = { role: 'user', content: query };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const data = await sendMessage(query);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.answer,
                metrics: data.metrics,
                warnings: data.warnings,
                sources: data.sources
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Error: ${error.message}`
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-100px)] max-w-4xl mx-auto bg-gray-50/50 rounded-2xl border border-gray-200 overflow-hidden shadow-xl">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-gray-800">Skylark BI Agent</h1>
                    <p className="text-sm text-gray-500">Ask questions across Deals and Work Orders</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <span className="text-xs font-medium text-gray-600">API Connected</span>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
                {messages.map((m, i) => (
                    <Message key={i} message={m} />
                ))}
                
                {isLoading && (
                    <div className="flex items-center gap-2 text-gray-500 ml-12">
                        <Loader2 className="animate-spin" size={16} />
                        <span className="text-sm font-medium">Agent is analyzing data...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-200">
                {messages.length === 1 && (
                    <div className="mb-4">
                        <PromptSuggestions onSelect={handleSend} />
                    </div>
                )}
                
                <form 
                    onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                    className="flex items-center relative"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about pipeline, deals, or projects..."
                        className="w-full bg-gray-100 border-transparent focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 rounded-full py-4 pl-6 pr-14 text-sm transition-all outline-none"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="absolute right-2 p-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white rounded-full transition-colors flex items-center justify-center h-10 w-10"
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
}
