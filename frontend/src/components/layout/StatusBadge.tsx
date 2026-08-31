import React from 'react';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const normalized = status.toLowerCase();

  let bgClass = 'bg-slate-800 text-slate-300 border-slate-700';
  let dotClass = 'bg-slate-400';

  if (['online', 'up', 'active', 'optimal', 'success', 'pass', 'excellent', 'good', 'verified', 'resolved'].includes(normalized)) {
    bgClass = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/60';
    dotClass = 'bg-emerald-400 animate-pulse';
  } else if (['warning', 'degraded', 'investigating', 'mitigating', 'silenced', 'draft', 'pending_approval', 'flagged'].includes(normalized)) {
    bgClass = 'bg-amber-950/70 text-amber-300 border-amber-800/60';
    dotClass = 'bg-amber-400';
  } else if (['critical', 'down', 'failed', 'offline', 'conflict', 'p1', 'fail', 'high'].includes(normalized)) {
    bgClass = 'bg-rose-950/70 text-rose-300 border-rose-800/60';
    dotClass = 'bg-rose-500 animate-ping';
  } else if (['maintenance', 'rolled_back', 'cancelled'].includes(normalized)) {
    bgClass = 'bg-purple-950/70 text-purple-300 border-purple-800/60';
    dotClass = 'bg-purple-400';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${bgClass} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`}></span>
      {status}
    </span>
  );
};
