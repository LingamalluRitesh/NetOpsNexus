import React from 'react';
import {
  Users,
  Shield,
  CheckCircle2,
  Lock,
  Key,
  ShieldAlert,
} from 'lucide-react';

export const RbacAdmin: React.FC = () => {
  const roles = [
    { name: 'super_admin', label: 'Super Administrator', desc: 'Full unrestricted root authority across all resources, RBAC roles, and audits.', color: 'text-rose-400' },
    { name: 'network_admin', label: 'Network Administrator', desc: 'Full infrastructure control, staged config rollouts, and rollback permissions.', color: 'text-cyan-400' },
    { name: 'network_engineer', label: 'Network Engineer', desc: 'Device provisioning, discovery scans, IPAM allocation, and automation executions.', color: 'text-indigo-400' },
    { name: 'security_engineer', label: 'Security Engineer', desc: 'CIS benchmark audits, ACL shadow analysis, and rogue MAC device quarantine.', color: 'text-emerald-400' },
    { name: 'noc_engineer', label: 'NOC Engineer', desc: 'Telemetry monitoring, diagnostics toolkit, alert acknowledgement, and incident triage.', color: 'text-amber-400' },
    { name: 'auditor', label: 'Compliance Auditor', desc: 'Read-only access to audit logs, configuration diffs, and executive PDF reports.', color: 'text-purple-400' },
    { name: 'read_only', label: 'Read Only Observer', desc: 'Global read-only access to topology maps, telemetry dashboards, and device inventory.', color: 'text-slate-400' },
  ];

  const permissionMatrix = [
    { scope: 'Device Management', read: ['super_admin', 'network_admin', 'network_engineer', 'security_engineer', 'noc_engineer', 'auditor', 'read_only'], write: ['super_admin', 'network_admin', 'network_engineer'] },
    { scope: 'Network Discovery', read: ['super_admin', 'network_admin', 'network_engineer', 'noc_engineer'], write: ['super_admin', 'network_admin', 'network_engineer'] },
    { scope: 'Topology Engine', read: ['super_admin', 'network_admin', 'network_engineer', 'security_engineer', 'noc_engineer', 'auditor', 'read_only'], write: ['super_admin', 'network_admin'] },
    { scope: 'Telemetry & Monitoring', read: ['super_admin', 'network_admin', 'network_engineer', 'security_engineer', 'noc_engineer', 'auditor', 'read_only'], write: ['super_admin', 'network_admin', 'noc_engineer'] },
    { scope: 'IP Address Management', read: ['super_admin', 'network_admin', 'network_engineer', 'noc_engineer', 'auditor', 'read_only'], write: ['super_admin', 'network_admin', 'network_engineer'] },
    { scope: 'Configuration Backups', read: ['super_admin', 'network_admin', 'network_engineer', 'auditor'], write: ['super_admin', 'network_admin', 'network_engineer'] },
    { scope: 'Staged Config Rollout', read: ['super_admin', 'network_admin', 'auditor'], write: ['super_admin', 'network_admin'] },
    { scope: 'Atomic Rollback', read: ['super_admin', 'network_admin'], write: ['super_admin', 'network_admin'] },
    { scope: 'Automation DAG Workflows', read: ['super_admin', 'network_admin', 'network_engineer', 'noc_engineer'], write: ['super_admin', 'network_admin', 'network_engineer'] },
    { scope: 'Incident Operations', read: ['super_admin', 'network_admin', 'network_engineer', 'security_engineer', 'noc_engineer', 'auditor'], write: ['super_admin', 'network_admin', 'network_engineer', 'noc_engineer'] },
    { scope: 'Alert Engine & Ack', read: ['super_admin', 'network_admin', 'network_engineer', 'security_engineer', 'noc_engineer'], write: ['super_admin', 'network_admin', 'noc_engineer'] },
    { scope: 'CIS Security Benchmark', read: ['super_admin', 'security_engineer', 'auditor'], write: ['super_admin', 'security_engineer'] },
    { scope: 'Traffic Flow Analytics', read: ['super_admin', 'network_admin', 'network_engineer', 'security_engineer', 'noc_engineer'], write: ['super_admin', 'network_admin'] },
    { scope: 'Audit Trail Ledger', read: ['super_admin', 'auditor'], write: ['super_admin'] },
    { scope: 'RBAC Role Management', read: ['super_admin'], write: ['super_admin'] },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
          <Shield className="w-5 h-5 text-cyan-400" />
          7-Role Granular RBAC Permissions Matrix
        </h2>
        <p className="text-xs text-slate-400">
          Role-Based Access Control security architecture enforcing strict operational boundaries across 15 scopes.
        </p>
      </div>

      {/* Roles Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {roles.slice(0, 4).map((r) => (
          <div key={r.name} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2">
              <Key className={`w-4 h-4 ${r.color}`} />
              <span className={`font-mono text-xs font-bold ${r.color}`}>{r.label}</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">{r.desc}</p>
          </div>
        ))}
      </div>

      {/* Permissions Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-sm text-white font-mono">Scope-to-Role Authorization Matrix</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
              <tr>
                <th className="px-4 py-3">Operational Scope</th>
                <th className="px-4 py-3">Read Authority</th>
                <th className="px-4 py-3">Write / Execute Authority</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {permissionMatrix.map((p, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="px-4 py-3 font-bold text-white">{p.scope}</td>
                  <td className="px-4 py-3 text-slate-400">
                    <div className="flex flex-wrap gap-1.5">
                      {p.read.map((r) => (
                        <span key={r} className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] text-slate-300">
                          {r}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1.5">
                      {p.write.map((r) => (
                        <span key={r} className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-[10px] text-cyan-300 font-bold">
                          {r}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
