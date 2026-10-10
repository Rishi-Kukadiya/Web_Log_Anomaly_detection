import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronDown, Check } from 'lucide-react';
import { useDashboard } from '../../context/DashboardContext';

export default function Header() {
  const { timeRange, setTimeRange, activeTab } = useDashboard();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const ranges = [
    { value: '1h', label: 'Last 1 Hour' },
    { value: '6h', label: 'Last 6 Hours' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '72h', label: 'Last 72 Hours' },
    { value: '7d', label: 'Last 7 Days' },
  ];

  const currentLabel = ranges.find(r => r.value === timeRange)?.label || 'Last 24 Hours';

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getPageMeta = () => {
    switch (activeTab) {
      case 'analytics':
        return {
          title: 'Analytics',
          subtitle: 'In-depth anomaly analysis and threat distribution patterns'
        };
      case 'settings':
        return {
          title: 'Settings',
          subtitle: 'System configuration, cluster thresholds, and alert rules'
        };
      default:
        return {
          title: 'Dashboard',
          subtitle: 'Overview of system activity and detected anomalies from web server logs'
        };
    }
  };

  const meta = getPageMeta();

  return (
    <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6">
      {/* Page Title & Description */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          {meta.title}
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          {meta.subtitle}
        </p>
      </div>

      {/* Time Range Dropdown */}
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-3 bg-white border border-slate-200 rounded-lg px-3.5 py-2 shadow-sm hover:border-slate-300 transition-all text-left"
        >
          <Calendar className="w-4 h-4 text-slate-400" />
          <div className="flex flex-col">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 leading-none">
              Time Range
            </span>
            <span className="text-xs font-semibold text-slate-800 leading-tight mt-0.5 flex items-center gap-1.5">
              {currentLabel}
              <ChevronDown className={`w-3.5 h-3.5 text-slate-500 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
            </span>
          </div>
        </button>

        {/* Dropdown Menu */}
        {dropdownOpen && (
          <div className="absolute right-0 mt-1.5 w-48 bg-white border border-slate-200 rounded-xl shadow-lg z-50 py-1 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
            {ranges.map((range) => {
              const isSelected = range.value === timeRange;
              return (
                <button
                  key={range.value}
                  onClick={() => {
                    setTimeRange(range.value);
                    setDropdownOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-3.5 py-2 text-xs font-medium text-left transition-colors ${
                    isSelected
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <span>{range.label}</span>
                  {isSelected && <Check className="w-3.5 h-3.5 text-blue-600" />}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </header>
  );
}
