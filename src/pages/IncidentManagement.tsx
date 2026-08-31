import React, { useState, useEffect } from 'react';
import {
  Flame,
  Plus,
  Clock,
  UserCheck,
  CheckCircle2,
  AlertTriangle,
  FileText,
  MessageSquare,
  Shield,
  Layers,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const IncidentManagement: React.FC = () => {
  const [incidents, setIncidents] = useState<Types.Incident[]>([]);
  const [mttrData, setMttrData] = useState<any>(null);
  const [selectedIncident, setSelectedIncident] = useState<Types.Incident | null>(null);
  const [commentInput, setCommentInput] = useState('');
  const [showRcaModal, setShowRcaModal] = useState(false);
  const [rcaRootCause, setRcaRootCause] = useState('');
  const [rcaPreventative, setRcaPreventative] = useState('');

  const loadData = async () => {
    try {
      const [incs, mttr] = await Promise.all([api.getIncidents(), api.getMttrAnalytics()]);
      setIncidents(incs);
      setMttrData(mttr);
      if (incs.length > 0 && !selectedIncident) {
        setSelectedIncident(incs[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident || !commentInput) return;
    try {
      // Refresh
      await api.resolveIncident(selectedIncident.id, commentInput);
      setCommentInput('');
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateRca = async () => {
    if (!selectedIncident) return;
    try {
      await api.generateRca(selectedIncident.id, {
        root_cause_summary: rcaRootCause || 'Hardware transceiver link flap during peak traffic.',
        impacted_services: ['WAN Edge Routing'],
        remediation_steps_taken: ['Replaced fiber SFP+ module', 'Reset BGP peering session'],
        preventative_actions: [rcaPreventative || 'Deploy optical power alert rule with 5-minute hysteresis'],
      });
      setShowRcaModal(false);
      await loadData();
      alert('RCA Document generated successfully!');
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
            <Flame className="w-5 h-5 text-rose-400" />
            Carrier Incident Management & RCA Engine
          </h2>
          <p className="text-xs text-slate-400">
            Lifecycle triage, engineer assignment, timeline investigation events, and Root Cause Analysis (RCA) post-mortems.
          </p>
        </div>

        {/* SLA MTTR Summary Card */}
        {mttrData && (
          <div className="flex items-center gap-4 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Mean Time to Resolve</span>
              <p className="font-bold text-emerald-400">{mttrData.mean_time_to_resolution_minutes} min</p>
            </div>
            <div className="h-8 w-[1px] bg-slate-800"></div>
            <div>
              <span className="text-slate-500 text-[10px] uppercase">Resolution Rate</span>
              <p className="font-bold text-cyan-400">{mttrData.resolution_rate_pct}%</p>
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Incidents Kanban List & Selected Incident Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incidents List (1 col) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">
              All Incidents ({incidents.length})
            </h3>
          </div>

          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {incidents.map((inc) => {
              const isSelected = selectedIncident?.id === inc.id;
              return (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-rose-950/30 border-rose-500/50 shadow-md shadow-rose-950/20'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5 font-mono text-xs">
                    <span className="font-bold text-rose-400 uppercase">{inc.priority} • INC-{inc.id}</span>
                    <StatusBadge status={inc.status} />
                  </div>
                  <h4 className="font-bold text-xs text-white line-clamp-1">{inc.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">{inc.description}</p>
                  
                  <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Opened {new Date(inc.opened_at).toLocaleTimeString()}</span>
                    <span className="text-cyan-400">Investigate →</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Incident Details & Timeline (2 cols) */}
        {selectedIncident ? (
          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-6 space-y-6">
            {/* Top Details */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-300 text-xs font-mono font-bold uppercase">
                    {selectedIncident.priority}
                  </span>
                  <h3 className="font-bold text-base text-white">{selectedIncident.title}</h3>
                </div>
                <p className="text-xs text-slate-400 font-mono">Incident #{selectedIncident.id} • Opened {new Date(selectedIncident.opened_at).toLocaleString()}</p>
              </div>

              <div className="flex items-center gap-3">
                <StatusBadge status={selectedIncident.status} />
                <button
                  onClick={() => setShowRcaModal(true)}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 rounded-lg text-xs font-bold font-mono flex items-center gap-1.5"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Generate RCA</span>
                </button>
              </div>
            </div>

            {/* Incident Description */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed">
              {selectedIncident.description}
            </div>

            {/* Investigation Timeline */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 font-mono flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                Investigation Timeline & Event History
              </h4>

              <div className="space-y-3">
                {selectedIncident.events?.map((evt) => (
                  <div key={evt.id} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs font-mono space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span className="font-bold uppercase text-cyan-400">{evt.event_type}</span>
                      <span>{new Date(evt.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-slate-300">{evt.message}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* RCA Report View (if generated) */}
            {selectedIncident.root_cause_analysis && (
              <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/40 text-xs font-mono space-y-2">
                <span className="font-bold text-cyan-300 uppercase text-[11px] block">
                  Root Cause Analysis (RCA) Published
                </span>
                <p className="text-slate-300">{selectedIncident.root_cause_analysis.root_cause_summary}</p>
                <div className="text-[11px] text-slate-400">
                  <span className="text-slate-500 font-bold">Preventative Actions: </span>
                  {selectedIncident.root_cause_analysis.preventative_actions?.join(', ')}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="lg:col-span-2 p-12 text-center text-slate-500 text-xs">
            Select an incident ticket to view investigation timeline and runbooks.
          </div>
        )}
      </div>

      {/* RCA Post-Mortem Modal */}
      {showRcaModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-white font-mono">Publish Root Cause Analysis (RCA)</h3>
              <button onClick={() => setShowRcaModal(false)} className="text-slate-500 hover:text-white">✕</button>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Root Cause Summary</label>
              <textarea
                rows={3}
                value={rcaRootCause}
                onChange={(e) => setRcaRootCause(e.target.value)}
                placeholder="Explain the technical trigger, sequence of failures, and resolution..."
                className="w-full p-3 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Preventative Action Plan</label>
              <textarea
                rows={2}
                value={rcaPreventative}
                onChange={(e) => setRcaPreventative(e.target.value)}
                placeholder="Actionable steps to prevent recurrence..."
                className="w-full p-3 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setShowRcaModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono font-bold"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateRca}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold"
              >
                Publish RCA Document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
