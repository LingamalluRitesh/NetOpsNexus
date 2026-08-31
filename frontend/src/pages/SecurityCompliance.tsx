import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  Search,
  CheckCircle2,
  AlertTriangle,
  Play,
  Layers,
  FileCode2,
  Lock,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { MetricCard } from '../components/layout/MetricCard';
import { api } from '../services/api';
import * as Types from '../types';

export const SecurityCompliance: React.FC = () => {
  const [secOverview, setSecOverview] = useState<Types.SecurityScoreOverview | null>(null);
  const [devices, setDevices] = useState<Types.Device[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | ''>('');
  const [auditResult, setAuditResult] = useState<any>(null);
  const [isAuditing, setIsAuditing] = useState(false);

  // ACL Shadow Analysis State
  const [aclShadowResult, setAclShadowResult] = useState<any>(null);

  const loadData = async () => {
    try {
      const [ov, devs] = await Promise.all([api.getSecurityOverview(), api.getDevices()]);
      setSecOverview(ov);
      setDevices(devs);
      if (devs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(devs[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
    // Default ACL shadow sample
    handleAnalyzeAcl();
  }, []);

  const handleRunAudit = async () => {
    if (!selectedDeviceId) return;
    setIsAuditing(true);
    try {
      const res = await api.runSecurityAudit(Number(selectedDeviceId));
      setAuditResult(res);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsAuditing(false);
    }
  };

  const handleAnalyzeAcl = async () => {
    try {
      const sampleRules = [
        { sequence_num: 10, action: 'deny', protocol: 'ip', src_ip_prefix: '10.0.0.0/8', dst_ip_prefix: 'any', src_port: 'any', dst_port: 'any' },
        { sequence_num: 20, action: 'permit', protocol: 'tcp', src_ip_prefix: '10.20.0.0/16', dst_ip_prefix: 'any', src_port: 'any', dst_port: '443' },
        { sequence_num: 30, action: 'permit', protocol: 'udp', src_ip_prefix: '192.168.1.0/24', dst_ip_prefix: 'any', src_port: 'any', dst_port: '53' },
      ];
      const res = await api.analyzeAcl(1, 'EDGE-ACCESS-FILTER', sampleRules);
      setAclShadowResult(res);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Security & CIS Hardening Compliance
          </h2>
          <p className="text-xs text-slate-400">
            Automated CIS benchmark audits, ACL shadow/redundancy analysis, and rogue MAC device quarantine.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedDeviceId}
            onChange={(e) => setSelectedDeviceId(Number(e.target.value))}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            {devices.map((d) => (
              <option key={d.id} value={d.id}>
                {d.hostname} ({d.management_ip})
              </option>
            ))}
          </select>

          <button
            onClick={handleRunAudit}
            disabled={isAuditing}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white rounded-lg text-xs font-bold font-mono shadow-lg shadow-emerald-500/10 disabled:opacity-50"
          >
            {isAuditing ? 'Auditing CIS...' : 'Run Security Audit'}
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Fleet Compliance Score"
          value={`${secOverview?.overall_fleet_score || 88.5}%`}
          subtitle={`Security Grade: ${secOverview?.grade || 'B+'}`}
          statusColor="emerald"
          icon={<ShieldCheck className="w-5 h-5" />}
        />
        <MetricCard
          title="Audited Fleet"
          value={`${secOverview?.compliant_devices_count || 20} / ${secOverview?.total_devices_audited || 24}`}
          subtitle={`${secOverview?.vulnerable_devices_count || 4} require remediation`}
          statusColor="cyan"
          icon={<Lock className="w-5 h-5" />}
        />
        <MetricCard
          title="Critical Vulnerabilities"
          value={secOverview?.critical_findings_count || 2}
          subtitle="Telnet / Plaintext Passwords"
          statusColor="rose"
          icon={<ShieldAlert className="w-5 h-5" />}
        />
        <MetricCard
          title="Shadowed ACL Rules"
          value={aclShadowResult?.shadowed_rules_count || 1}
          subtitle="Unreachable firewall entries"
          statusColor="amber"
          icon={<FileCode2 className="w-5 h-5" />}
        />
      </div>

      {/* Main Double Grid: CIS Audit Findings & ACL Shadow Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CIS Benchmark Audit Findings Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              CIS Hardening Benchmark Checklist
            </h3>
            {auditResult && (
              <span className="text-xs font-mono font-bold text-emerald-400">
                Score: {auditResult.score_percent}%
              </span>
            )}
          </div>

          <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
            {(auditResult?.findings || [
              { check_id: 'CIS-1.1', title: 'AAA Authentication Model', status: 'PASS', severity: 'HIGH', description: 'AAA new-model is enabled on the device.' },
              { check_id: 'CIS-2.1', title: 'Secure Management Transport (SSH)', status: 'PASS', severity: 'HIGH', description: 'VTY lines configured for SSH only; Telnet is disabled.' },
              { check_id: 'CIS-3.1', title: 'Service Password Encryption', status: 'PASS', severity: 'MEDIUM', description: 'Cleartext password storage encryption service is enabled.' },
              { check_id: 'CIS-4.1', title: 'Default SNMP Community Strings', status: 'PASS', severity: 'HIGH', description: 'No default SNMP community strings found.' },
              { check_id: 'CIS-5.1', title: 'Remote Syslog Forwarding', status: 'PASS', severity: 'MEDIUM', description: 'Remote centralized syslog collector configured.' },
              { check_id: 'CIS-6.1', title: 'Network Time Protocol (NTP)', status: 'PASS', severity: 'LOW', description: 'Authoritative NTP time synchronization configured.' },
            ]).map((f: any, idx: number) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs font-mono space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-cyan-400">{f.check_id}</span>
                    <span className="font-bold text-white">{f.title}</span>
                  </div>
                  <StatusBadge status={f.status} />
                </div>
                <p className="text-[11px] text-slate-400">{f.description}</p>
                {f.remediation_command && (
                  <pre className="p-2 rounded bg-black/80 border border-rose-950 text-[10px] text-rose-300">
                    Fix: {f.remediation_command}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* ACL Shadow & Redundancy Matrix Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
              <FileCode2 className="w-4 h-4 text-cyan-400" />
              ACL Shadow & Overlap Analyzer
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">EDGE-ACCESS-FILTER</span>
          </div>

          <div className="space-y-3">
            {aclShadowResult?.rules?.map((rule: any) => (
              <div
                key={rule.sequence_num}
                className={`p-3.5 rounded-xl border text-xs font-mono space-y-1.5 ${
                  rule.is_shadowed
                    ? 'bg-rose-950/40 border-rose-800/80 shadow-md shadow-rose-950/20'
                    : 'bg-slate-950/60 border-slate-800/80'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-400">Seq {rule.sequence_num}</span>
                    <span className={`font-bold uppercase ${rule.action === 'permit' ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {rule.action} {rule.protocol}
                    </span>
                  </div>
                  {rule.is_shadowed && (
                    <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 text-[10px] font-bold">
                      Shadowed by Seq {rule.shadowed_by_sequence}
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-300">
                  Source: <span className="text-cyan-400">{rule.src_ip_prefix}</span> • Destination: <span className="text-cyan-400">{rule.dst_ip_prefix}</span> (Port: {rule.dst_port})
                </p>
                {rule.is_shadowed && (
                  <p className="text-[10px] text-rose-400 italic">
                    ⚠️ Rule will never be reached because parent rule #{rule.shadowed_by_sequence} matches superset traffic first.
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
