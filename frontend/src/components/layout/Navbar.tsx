import React, { useState } from 'react';
import { Search, Bell, Shield, Radio, RefreshCw, Terminal, Download, Globe } from 'lucide-react';
import { api } from '../../services/api';

interface NavbarProps {
  onQuickAction?: (action: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onQuickAction }) => {
  const [isPolling, setIsPolling] = useState(false);

  const handlePollNow = async () => {
    setIsPolling(true);
    try {
      await api.triggerPollCycle();
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => setIsPolling(false), 800);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      await api.downloadExecutivePdf();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md flex items-center justify-between px-6 z-10">
      {/* Search Input */}
      <div className="flex items-center gap-3 w-96">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search hostnames, IPs, subnets, alerts, or ACLs (Ctrl+K)..."
            className="w-full pl-9 pr-4 py-1.5 bg-slate-900/90 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30 transition-all font-mono"
          />
        </div>
      </div>

      {/* Action Controls & User Profile */}
      <div className="flex items-center gap-3">
        {/* Quick Poll Button */}
        <button
          onClick={handlePollNow}
          disabled={isPolling}
          title="Trigger instantaneous SNMP/SSH telemetry poll cycle across all devices"
          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-lg text-xs font-semibold transition-all shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isPolling ? 'animate-spin text-cyan-400' : 'text-slate-400'}`} />
          <span>{isPolling ? 'Polling Fleet...' : 'Poll Telemetry'}</span>
        </button>

        {/* Export PDF Executive Summary */}
        <button
          onClick={handleDownloadPdf}
          title="Download Carrier-Grade PDF Executive Intelligence Report"
          className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-800/60 text-cyan-300 rounded-lg text-xs font-semibold transition-all shadow-sm"
        >
          <Download className="w-3.5 h-3.5 text-cyan-400" />
          <span>Export PDF Report</span>
        </button>

        {/* Telemetry Stream Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>NOC WebSocket Stream</span>
        </div>

        {/* User Badge */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-md">
            NA
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-bold text-slate-200">Network Admin</p>
            <p className="text-[10px] text-cyan-400 font-mono">super_admin</p>
          </div>
        </div>
      </div>
    </header>
  );
};
