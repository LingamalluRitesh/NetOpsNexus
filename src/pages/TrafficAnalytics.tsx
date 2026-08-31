import React, { useState, useEffect } from 'react';
import {
  Activity,
  ArrowUpRight,
  ArrowDownLeft,
  PieChart,
  Layers,
  Clock,
  Zap,
} from 'lucide-react';
import { MetricCard } from '../components/layout/MetricCard';
import { api } from '../services/api';
import * as Types from '../types';

export const TrafficAnalytics: React.FC = () => {
  const [windowHours, setWindowHours] = useState(24);
  const [talkers, setTalkers] = useState<Types.TopTalkersResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const res = await api.getTopTalkers(windowHours);
      setTalkers(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [windowHours]);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            NetFlow & sFlow Traffic Intelligence
          </h2>
          <p className="text-xs text-slate-400">
            Real-time flow ingestion, conversation matrix, and Top Talker bandwidth analytics.
          </p>
        </div>

        {/* Time Window Selector */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-1 rounded-lg text-xs font-mono">
          {[1, 6, 24, 168].map((h) => (
            <button
              key={h}
              onClick={() => setWindowHours(h)}
              className={`px-3 py-1 rounded-md font-bold transition-all ${
                windowHours === h ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              {h === 1 ? '1 Hour' : h === 6 ? '6 Hours' : h === 24 ? '24 Hours' : '7 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Top Talker Volumes Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Aggregated Flow Volume"
          value={`${talkers?.total_volume_gigabytes || 4.2} GB`}
          subtitle={`Analyzed over past ${windowHours} hours`}
          statusColor="cyan"
          icon={<Zap className="w-5 h-5" />}
        />
        <MetricCard
          title="Top Source Emitter"
          value={talkers?.top_sources[0]?.entity || '10.100.1.50'}
          subtitle={`${talkers?.top_sources[0]?.megabytes_total || 1840} MB (${talkers?.top_sources[0]?.percentage || 45}%)`}
          statusColor="indigo"
          icon={<ArrowUpRight className="w-5 h-5" />}
        />
        <MetricCard
          title="Top Destination Target"
          value={talkers?.top_destinations[0]?.entity || '142.250.190.46'}
          subtitle={`${talkers?.top_destinations[0]?.megabytes_total || 1450} MB (${talkers?.top_destinations[0]?.percentage || 35}%)`}
          statusColor="emerald"
          icon={<ArrowDownLeft className="w-5 h-5" />}
        />
        <MetricCard
          title="Dominant Protocol"
          value={talkers?.top_applications[0]?.entity || 'HTTPS (TCP/443)'}
          subtitle={`${talkers?.top_applications[0]?.percentage || 65}% of traffic`}
          statusColor="amber"
          icon={<PieChart className="w-5 h-5" />}
        />
      </div>

      {/* Top Talkers Tables Grid (2x2) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Source IPs */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
            <ArrowUpRight className="w-4 h-4 text-cyan-400" />
            Top Source Endpoints (Emitters)
          </h3>
          <div className="space-y-3">
            {talkers?.top_sources.map((src, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-white">{src.entity}</span>
                  <span className="text-cyan-400 font-bold">{src.megabytes_total} MB ({src.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div className="h-full bg-cyan-400" style={{ width: `${src.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Destination IPs */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
            <ArrowDownLeft className="w-4 h-4 text-emerald-400" />
            Top Destination Targets
          </h3>
          <div className="space-y-3">
            {talkers?.top_destinations.map((dst, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-white">{dst.entity}</span>
                  <span className="text-emerald-400 font-bold">{dst.megabytes_total} MB ({dst.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div className="h-full bg-emerald-400" style={{ width: `${dst.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Applications */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
            <PieChart className="w-4 h-4 text-indigo-400" />
            Application Layer Breakdown
          </h3>
          <div className="space-y-3">
            {talkers?.top_applications.map((app, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-white">{app.entity}</span>
                  <span className="text-indigo-400 font-bold">{app.megabytes_total} MB ({app.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div className="h-full bg-indigo-400" style={{ width: `${app.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Transport Protocols */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
            <Layers className="w-4 h-4 text-amber-400" />
            Transport Protocols (Layer 4)
          </h3>
          <div className="space-y-3">
            {talkers?.top_protocols.map((proto, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-white uppercase">{proto.entity}</span>
                  <span className="text-amber-400 font-bold">{proto.megabytes_total} MB ({proto.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div className="h-full bg-amber-400" style={{ width: `${proto.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
