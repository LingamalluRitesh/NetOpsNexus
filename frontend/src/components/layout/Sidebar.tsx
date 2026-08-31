import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Network,
  Server,
  Radar,
  Radio,
  Binary,
  FileCode2,
  Workflow,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Activity,
  Wrench,
  TrendingUp,
  FileText,
  History,
  Users,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  badge?: number | string;
  badgeColor?: string;
}

export const Sidebar: React.FC = () => {
  const navigation: { section: string; items: NavItem[] }[] = [
    {
      section: 'NOC Command Center',
      items: [
        { name: 'Dashboard Overview', path: '/', icon: <LayoutDashboard className="w-4 h-4" /> },
        { name: 'Interactive Topology', path: '/topology', icon: <Network className="w-4 h-4" /> },
        { name: 'Live Telemetry', path: '/monitoring', icon: <Radio className="w-4 h-4" /> },
      ],
    },
    {
      section: 'Infrastructure & Control',
      items: [
        { name: 'Device Inventory', path: '/devices', icon: <Server className="w-4 h-4" /> },
        { name: 'Discovery Scanner', path: '/discovery', icon: <Radar className="w-4 h-4" /> },
        { name: 'IPAM & Subnets', path: '/ipam', icon: <Binary className="w-4 h-4" /> },
        { name: 'Config Management', path: '/configs', icon: <FileCode2 className="w-4 h-4" /> },
        { name: 'Workflow Automation', path: '/automation', icon: <Workflow className="w-4 h-4" /> },
      ],
    },
    {
      section: 'Operations & Reliability',
      items: [
        { name: 'Incident Response', path: '/incidents', icon: <Flame className="w-4 h-4" />, badge: 'P1 Live', badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30' },
        { name: 'Alert Center', path: '/alerts', icon: <AlertTriangle className="w-4 h-4" />, badge: '4', badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
        { name: 'Diagnostics Toolkit', path: '/diagnostics', icon: <Wrench className="w-4 h-4" /> },
        { name: 'Capacity Planner', path: '/capacity', icon: <TrendingUp className="w-4 h-4" /> },
      ],
    },
    {
      section: 'Security & Intelligence',
      items: [
        { name: 'Security & CIS Audit', path: '/security', icon: <ShieldCheck className="w-4 h-4" />, badge: '92%', badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
        { name: 'Traffic Intelligence', path: '/traffic', icon: <Activity className="w-4 h-4" /> },
        { name: 'Reports & Export', path: '/reports', icon: <FileText className="w-4 h-4" /> },
        { name: 'Audit Trail', path: '/audit', icon: <History className="w-4 h-4" /> },
        { name: 'RBAC Administration', path: '/rbac', icon: <Users className="w-4 h-4" /> },
      ],
    },
  ];

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-slate-950 flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Network className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-sm tracking-wider text-white flex items-center gap-1.5 font-mono">
            NETOPS <span className="text-cyan-400">NEXUS</span>
          </h1>
          <p className="text-[10px] uppercase font-bold tracking-widest text-slate-500">Carrier-Grade NOC</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6 custom-scrollbar">
        {navigation.map((sec, idx) => (
          <div key={idx}>
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 font-mono">
              {sec.section}
            </p>
            <div className="space-y-1">
              {sec.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-150 ${
                      isActive
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    {item.icon}
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${item.badgeColor || 'bg-slate-800 text-slate-400'}`}>
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-mono text-[11px]">Core Telemetry: Live</span>
          </div>
          <span className="font-mono text-[10px] text-slate-600">v2.4.0</span>
        </div>
      </div>
    </aside>
  );
};
