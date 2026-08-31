import React, { useState, useEffect } from 'react';
import {
  Server,
  Terminal,
  Activity,
  RefreshCw,
  Search,
  Filter,
  Layers,
  Cpu,
  HardDrive,
  CheckCircle2,
  ChevronRight,
  Shield,
  FileCode2,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const DeviceInventory: React.FC = () => {
  const [devices, setDevices] = useState<Types.Device[]>([]);
  const [sites, setSites] = useState<Types.Site[]>([]);
  const [selectedSite, setSelectedSite] = useState<number | ''>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDevice, setSelectedDevice] = useState<Types.Device | null>(null);

  // Terminal CLI State
  const [cliCommand, setCliCommand] = useState('show ip interface brief');
  const [cliOutput, setCliOutput] = useState('');
  const [isExecutingCli, setIsExecutingCli] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);

  const loadData = async () => {
    try {
      const [devs, s] = await Promise.all([
        api.getDevices(selectedSite ? Number(selectedSite) : undefined),
        api.getSites(),
      ]);
      setDevices(devs);
      setSites(s);
      if (devs.length > 0 && !selectedDevice) {
        setSelectedDevice(devs[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSite]);

  const handleExecuteCli = async (cmdToRun?: string) => {
    const cmd = cmdToRun || cliCommand;
    if (!selectedDevice || !cmd) return;
    setIsExecutingCli(true);
    try {
      const res = await api.executeCli(selectedDevice.id, cmd);
      setCliOutput(res.output);
    } catch (e: any) {
      setCliOutput(`Error executing command: ${e?.response?.data?.detail || e.message}`);
    } finally {
      setIsExecutingCli(false);
    }
  };

  const filteredDevices = devices.filter(
    (d) =>
      d.hostname.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.management_ip.includes(searchQuery) ||
      d.model.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <Server className="w-5 h-5 text-cyan-400" />
            Carrier-Grade Hardware Inventory
          </h2>
          <p className="text-xs text-slate-400">
            Multi-vendor physical and virtual network appliances with live SNMP/SSH device telemetry.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Filter devices..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={selectedSite}
            onChange={(e) => setSelectedSite(e.target.value ? Number(e.target.value) : '')}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Sites</option>
            {sites.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Layout: Device Table & Detail View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Device Table (2 cols) */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden flex flex-col justify-between">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="px-4 py-3">Hostname</th>
                  <th className="px-4 py-3">Management IP</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Vendor / Model</th>
                  <th className="px-4 py-3">CPU / RAM</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredDevices.map((dev) => {
                  const isSelected = selectedDevice?.id === dev.id;
                  return (
                    <tr
                      key={dev.id}
                      onClick={() => setSelectedDevice(dev)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-cyan-950/40 border-l-2 border-cyan-400' : 'hover:bg-slate-800/40'
                      }`}
                    >
                      <td className="px-4 py-3 font-bold text-white">{dev.hostname}</td>
                      <td className="px-4 py-3 text-cyan-400">{dev.management_ip}</td>
                      <td className="px-4 py-3 uppercase text-slate-400 text-[11px]">{dev.device_type}</td>
                      <td className="px-4 py-3 text-slate-300">
                        {dev.vendor} <span className="text-slate-500 font-sans">({dev.model})</span>
                      </td>
                      <td className="px-4 py-3 text-slate-300">
                        <div className="flex items-center gap-2">
                          <span>{dev.cpu_utilization.toFixed(0)}%</span>
                          <div className="w-12 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${dev.cpu_utilization > 80 ? 'bg-rose-500' : 'bg-cyan-400'}`}
                              style={{ width: `${dev.cpu_utilization}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={dev.status} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedDevice(dev);
                            setShowTerminal(true);
                            handleExecuteCli('show version');
                          }}
                          className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-[11px] text-cyan-300 font-bold"
                        >
                          CLI
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Device Deep-Dive Panel (1 col) */}
        {selectedDevice && (
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-white font-mono">{selectedDevice.hostname}</h3>
                <p className="text-xs text-cyan-400 font-mono">{selectedDevice.management_ip}</p>
              </div>
              <StatusBadge status={selectedDevice.status} />
            </div>

            {/* Hardware Specs Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs font-mono p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
              <div>
                <span className="text-slate-500 text-[10px] uppercase">Vendor</span>
                <p className="font-bold text-slate-200">{selectedDevice.vendor}</p>
              </div>
              <div>
                <span className="text-slate-500 text-[10px] uppercase">Model</span>
                <p className="font-bold text-slate-200">{selectedDevice.model}</p>
              </div>
              <div>
                <span className="text-slate-500 text-[10px] uppercase">OS Platform</span>
                <p className="font-bold text-slate-200">{selectedDevice.os_type}</p>
              </div>
              <div>
                <span className="text-slate-500 text-[10px] uppercase">OS Version</span>
                <p className="font-bold text-slate-200">{selectedDevice.os_version || '17.9.4a'}</p>
              </div>
            </div>

            {/* Interfaces List */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 font-mono">
                Port Interfaces ({selectedDevice.interfaces?.length || 0})
              </h4>
              <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                {selectedDevice.interfaces?.map((iface) => (
                  <div
                    key={iface.id}
                    className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs font-mono"
                  >
                    <div>
                      <span className="font-bold text-slate-200">{iface.name}</span>
                      <p className="text-[10px] text-slate-500">{iface.ip_address || 'Unnumbered'}</p>
                    </div>
                    <div className="text-right">
                      <StatusBadge status={iface.oper_status} />
                      <p className="text-[10px] text-slate-500 mt-0.5">{iface.speed_mbps}M {iface.duplex}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Terminal Action Bar */}
            <div className="pt-2">
              <button
                onClick={() => {
                  setShowTerminal(!showTerminal);
                  if (!cliOutput) handleExecuteCli('show ip interface brief');
                }}
                className="w-full py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/10"
              >
                <Terminal className="w-4 h-4" />
                <span>{showTerminal ? 'Hide Terminal' : 'Open SSH Terminal CLI'}</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Terminal CLI Modal / Drawer */}
      {showTerminal && selectedDevice && (
        <div className="rounded-2xl border border-cyan-500/40 bg-slate-950 p-5 shadow-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold text-white font-mono">
                SSH Terminal Session: {selectedDevice.hostname} ({selectedDevice.management_ip}:22)
              </span>
            </div>

            {/* Quick Command Buttons */}
            <div className="flex items-center gap-2">
              {['show ip route', 'show bgp summary', 'show running-config', 'show version'].map((quickCmd) => (
                <button
                  key={quickCmd}
                  onClick={() => {
                    setCliCommand(quickCmd);
                    handleExecuteCli(quickCmd);
                  }}
                  className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded text-[11px] font-mono"
                >
                  {quickCmd}
                </button>
              ))}
            </div>
          </div>

          {/* Terminal Console Output */}
          <div className="bg-black/90 p-4 rounded-xl border border-slate-800 font-mono text-xs text-emerald-400 h-80 overflow-y-auto whitespace-pre-wrap leading-relaxed">
            {isExecutingCli ? (
              <div className="flex items-center gap-2 text-cyan-400">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Executing on device adapter...</span>
              </div>
            ) : (
              cliOutput || 'Enter command below and press Run...'
            )}
          </div>

          {/* Terminal Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleExecuteCli();
            }}
            className="flex items-center gap-3"
          >
            <span className="text-cyan-400 font-mono font-bold text-xs">{selectedDevice.hostname}#</span>
            <input
              type="text"
              value={cliCommand}
              onChange={(e) => setCliCommand(e.target.value)}
              placeholder="Enter Cisco IOS / Junos CLI command..."
              className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              disabled={isExecutingCli}
              className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-bold font-mono transition-all disabled:opacity-50"
            >
              Run
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
