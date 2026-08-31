import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: string;
  trendPositive?: boolean;
  icon?: React.ReactNode;
  statusColor?: 'emerald' | 'cyan' | 'amber' | 'rose' | 'indigo';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendPositive,
  icon,
  statusColor = 'indigo',
}) => {
  const colorMap = {
    emerald: 'from-emerald-500/10 to-transparent border-emerald-500/20 text-emerald-400',
    cyan: 'from-cyan-500/10 to-transparent border-cyan-500/20 text-cyan-400',
    amber: 'from-amber-500/10 to-transparent border-amber-500/20 text-amber-400',
    rose: 'from-rose-500/10 to-transparent border-rose-500/20 text-rose-400',
    indigo: 'from-indigo-500/10 to-transparent border-indigo-500/20 text-indigo-400',
  };

  return (
    <div className={`relative overflow-hidden rounded-xl border bg-gradient-to-b bg-slate-900/90 backdrop-blur-md p-5 transition-all duration-200 hover:border-slate-700 ${colorMap[statusColor]}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {icon && <div className="p-2 rounded-lg bg-slate-800/80 text-slate-300">{icon}</div>}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-black tracking-tight text-white font-mono">{value}</span>
        {trend && (
          <span className={`text-xs font-bold ${trendPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {trend}
          </span>
        )}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-500 font-medium">{subtitle}</p>}
    </div>
  );
};
