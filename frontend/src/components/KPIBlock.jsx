import React from 'react';

export default function KPIBlock({ metrics }) {
    if (!metrics || Object.keys(metrics).length === 0) return null;
    
    const formatValue = (key, value) => {
        if (typeof value === 'number') {
            if (key.includes('value') || key.includes('pipeline')) {
                return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
            }
            if (Number.isInteger(value)) return value;
            return value.toFixed(2);
        }
        return value;
    };

    const formatLabel = (key) => {
        return key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    };

    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(metrics).map(([key, value]) => {
                if (typeof value === 'object') return null;
                
                return (
                    <div key={key} className="bg-gray-50 p-3 rounded-lg border border-gray-100 shadow-sm">
                        <div className="text-xs text-gray-500 font-medium mb-1 truncate">{formatLabel(key)}</div>
                        <div className="text-lg font-semibold text-gray-800">{formatValue(key, value)}</div>
                    </div>
                );
            })}
        </div>
    );
}
