import React, { useState, useEffect } from 'react';
import {
  FileCode2,
  GitCompare,
  RotateCcw,
  Play,
  CheckCircle2,
  Layers,
  Plus,
  Search,
  Download,
  AlertTriangle,
  History,
  FileCheck,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const ConfigManager: React.FC = () => {
  const [devices, setDevices] = useState<Types.Device[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | ''>('');
  const [versions, setVersions] = useState<Types.ConfigVersion[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<Types.ConfigVersion | null>(null);

  // Diff State
  const [diffResult, setDiffResult] = useState<Types.ConfigDiff | null>(null);
  const [compareVersionId, setCompareVersionId] = useState<number | ''>('');

  // Template State
  const [templates, setTemplates] = useState<Types.ConfigTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Types.ConfigTemplate | null>(null);
  const [templateVarsInput, setTemplateVarsInput] = useState('{\n  "hostname": "RTR-CORE-01",\n  "int_name": "GigabitEthernet0/1"\n}');
  const [renderedOutput, setRenderedOutput] = useState('');

  const loadData = async () => {
    try {
      const [devs, tmpls] = await Promise.all([api.getDevices(), api.getTemplates()]);
      setDevices(devs);
      setTemplates(tmpls);
      if (devs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(devs[0].id);
      }
      if (tmpls.length > 0 && !selectedTemplate) {
        setSelectedTemplate(tmpls[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadVersions = async (devId: number) => {
    try {
      const v = await api.getConfigVersions(devId);
      setVersions(v);
      if (v.length > 0) {
        setSelectedVersion(v[0]);
        if (v.length > 1) {
          setCompareVersionId(v[1].id);
          const d = await api.compareConfigs(v[1].config_text, v[0].config_text);
          setDiffResult(d);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedDeviceId) {
      loadVersions(Number(selectedDeviceId));
    }
  }, [selectedDeviceId]);

  const handleTakeBackup = async () => {
    if (!selectedDeviceId) return;
    try {
      await api.takeBackup(Number(selectedDeviceId), 'Manual Snapshot from NCM UI');
      await loadVersions(Number(selectedDeviceId));
    } catch (e) {
      console.error(e);
    }
  };

  const handleRollback = async (versionId: number) => {
    if (!selectedDeviceId) return;
    if (!confirm('Are you sure you want to execute an atomic rollback to this configuration version?')) return;
    try {
      await api.rollbackConfig(Number(selectedDeviceId), versionId);
      await loadVersions(Number(selectedDeviceId));
      alert('Rollback executed successfully!');
    } catch (e: any) {
      alert(`Rollback error: ${e?.response?.data?.detail || e.message}`);
    }
  };

  const handleRenderTemplate = async () => {
    if (!selectedTemplate) return;
    try {
      const parsedVars = JSON.parse(templateVarsInput);
      const res = await api.renderTemplate(selectedTemplate.id, parsedVars);
      setRenderedOutput(res.rendered_config || res.errors.join('\n'));
    } catch (e: any) {
      setRenderedOutput(`JSON syntax error: ${e.message}`);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
            <FileCode2 className="w-5 h-5 text-cyan-400" />
            Network Configuration Management (NCM)
          </h2>
          <p className="text-xs text-slate-400">
            Canonical versioning, side-by-side syntax diffing, Jinja2 template rendering, and 1-click atomic rollback.
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
            onClick={handleTakeBackup}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono shadow-lg shadow-cyan-500/10"
          >
            Take Snapshot
          </button>
        </div>
      </div>

      {/* Main Double Grid: Version History & Diff Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Version History List (1 col) */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono flex items-center gap-2">
              <History className="w-4 h-4 text-cyan-400" />
              Configuration Backups ({versions.length})
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">SHA-256 Verified</span>
          </div>

          <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {versions.map((ver) => {
              const isSelected = selectedVersion?.id === ver.id;
              return (
                <div
                  key={ver.id}
                  onClick={() => setSelectedVersion(ver)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500/50 shadow-md shadow-cyan-950/30'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-mono mb-1">
                    <span className="font-bold text-cyan-400">v{ver.version_number}</span>
                    <span className="text-[10px] text-slate-500">{new Date(ver.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-[11px] text-slate-300 font-mono line-clamp-1">{ver.comment || 'Automatic Snapshot'}</p>
                  <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-500 truncate max-w-[140px]">{ver.config_hash.slice(0, 16)}...</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRollback(ver.id);
                      }}
                      className="px-2 py-0.5 bg-rose-950/60 hover:bg-rose-900/60 border border-rose-800/60 text-rose-300 rounded font-bold"
                    >
                      Rollback
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Diff & Code Viewer (2 cols) */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <GitCompare className="w-4 h-4 text-cyan-400" />
                <span className="font-bold text-xs uppercase tracking-wider text-white font-mono">
                  {diffResult ? 'Side-by-Side Configuration Diff' : 'Active Running-Config'}
                </span>
              </div>
              {diffResult && (
                <div className="flex items-center gap-3 text-xs font-mono">
                  <span className="text-emerald-400">+{diffResult.additions} added</span>
                  <span className="text-rose-400">-{diffResult.deletions} removed</span>
                </div>
              )}
            </div>

            {/* Code Diff Display Container */}
            <div className="bg-black/90 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 h-[480px] overflow-y-auto whitespace-pre-wrap leading-relaxed">
              {diffResult?.unified_diff ? (
                diffResult.unified_diff.split('\n').map((line, idx) => (
                  <div
                    key={idx}
                    className={`${
                      line.startsWith('+')
                        ? 'bg-emerald-950/60 text-emerald-300'
                        : line.startsWith('-')
                        ? 'bg-rose-950/60 text-rose-300'
                        : 'text-slate-400'
                    }`}
                  >
                    {line}
                  </div>
                ))
              ) : selectedVersion ? (
                selectedVersion.config_text
              ) : (
                'Select a configuration version from the left panel.'
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Jinja2 Template Studio */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-sm text-white font-mono flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-cyan-400" />
            Jinja2 Configuration Template Studio
          </h3>
          <button
            onClick={handleRenderTemplate}
            className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-bold font-mono"
          >
            Dry-Run Render
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Template Text */}
          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono">Template Definition</label>
            <textarea
              rows={8}
              value={selectedTemplate?.template_text || 'hostname {{ hostname }}\ninterface {{ int_name }}\n no shutdown'}
              readOnly
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-cyan-300 font-mono focus:outline-none"
            />
          </div>

          {/* Variables Input */}
          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono">JSON Variables Payload</label>
            <textarea
              rows={8}
              value={templateVarsInput}
              onChange={(e) => setTemplateVarsInput(e.target.value)}
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Rendered Output */}
          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono">Rendered Output</label>
            <textarea
              rows={8}
              value={renderedOutput}
              readOnly
              placeholder="Click 'Dry-Run Render' to test template generation..."
              className="w-full p-3 bg-black/90 border border-slate-800 rounded-lg text-xs text-emerald-400 font-mono focus:outline-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
