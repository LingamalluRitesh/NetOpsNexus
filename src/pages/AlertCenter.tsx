import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  BellOff,
  Plus,
  Sliders,
  CheckCircle2,
  Clock,
  Shield,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const AlertCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Types.Alert[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [selectedAlertIds, setSelectedAlertIds] = useState<number[]>([]);
  const [showRuleModal, setShowRuleModal] = useState(false);

  // New Rule State
  const [ruleName, setRuleName] = useState('');
  const [metricName, setMetricName] = useState('cpu_percent');
  const [conditionOp, setConditionOp] = useState('gt');
  const [thresholdVal, setThresholdVal] = useState(85.0);
  const [severity, setSeverity] = useState('critical');

  const loadData = async () => {
    try {
      const [al, rl] = await Promise.all([api.getAlerts(), api.getAlertRules()]);
      setAlerts(al);
      setRules(rl);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAcknowledge = async (alertId?: number) => {
    const ids = alertId ? [alertId] : selectedAlertIds;
    if (ids.length === 0) return;
    try {
      await api.acknowledgeAlerts(ids);
      setSelectedAlertIds([]);
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createAlertRule({
        name: ruleName,
        metric_name: metricName,
        condition_op: conditionOp,
        threshold_value: thresholdVal,
        severity: severity,
        auto_create_incident: true,
      });
      setShowRuleModal(false);
      setRuleName('');
      await loadData();
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
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Alerting Engine & Live Alarms
          </h2>
          <p className="text-xs text-slate-400">
            Threshold evaluation rules, multi-channel alerting, batch acknowledgement, and maintenance suppression.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {selectedAlertIds.length > 0 && (
            <button
              onClick={() => handleAcknowledge()}
              className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold font-mono"
            >
              Acknowledge Selected ({selectedAlertIds.length})
            </button>
          )}

          <button
            onClick={() => setShowRuleModal(true)}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono shadow-lg shadow-cyan-500/10"
          >
            <Plus className="w-4 h-4" />
            <span>Create Alert Rule</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Active Alarms & Configured Rules */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Alarms Feed (2 cols) */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="font-bold text-sm text-white font-mono">Live Alarms Stream ({alerts.length})</h3>
            <span className="text-xs text-slate-400 font-mono">Real-time telemetry threshold triggers</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px]">
                <tr>
                  <th className="px-4 py-3">Device Hostname</th>
                  <th className="px-4 py-3">Message</th>
                  <th className="px-4 py-3">Value</th>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Triggered</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {alerts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                      Zero active alerts. System healthy.
                    </td>
                  </tr>
                ) : (
                  alerts.map((al) => (
                    <tr key={al.id} className="hover:bg-slate-800/40">
                      <td className="px-4 py-3 font-bold text-white">{al.device_hostname || 'RTR-CORE'}</td>
                      <td className="px-4 py-3 text-slate-300 max-w-xs truncate">{al.message}</td>
                      <td className="px-4 py-3 font-bold text-cyan-400">{al.metric_value}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={al.severity} />
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-[11px]">
                        {new Date(al.triggered_at).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {al.status === 'acknowledged' ? (
                          <span className="text-slate-500 text-[11px]">Acked ✓</span>
                        ) : (
                          <button
                            onClick={() => handleAcknowledge(al.id)}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded font-bold text-[11px]"
                          >
                            Ack
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

        {/* Configured Threshold Rules (1 col) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              Threshold Rules ({rules.length})
            </h3>
          </div>

          <div className="space-y-3">
            {rules.map((r) => (
              <div key={r.id} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs font-mono space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">{r.name}</span>
                  <StatusBadge status={r.severity} />
                </div>
                <p className="text-[11px] text-slate-400">
                  Condition: <span className="text-cyan-400">{r.metric_name} {r.condition_op} {r.threshold_value}</span>
                </p>
                <span className="text-[10px] text-emerald-400 font-bold block">
                  {r.auto_create_incident ? 'Auto Incident Trigger: Enabled' : 'Log Only'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Create Rule Modal */}
      {showRuleModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreateRule} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-white font-mono">Create Threshold Alert Rule</h3>
              <button type="button" onClick={() => setShowRuleModal(false)} className="text-slate-500 hover:text-white">✕</button>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Rule Name</label>
              <input
                type="text"
                value={ruleName}
                onChange={(e) => setRuleName(e.target.value)}
                placeholder="e.g. Spine Bandwidth Saturation"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Metric</label>
                <select
                  value={metricName}
                  onChange={(e) => setMetricName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                >
                  <option value="cpu_percent">CPU Utilization (%)</option>
                  <option value="memory_percent">Memory Utilization (%)</option>
                  <option value="packet_loss_percent">Packet Loss (%)</option>
                  <option value="latency_ms">Latency (ms)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Threshold</label>
                <input
                  type="number"
                  step="0.1"
                  value={thresholdVal}
                  onChange={(e) => setThresholdVal(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowRuleModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono font-bold"
              >
                Cancel
              </button>
              <button type="submit" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold">
                Save Alert Rule
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
