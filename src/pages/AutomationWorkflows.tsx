import React, { useState, useEffect } from 'react';
import {
  Workflow,
  Play,
  CheckCircle2,
  AlertCircle,
  Plus,
  Clock,
  Code2,
  Terminal,
  Activity,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const AutomationWorkflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Types.Workflow[]>([]);
  const [runs, setRuns] = useState<Types.WorkflowRun[]>([]);
  const [actionCatalog, setActionCatalog] = useState<any[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Types.Workflow | null>(null);
  const [selectedRun, setSelectedRun] = useState<Types.WorkflowRun | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const loadData = async () => {
    try {
      const [wfs, r, acts] = await Promise.all([
        api.getWorkflows(),
        api.getWorkflowRuns(),
        api.getActionCatalog(),
      ]);
      setWorkflows(wfs);
      setRuns(r);
      setActionCatalog(acts);
      if (wfs.length > 0 && !selectedWorkflow) {
        setSelectedWorkflow(wfs[0]);
      }
      if (r.length > 0 && !selectedRun) {
        setSelectedRun(r[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerWorkflow = async (wfId: number) => {
    setIsRunning(true);
    try {
      const run = await api.triggerWorkflow(wfId, { source: 'NOC UI Manual Trigger' });
      setSelectedRun(run);
      await loadData();
    } catch (e: any) {
      alert(`Execution error: ${e?.response?.data?.detail || e.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <Workflow className="w-5 h-5 text-cyan-400" />
            Network Automation DAG Workflow Engine
          </h2>
          <p className="text-xs text-slate-400">
            Orchestrate multi-step operational pipelines: Pre-checks → CLI Commands → Config Push → Health Verification → Auto Rollback.
          </p>
        </div>
      </div>

      {/* Action Catalog Badges */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-4">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono block mb-2">
          Available Action Catalog ({actionCatalog.length})
        </span>
        <div className="flex flex-wrap gap-2">
          {actionCatalog.map((act) => (
            <span
              key={act.action_name}
              className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-400 flex items-center gap-1.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
              {act.action_name}
            </span>
          ))}
        </div>
      </div>

      {/* Main Grid: Workflows List & Execution Run Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workflows List (1 col) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">
              Configured Workflows ({workflows.length})
            </h3>
          </div>

          <div className="space-y-3">
            {workflows.map((wf) => {
              const isSelected = selectedWorkflow?.id === wf.id;
              return (
                <div
                  key={wf.id}
                  onClick={() => setSelectedWorkflow(wf)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500/50 shadow-md shadow-cyan-950/30'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <h4 className="font-bold text-xs text-white font-mono">{wf.name}</h4>
                    <StatusBadge status={wf.is_active ? 'active' : 'offline'} />
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{wf.description}</p>
                  
                  <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-500">{wf.definition?.nodes?.length || 0} DAG steps</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTriggerWorkflow(wf.id);
                      }}
                      disabled={isRunning}
                      className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-bold flex items-center gap-1"
                    >
                      <Play className="w-3 h-3" />
                      <span>Execute</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Workflow DAG & Execution Trace (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Selected Workflow DAG Nodes Visualizer */}
          {selectedWorkflow && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-sm text-white font-mono">{selectedWorkflow.name}</h3>
                  <p className="text-xs text-slate-400">{selectedWorkflow.description}</p>
                </div>
                <button
                  onClick={() => handleTriggerWorkflow(selectedWorkflow.id)}
                  disabled={isRunning}
                  className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono flex items-center gap-1.5 shadow-lg shadow-cyan-500/10"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>{isRunning ? 'Running DAG...' : 'Trigger Pipeline'}</span>
                </button>
              </div>

              {/* DAG Pipeline Flow */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center gap-3">
                {selectedWorkflow.definition?.nodes?.map((node, idx) => (
                  <React.Fragment key={node.id}>
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-center min-w-[140px]">
                      <span className="text-[10px] text-cyan-400 uppercase font-bold block">{node.type}</span>
                      <span className="font-bold text-white block mt-0.5">{node.label}</span>
                      <span className="text-[10px] text-slate-500 block truncate">{node.action_name || 'Manual'}</span>
                    </div>
                    {idx < (selectedWorkflow.definition?.nodes?.length || 0) - 1 && (
                      <ChevronRight className="w-4 h-4 text-slate-600" />
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}

          {/* Execution Run Timeline Log */}
          {selectedRun && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-xs uppercase tracking-wider text-white font-mono">
                    Execution Trace #{selectedRun.id}
                  </h4>
                  <p className="text-[10px] text-slate-400 font-mono">
                    Triggered by {selectedRun.trigger_source} • {new Date(selectedRun.started_at).toLocaleString()}
                  </p>
                </div>
                <StatusBadge status={selectedRun.status} />
              </div>

              {/* Step Logs */}
              <div className="space-y-2.5">
                {selectedRun.step_logs?.map((step) => (
                  <div
                    key={step.id}
                    className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs font-mono space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span className="font-bold text-white">{step.action_name || step.node_id}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] text-slate-400">{step.execution_time_ms} ms</span>
                        <StatusBadge status={step.status} />
                      </div>
                    </div>
                    {step.output_data && (
                      <pre className="p-2.5 rounded bg-black/80 border border-slate-800/80 text-[11px] text-emerald-300 overflow-x-auto">
                        {JSON.stringify(step.output_data, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
