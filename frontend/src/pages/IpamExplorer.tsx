import React, { useState, useEffect } from 'react';
import {
  Binary,
  Plus,
  Split,
  Calculator,
  AlertOctagon,
  Search,
  CheckCircle2,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const IpamExplorer: React.FC = () => {
  const [subnets, setSubnets] = useState<Types.Subnet[]>([]);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [selectedSubnet, setSelectedSubnet] = useState<Types.Subnet | null>(null);

  // CIDR Calculator State
  const [calcInput, setCalcInput] = useState('10.20.10.0/24');
  const [calcResult, setCalcResult] = useState<any>(null);

  // Split Modal State
  const [showSplitModal, setShowSplitModal] = useState(false);
  const [targetPrefix, setTargetPrefix] = useState(25);
  const [isSplitting, setIsSplitting] = useState(false);

  // Create Subnet State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newSubnetName, setNewSubnetName] = useState('');
  const [newNetAddr, setNewNetAddr] = useState('10.40.0.0');
  const [newPrefix, setNewPrefix] = useState(24);

  const loadData = async () => {
    try {
      const [s, c] = await Promise.all([api.getSubnets(), api.getConflicts()]);
      setSubnets(s);
      setConflicts(c);
      if (s.length > 0 && !selectedSubnet) {
        setSelectedSubnet(s[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
    handleCalculateCidr('10.20.10.0/24');
  }, []);

  const handleCalculateCidr = async (cidrToCalc?: string) => {
    const c = cidrToCalc || calcInput;
    try {
      const res = await api.calculateCidr(c);
      setCalcResult(res);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSplitSubnet = async () => {
    if (!selectedSubnet) return;
    setIsSplitting(true);
    try {
      await api.splitSubnet(selectedSubnet.id, targetPrefix);
      setShowSplitModal(false);
      await loadData();
    } catch (e: any) {
      alert(`Split error: ${e?.response?.data?.detail || e.message}`);
    } finally {
      setIsSplitting(false);
    }
  };

  const handleCreateSubnet = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createSubnet({
        name: newSubnetName,
        network_address: newNetAddr,
        prefix_len: newPrefix,
        ip_version: 4,
      });
      setShowCreateModal(false);
      setNewSubnetName('');
      await loadData();
    } catch (e: any) {
      alert(`Create error: ${e?.response?.data?.detail || e.message}`);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <Binary className="w-5 h-5 text-cyan-400" />
            Enterprise IP Address Management (IPAM)
          </h2>
          <p className="text-xs text-slate-400">
            IPv4/IPv6 hierarchical address planner, dynamic CIDR calculator, subnet splitting/merging, and collision detection.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono shadow-lg shadow-cyan-500/10"
        >
          <Plus className="w-4 h-4" />
          <span>New Subnet Block</span>
        </button>
      </div>

      {/* CIDR Calculator Interactive Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
            <Calculator className="w-4 h-4 text-cyan-400" />
            Interactive CIDR & Netmask Calculator
          </h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleCalculateCidr();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={calcInput}
              onChange={(e) => setCalcInput(e.target.value)}
              placeholder="e.g. 10.20.10.0/24"
              className="px-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500 w-48"
            />
            <button type="submit" className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-bold font-mono">
              Calculate
            </button>
          </form>
        </div>

        {calcResult && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 text-xs font-mono p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Network Address</span>
              <p className="font-bold text-white">{calcResult.network_address}</p>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Netmask</span>
              <p className="font-bold text-cyan-400">{calcResult.netmask}</p>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Wildcard Mask</span>
              <p className="font-bold text-slate-300">{calcResult.wildcard_mask}</p>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Usable Host Range</span>
              <p className="font-bold text-slate-200">
                {calcResult.first_usable_ip} - {calcResult.last_usable_ip}
              </p>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Total / Usable Hosts</span>
              <p className="font-bold text-emerald-400">
                {calcResult.usable_hosts} hosts (/{calcResult.prefix_len})
              </p>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Broadcast IP</span>
              <p className="font-bold text-slate-300">{calcResult.broadcast_address}</p>
            </div>
          </div>
        )}
      </div>

      {/* Main IPAM Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Subnets List Table (2 cols) */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="font-bold text-sm text-white font-mono">Managed Subnets ({subnets.length})</h3>
            <span className="text-xs text-slate-400 font-mono">Click subnet to inspect allocations</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="px-4 py-3">Subnet Name</th>
                  <th className="px-4 py-3">CIDR Block</th>
                  <th className="px-4 py-3">Gateway</th>
                  <th className="px-4 py-3">Utilization</th>
                  <th className="px-4 py-3">Allocated / Total</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {subnets.map((sub) => {
                  const isSelected = selectedSubnet?.id === sub.id;
                  return (
                    <tr
                      key={sub.id}
                      onClick={() => setSelectedSubnet(sub)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? 'bg-cyan-950/40 border-l-2 border-cyan-400' : 'hover:bg-slate-800/40'
                      }`}
                    >
                      <td className="px-4 py-3 font-bold text-white">{sub.name}</td>
                      <td className="px-4 py-3 text-cyan-400">
                        {sub.network_address}/{sub.prefix_len}
                      </td>
                      <td className="px-4 py-3 text-slate-400">{sub.gateway_ip || 'N/A'}</td>
                      <td className="px-4 py-3 text-slate-300">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-cyan-400"
                              style={{ width: `${Math.max(4, sub.utilization_pct)}%` }}
                            ></div>
                          </div>
                          <span>{sub.utilization_pct}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-slate-300">
                        {sub.used_ips + sub.reserved_ips} / {sub.total_ips}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedSubnet(sub);
                            setTargetPrefix(sub.prefix_len + 1);
                            setShowSplitModal(true);
                          }}
                          className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-[11px] text-cyan-300 font-bold flex items-center gap-1 ml-auto"
                        >
                          <Split className="w-3 h-3" />
                          <span>Split</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Subnet Breakdown & Conflicts (1 col) */}
        <div className="space-y-6">
          {selectedSubnet && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
              <div>
                <h3 className="font-bold text-sm text-white font-mono">{selectedSubnet.name}</h3>
                <p className="text-xs text-cyan-400 font-mono">
                  {selectedSubnet.network_address}/{selectedSubnet.prefix_len}
                </p>
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-500">Total Capacity:</span>
                  <span className="text-white font-bold">{selectedSubnet.total_ips} IPs</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-500">Available Pool:</span>
                  <span className="text-emerald-400 font-bold">{selectedSubnet.available_ips} IPs</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                  <span className="text-slate-500">Default Gateway:</span>
                  <span className="text-slate-200">{selectedSubnet.gateway_ip}</span>
                </div>
              </div>
            </div>
          )}

          {/* Conflicts Feed */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-3">
            <h4 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-rose-400" />
              IP Collision Conflicts ({conflicts.length})
            </h4>

            {conflicts.length === 0 ? (
              <p className="text-xs text-slate-500">No duplicate IP assignments detected across subnets.</p>
            ) : (
              conflicts.map((conf) => (
                <div key={conf.id} className="p-3 rounded-lg bg-rose-950/40 border border-rose-800 text-xs font-mono space-y-1">
                  <span className="font-bold text-rose-300">{conf.ip_address}</span>
                  <p className="text-[11px] text-slate-400">
                    Duplicate MAC collision: {conf.conflicting_macs?.join(' vs ')}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Subnet Split Modal */}
      {showSplitModal && selectedSubnet && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-white font-mono">Split Subnet Block</h3>
              <button onClick={() => setShowSplitModal(false)} className="text-slate-500 hover:text-white">
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Splitting <span className="text-cyan-400 font-mono">{selectedSubnet.network_address}/{selectedSubnet.prefix_len}</span> into smaller contiguous prefixes.
            </p>

            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">
                Target Prefix Length
              </label>
              <select
                value={targetPrefix}
                onChange={(e) => setTargetPrefix(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
              >
                {[selectedSubnet.prefix_len + 1, selectedSubnet.prefix_len + 2, selectedSubnet.prefix_len + 3].map((p) => (
                  <option key={p} value={p}>
                    /{p} ({Math.pow(2, 32 - p)} IPs per subnet, {Math.pow(2, p - selectedSubnet.prefix_len)} child blocks)
                  </option>
                ))}
              </select>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setShowSplitModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono font-bold"
              >
                Cancel
              </button>
              <button
                onClick={handleSplitSubnet}
                disabled={isSplitting}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold"
              >
                {isSplitting ? 'Splitting...' : 'Confirm Split'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Subnet Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreateSubnet} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-white font-mono">Create New Subnet Block</h3>
              <button type="button" onClick={() => setShowCreateModal(false)} className="text-slate-500 hover:text-white">
                ✕
              </button>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Subnet Name</label>
              <input
                type="text"
                value={newSubnetName}
                onChange={(e) => setNewSubnetName(e.target.value)}
                placeholder="e.g. DMZ Web Server Tier"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Network IP</label>
                <input
                  type="text"
                  value={newNetAddr}
                  onChange={(e) => setNewNetAddr(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Prefix /</label>
                <input
                  type="number"
                  min={8}
                  max={30}
                  value={newPrefix}
                  onChange={(e) => setNewPrefix(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono font-bold"
              >
                Cancel
              </button>
              <button type="submit" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold">
                Create Subnet
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
