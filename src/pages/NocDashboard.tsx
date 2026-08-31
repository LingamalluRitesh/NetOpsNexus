import React, { useState, useEffect } from 'react';
import {
  Activity,
  Server,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Zap,
  TrendingUp,
  RefreshCw,
  Clock,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { MetricCard } from '../components/layout/MetricCard';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const NocDashboard: React.FC = () => {
  const [overview, setOverview] = useState<Types.MonitoringOverview | null>(null);
  const [fleetHealth, setFleetHealth] = useState<Types.FleetHealthOverview | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<Types.Alert[]>([]);
  const [activeIncidents, setActiveIncidents] = useState<Types.Incident[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [ov, health, alerts, incs] = await Promise.all([
        api.getMonitoringOverview(),
        api.getFleetHealth(),
        api.getAlerts(undefined, undefined),
        api.getIncidents('open', undefined),
      ]);
      setOverview(ov);
      setFleetHealth(health);
      setRecentAlerts(alerts.slice(0, 5));
      setActiveIncidents(incs.slice(0, 4));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-950 text-cyan-400 border border-cyan-800">
              Live Operations
            </span>
            <span className="text-xs text-slate-400 font-mono">Global WAN + Data Center Fabric</span>
          </div>
          <h2 className="text-2xl font-black text-white mt-1 tracking-tight">Enterprise NOC Command Center</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time multi-site telemetry, Dijkstra topological analysis, and active automated mitigation.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono">Fleet Health Score</p>
            <p className="text-3xl font-black text-emerald-400 font-mono">
              {fleetHealth?.fleet_health_score || 94.0}%
            </p>
          </div>
          <div className="h-12 w-[1px] bg-slate-800"></div>
          <div className="text-right">
            <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono">Total Throughput</p>
            <p className="text-3xl font-black text-cyan-400 font-mono">
              {overview?.total_throughput_gbps || 38.4} <span className="text-sm font-normal text-slate-400">Gbps</span>
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Monitored Fleet"
          value={`${overview?.devices_online || 24} / ${overview?.total_devices_monitored || 24}`}
          subtitle={`${overview?.devices_critical || 0} Critical • ${overview?.devices_warning || 0} Warning`}
          statusColor="emerald"
          icon={<Server className="w-5 h-5" />}
        />
        <MetricCard
          title="Average Fleet CPU"
          value={`${overview?.average_network_cpu || 24.5}%`}
          subtitle="Memory Average: 42.1%"
          statusColor="cyan"
          icon={<Activity className="w-5 h-5" />}
        />
        <MetricCard
          title="Active Live Alarms"
          value={recentAlerts.length}
          subtitle="Threshold violations active"
          statusColor="amber"
          icon={<AlertTriangle className="w-5 h-5" />}
        />
        <MetricCard
          title="Active P1 Incidents"
          value={activeIncidents.length}
          subtitle="Mean Time to Resolve: 14.5 min"
          statusColor="rose"
          icon={<Flame className="w-5 h-5" />}
        />
      </div>

      {/* Main Double Grid: Top Interfaces & Live Alarm Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Utilized Interfaces (2 cols) */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                  <Zap className="w-4 h-4 text-cyan-400" />
                  Peak Interface Bandwidth Utilization
                </h3>
                <p className="text-xs text-slate-400">High-capacity core, spine, and WAN transit uplinks</p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 px-2.5 py-1 rounded-lg">
                Diurnal Peak
              </span>
            </div>

            <div className="space-y-4">
              {(overview?.top_utilized_interfaces || [
                { device_hostname: 'HQ-DC-CORE-01', interface_name: 'HundredGigE1/0/1', rx_mbps: 78500, tx_mbps: 84200, utilization_pct: 84.2 },
                { device_hostname: 'HQ-DC-SPINE-01', interface_name: 'FortyGigE0/1', rx_mbps: 29400, tx_mbps: 31200, utilization_pct: 78.0 },
                { device_hostname: 'SJC-CAMPUS-CORE-01', interface_name: 'TenGigabitEthernet0/1', rx_mbps: 6800, tx_mbps: 7100, utilization_pct: 71.0 },
                { device_hostname: 'LON-BRANCH-RTR-01', interface_name: 'GigabitEthernet0/0/0', rx_mbps: 620, tx_mbps: 580, utilization_pct: 62.0 },
              ]).map((iface, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="flex items-center justify-between text-xs mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white font-mono">{iface.device_hostname}</span>
                      <span className="text-slate-400 font-mono text-[11px]">{iface.interface_name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-400 font-mono text-[11px]">
                        RX: {(iface.rx_mbps / 1000).toFixed(1)} Gbps • TX: {(iface.tx_mbps / 1000).toFixed(1)} Gbps
                      </span>
                      <span className="font-extrabold text-cyan-400 font-mono">{iface.utilization_pct}%</span>
                    </div>
                  </div>
                  {/* Progress Bar */}
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        iface.utilization_pct > 80
                          ? 'bg-rose-500'
                          : iface.utilization_pct > 65
                          ? 'bg-amber-500'
                          : 'bg-cyan-500'
                      }`}
                      style={{ width: `${iface.utilization_pct}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live Alarms Feed (1 col) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Live Alarms Ticker
              </h3>
              <span className="text-[10px] font-bold text-slate-400 uppercase font-mono">Stream Active</span>
            </div>

            <div className="space-y-3">
              {recentAlerts.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-xs">
                  <CheckCircle2 className="w-8 h-8 text-emerald-500/50 mx-auto mb-2" />
                  All thresholds nominal. No active alarms.
                </div>
              ) : (
                recentAlerts.map((alert) => (
                  <div key={alert.id} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-200 font-mono">{alert.device_hostname || 'RTR-CORE'}</span>
                      <StatusBadge status={alert.severity} />
                    </div>
                    <p className="text-slate-400 text-[11px] leading-relaxed">{alert.message}</p>
                    <p className="text-[10px] text-slate-500 font-mono">
                      {new Date(alert.triggered_at).toLocaleTimeString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Active Incidents Kanban Preview */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <Flame className="w-4 h-4 text-rose-400" />
              Active Incident Tickets
            </h3>
            <p className="text-xs text-slate-400">Under active operator investigation and runbook mitigation</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {activeIncidents.length === 0 ? (
            <div className="col-span-4 p-8 text-center text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800/60">
              Zero active incidents open. Infrastructure operating smoothly.
            </div>
          ) : (
            activeIncidents.map((inc) => (
              <div key={inc.id} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-rose-400 uppercase">{inc.priority}</span>
                  <StatusBadge status={inc.status} />
                </div>
                <h4 className="font-bold text-xs text-white line-clamp-1">{inc.title}</h4>
                <p className="text-slate-400 text-[11px] line-clamp-2">{inc.description}</p>
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>Opened {new Date(inc.opened_at).toLocaleTimeString()}</span>
                  <span className="text-cyan-400">View RCA →</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
