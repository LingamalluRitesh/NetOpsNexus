import React, { useState, useEffect } from 'react';
import {
  Radar,
  Play,
  CheckCircle2,
  AlertCircle,
  Plus,
  RefreshCw,
  Search,
  Server,
  Layers,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const DiscoveryScanner: React.FC = () => {
  const [subnetInput, setSubnetInput] = useState('10.100.0.0/24');
  const [scanType, setScanType] = useState('comprehensive');
  const [scanName, setScanName] = useState('HQ Data Center Discovery Sweep');
  const [isScanning, setIsScanning] = useState(false);
  const [jobs, setJobs] = useState<any[]>([]);
  const [discoveredDevices, setDiscoveredDevices] = useState<any[]>([]);
  const [importingId, setImportingId] = useState<number | null>(null);

  const loadData = async () => {
    try {
      const [j, devs] = await Promise.all([api.getScanJobs(), api.getDiscoveredDevices()]);
      setJobs(j);
      setDiscoveredDevices(devs);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsScanning(true);
    try {
      await api.startScan({
        name: scanName,
        scan_type: scanType,
        target_subnet: subnetInput,
        ports: [22, 23, 80, 443, 161, 179],
        snmp_communities: ['public', 'netops_ro', 'nexus_snmp_v2'],
      });
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsScanning(false);
    }
  };

  const handleImport = async (devId: number) => {
    setImportingId(devId);
    try {
      await api.importDiscoveredDevice(devId);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setImportingId(null);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
          <Radar className="w-5 h-5 text-cyan-400" />
          Multi-Protocol Network Discovery Engine
        </h2>
        <p className="text-xs text-slate-400">
          Probe subnets with ICMP, TCP SYN port sweeps, SNMP sysDescr extraction, and LLDP/CDP neighbor crawling.
        </p>
      </div>

      {/* Discovery Launcher Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5">
        <form onSubmit={handleStartScan} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Scan Job Name</label>
            <input
              type="text"
              value={scanName}
              onChange={(e) => setScanName(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Target Subnet (CIDR)</label>
            <input
              type="text"
              value={subnetInput}
              onChange={(e) => setSubnetInput(e.target.value)}
              placeholder="e.g. 10.100.0.0/24"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Discovery Protocol</label>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            >
              <option value="comprehensive">Comprehensive (ICMP + TCP + SNMP + Neighbors)</option>
              <option value="icmp_ping">ICMP Ping Sweep Only</option>
              <option value="tcp_syn">TCP Port Sweep (22, 80, 443, 179)</option>
              <option value="snmp_walk">SNMP v2c/v3 MIB Walk</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={isScanning}
              className="w-full py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/10 disabled:opacity-50"
            >
              {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>{isScanning ? 'Probing Subnet...' : 'Launch Discovery Scan'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Discovered Devices Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-sm text-white font-mono flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            Discovered Infrastructure Appliances ({discoveredDevices.length})
          </h3>
          <span className="text-xs text-slate-400 font-mono">1-Click Import into Active Inventory</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="px-4 py-3">IP Address</th>
                <th className="px-4 py-3">Discovered Hostname</th>
                <th className="px-4 py-3">MAC / OUI</th>
                <th className="px-4 py-3">Vendor / OS Fingerprint</th>
                <th className="px-4 py-3">Open Ports</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {discoveredDevices.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    No discovery scan results yet. Launch a scan above.
                  </td>
                </tr>
              ) : (
                discoveredDevices.map((dev) => (
                  <tr key={dev.id} className="hover:bg-slate-800/40">
                    <td className="px-4 py-3 font-bold text-cyan-400">{dev.ip_address}</td>
                    <td className="px-4 py-3 font-bold text-white">{dev.hostname || 'Unresolved'}</td>
                    <td className="px-4 py-3 text-slate-400">{dev.mac_address || 'N/A'}</td>
                    <td className="px-4 py-3 text-slate-300">
                      {dev.vendor || 'Generic'} • {dev.os_type || 'Unknown'}
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-[11px]">
                      {Array.isArray(dev.open_ports) ? dev.open_ports.join(', ') : '22, 161'}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={dev.is_imported ? 'online' : 'warning'} />
                    </td>
                    <td className="px-4 py-3 text-right">
                      {dev.is_imported ? (
                        <span className="text-emerald-400 text-[11px] font-bold">Imported ✓</span>
                      ) : (
                        <button
                          onClick={() => handleImport(dev.id)}
                          disabled={importingId === dev.id}
                          className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold"
                        >
                          {importingId === dev.id ? 'Importing...' : 'Import to Inventory'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
