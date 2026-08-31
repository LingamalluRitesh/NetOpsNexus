import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Layers,
  ArrowUpRight,
  HardDrive,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { MetricCard } from '../components/layout/MetricCard';
import { api } from '../services/api';
import * as Types from '../types';

export const CapacityPlanner: React.FC = () => {
  const [overview, setOverview] = useState<Types.CapacityOverview | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const res = await api.getCapacityOverview();
      setOverview(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-cyan-400" />
          Predictive Capacity Planning & Exhaustion Forecasts
        </h2>
        <p className="text-xs text-slate-400">
          Linear regression growth modeling projecting bandwidth, CPU, and RAM saturation milestone dates.
        </p>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          title="Monitored Resources"
          value={overview?.total_resources_analyzed || 32}
          subtitle="Interfaces, Memory, CPU, and IPAM"
          statusColor="indigo"
          icon={<Layers className="w-5 h-5" />}
        />
        <MetricCard
          title="Critical Saturation (<30d)"
          value={overview?.critical_saturation_count || 2}
          subtitle="Immediate capacity upgrades required"
          statusColor="rose"
          icon={<AlertTriangle className="w-5 h-5" />}
        />
        <MetricCard
          title="Quarterly Warnings (30-90d)"
          value={overview?.warning_saturation_count || 4}
          subtitle="Budget for next maintenance cycle"
          statusColor="amber"
          icon={<Calendar className="w-5 h-5" />}
        />
      </div>

      {/* Forecasts Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-sm text-white font-mono">Saturation Milestones & Days-to-Exhaustion</h3>
          <span className="text-xs text-slate-400 font-mono">Sorted by urgency</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="px-4 py-3">Resource / Uplink</th>
                <th className="px-4 py-3">Current Utilization</th>
                <th className="px-4 py-3">Daily Growth</th>
                <th className="px-4 py-3">Days to 80%</th>
                <th className="px-4 py-3">Projected 100% Saturation</th>
                <th className="px-4 py-3">Urgency</th>
                <th className="px-4 py-3">Engineering Action Plan</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {overview?.top_critical_forecasts.map((f, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="px-4 py-3 font-bold text-white">{f.resource_name}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${f.current_utilization_pct > 80 ? 'bg-rose-500' : 'bg-cyan-400'}`}
                          style={{ width: `${f.current_utilization_pct}%` }}
                        ></div>
                      </div>
                      <span>{f.current_utilization_pct}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-cyan-400">+{f.daily_growth_rate_pct}%/day</td>
                  <td className="px-4 py-3 text-slate-300">{f.days_to_threshold_80} days</td>
                  <td className="px-4 py-3 font-bold text-rose-300">
                    {f.projected_exhaustion_date || 'Within 45 days'}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={f.urgency_level} />
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-[11px] max-w-sm">{f.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
