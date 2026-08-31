import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Shield,
  Clock,
  User,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';
import * as Types from '../types';

export const AuditTrail: React.FC = () => {
  const [logs, setLogs] = useState<Types.AuditLog[]>([]);
  const [resourceFilter, setResourceFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const loadLogs = async () => {
    try {
      const l = await api.getAuditLogs(resourceFilter || undefined);
      setLogs(l);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [resourceFilter]);

  const filteredLogs = logs.filter(
    (l) =>
      l.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.resource_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            Immutable Compliance & Security Audit Trail
          </h2>
          <p className="text-xs text-slate-400">
            Cryptographic ledger tracking all operator logins, configuration deployments, rollbacks, and workflow executions.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search audit trail..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={resourceFilter}
            onChange={(e) => setResourceFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Resources</option>
            <option value="config">Configurations (NCM)</option>
            <option value="device">Devices</option>
            <option value="workflow">Automation Workflows</option>
            <option value="incident">Incidents</option>
            <option value="rbac">RBAC & Roles</option>
          </select>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="px-4 py-3">Timestamp (UTC)</th>
                <th className="px-4 py-3">Operator</th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">Resource Type</th>
                <th className="px-4 py-3">Target ID</th>
                <th className="px-4 py-3">Client IP</th>
                <th className="px-4 py-3">Details Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    No matching audit records found.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40">
                    <td className="px-4 py-3 text-slate-400">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-3 font-bold text-white flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-cyan-400" />
                      {log.username}
                    </td>
                    <td className="px-4 py-3 text-cyan-300 font-bold uppercase text-[11px]">{log.action}</td>
                    <td className="px-4 py-3 uppercase text-slate-400 text-[11px]">{log.resource_type}</td>
                    <td className="px-4 py-3 text-slate-400">{log.resource_id || 'N/A'}</td>
                    <td className="px-4 py-3 text-slate-500">{log.ip_address || '127.0.0.1'}</td>
                    <td className="px-4 py-3 text-slate-400 text-[11px] max-w-xs truncate">
                      {JSON.stringify(log.details)}
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
