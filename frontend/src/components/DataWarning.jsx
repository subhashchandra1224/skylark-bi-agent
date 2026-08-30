import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function DataWarning({ warnings }) {
    if (!warnings || warnings.length === 0) return null;
    
    return (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
            <div className="flex items-center gap-2 font-semibold mb-2 text-amber-900">
                <AlertTriangle size={16} />
                <span>Data Quality Warnings</span>
            </div>
            <ul className="list-disc pl-5 space-y-1">
                {warnings.map((w, i) => (
                    <li key={i}>{w}</li>
                ))}
            </ul>
        </div>
    );
}
