import React, { useState, useEffect } from 'react';
import {
  Network,
  Route,
  ShieldAlert,
  Layers,
  Search,
  Zap,
  Activity,
  AlertCircle,
  CheckCircle2,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { StatusBadge } from '../components/layout/StatusBadge';
import { api } from '../services/api';
import * as Types from '../types';

export const TopologyCanvas: React.FC = () => {
  const [graph, setGraph] = useState<Types.TopologyGraph | null>(null);
  const [sites, setSites] = useState<Types.Site[]>([]);
  const [selectedSite, setSelectedSite] = useState<number | undefined>(undefined);
  const [selectedNode, setSelectedNode] = useState<Types.TopologyNode | null>(null);

  // Path tracing state
  const [sourceDevId, setSourceDevId] = useState<number | ''>('');
  const [targetDevId, setTargetDevId] = useState<number | ''>('');
  const [pathResult, setPathResult] = useState<Types.PathTraceResponse | null>(null);
  const [isTracing, setIsTracing] = useState(false);

  // SPOF analysis state
  const [showSpof, setShowSpof] = useState(false);
  const [spofReport, setSpofReport] = useState<Types.SpofReport | null>(null);

  const loadTopology = async () => {
    try {
      const [g, s, spof] = await Promise.all([
        api.getTopologyGraph(selectedSite),
        api.getSites(),
        api.getSpofReport(),
      ]);
      setGraph(g);
      setSites(s);
      setSpofReport(spof);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadTopology();
  }, [selectedSite]);

  const handleTracePath = async () => {
    if (!sourceDevId || !targetDevId) return;
    setIsTracing(true);
    try {
      const res = await api.tracePath(Number(sourceDevId), Number(targetDevId));
      setPathResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsTracing(false);
    }
  };

  const spofNodeIds = new Set(spofReport?.single_points_of_failure.map((s) => `dev_${s.device_id}`) || []);
  const activePathNodeIds = new Set(pathResult?.path.map((p) => `dev_${p.device_id}`) || []);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-slate-950">
      {/* Topology Control Toolbar */}
      <div className="h-14 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-bold text-white font-mono uppercase">
            <Network className="w-4 h-4 text-cyan-400" />
            <span>Fabric Topology Canvas</span>
          </div>

          {/* Site Filter */}
          <select
            value={selectedSite || ''}
            onChange={(e) => setSelectedSite(e.target.value ? Number(e.target.value) : undefined)}
            className="px-3 py-1 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="">Global WAN Fabric (All Sites)</option>
            {sites.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.code})
              </option>
            ))}
          </select>

          {/* SPOF Toggle */}
          <button
            onClick={() => setShowSpof(!showSpof)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold border transition-all ${
              showSpof
                ? 'bg-rose-950/80 border-rose-600 text-rose-300 shadow-md shadow-rose-950/50'
                : 'bg-slate-950 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>SPOF & Articulation Points ({spofReport?.single_points_of_failure.length || 0})</span>
          </button>
        </div>

        {/* Path Tracer Controls */}
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold text-slate-400 font-mono flex items-center gap-1">
            <Route className="w-3.5 h-3.5 text-cyan-400" />
            Dijkstra Path:
          </span>
          <select
            value={sourceDevId}
            onChange={(e) => setSourceDevId(e.target.value ? Number(e.target.value) : '')}
            className="px-2 py-1 bg-slate-950 border border-slate-700 rounded text-xs text-slate-300 font-mono w-40"
          >
            <option value="">Source Node</option>
            {graph?.nodes.map((n) => (
              <option key={n.id} value={n.device_id}>
                {n.label}
              </option>
            ))}
          </select>
          <span className="text-slate-500 font-bold">→</span>
          <select
            value={targetDevId}
            onChange={(e) => setTargetDevId(e.target.value ? Number(e.target.value) : '')}
            className="px-2 py-1 bg-slate-950 border border-slate-700 rounded text-xs text-slate-300 font-mono w-40"
          >
            <option value="">Target Node</option>
            {graph?.nodes.map((n) => (
              <option key={n.id} value={n.device_id}>
                {n.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleTracePath}
            disabled={!sourceDevId || !targetDevId || isTracing}
            className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold transition-all disabled:opacity-50"
          >
            {isTracing ? 'Calculating...' : 'Trace'}
          </button>
        </div>
      </div>

      {/* Main Canvas & Detail Sidebar */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* SVG Topology Graph Canvas */}
        <div className="flex-1 bg-slate-950 p-6 overflow-auto relative select-none">
          <svg className="w-full h-full min-w-[1000px] min-h-[650px]">
            <defs>
              <linearGradient id="edgeGradDefault" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#0284c7" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0.6" />
              </linearGradient>
              <linearGradient id="edgeGradActive" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#38bdf8" />
                <stop offset="100%" stopColor="#38bdf8" />
              </linearGradient>
            </defs>

            {/* Render Links (Edges) */}
            {graph?.edges.map((edge) => {
              const srcNode = graph.nodes.find((n) => n.id === edge.source);
              const dstNode = graph.nodes.find((n) => n.id === edge.target);
              if (!srcNode || !dstNode) return null;

              const isPathEdge =
                activePathNodeIds.has(edge.source) && activePathNodeIds.has(edge.target);

              return (
                <g key={edge.id}>
                  <line
                    x1={srcNode.x || 100}
                    y1={srcNode.y || 100}
                    x2={dstNode.x || 200}
                    y2={dstNode.y || 200}
                    stroke={isPathEdge ? '#38bdf8' : '#334155'}
                    strokeWidth={isPathEdge ? 4 : 2}
                    strokeDasharray={isPathEdge ? '6,3' : 'none'}
                    className={isPathEdge ? 'animate-pulse' : ''}
                  />
                  {/* Link throughput tag */}
                  <text
                    x={((srcNode.x || 100) + (dstNode.x || 200)) / 2}
                    y={((srcNode.y || 100) + (dstNode.y || 200)) / 2 - 6}
                    fill="#64748b"
                    fontSize="10"
                    textAnchor="middle"
                    fontFamily="monospace"
                  >
                    {edge.bandwidth_mbps >= 100000 ? '100G' : edge.bandwidth_mbps >= 40000 ? '40G' : '10G'}
                  </text>
                </g>
              );
            })}

            {/* Render Nodes */}
            {graph?.nodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const isSpof = showSpof && spofNodeIds.has(node.id);
              const isPath = activePathNodeIds.has(node.id);

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x || 100}, ${node.y || 100})`}
                  className="cursor-pointer transition-transform hover:scale-110"
                  onClick={() => setSelectedNode(node)}
                >
                  {/* Outer Ring */}
                  <circle
                    r={isSpof ? 24 : 20}
                    fill={
                      isSpof
                        ? '#e11d48'
                        : isPath
                        ? '#0284c7'
                        : isSelected
                        ? '#4f46e5'
                        : '#0f172a'
                    }
                    stroke={
                      isSpof
                        ? '#fda4af'
                        : isPath
                        ? '#38bdf8'
                        : isSelected
                        ? '#818cf8'
                        : '#334155'
                    }
                    strokeWidth={isSelected || isSpof || isPath ? 3 : 1.5}
                    className={isSpof ? 'animate-pulse' : ''}
                  />

                  {/* Inner Node Icon */}
                  <text
                    textAnchor="middle"
                    dy=".3em"
                    fill="#ffffff"
                    fontSize="10"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    {node.tier === 'core' ? 'CR' : node.tier === 'spine' ? 'SP' : node.tier === 'leaf' ? 'LF' : 'SW'}
                  </text>

                  {/* Node Label */}
                  <text
                    y={32}
                    textAnchor="middle"
                    fill={isSpof ? '#fb7185' : '#e2e8f0'}
                    fontSize="11"
                    fontWeight="600"
                    fontFamily="monospace"
                  >
                    {node.label}
                  </text>

                  {/* Management IP */}
                  <text
                    y={44}
                    textAnchor="middle"
                    fill="#64748b"
                    fontSize="9"
                    fontFamily="monospace"
                  >
                    {node.management_ip}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Node & Path Detail Drawer (Right panel) */}
        <div className="w-96 border-l border-slate-800 bg-slate-900/95 backdrop-blur-md p-5 overflow-y-auto space-y-6">
          {/* Path Trace Result Card */}
          {pathResult && (
            <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-cyan-400 font-mono">Dijkstra Hop Trace</span>
                <span className="text-xs font-mono text-slate-400">{pathResult.total_latency_ms} ms RTT</span>
              </div>

              <div className="space-y-2">
                {pathResult.path.map((hop) => (
                  <div key={hop.hop_number} className="flex items-center justify-between text-xs p-2 rounded bg-slate-900 border border-slate-800 font-mono">
                    <div>
                      <span className="text-cyan-400 font-bold mr-2">#{hop.hop_number}</span>
                      <span className="text-white font-bold">{hop.hostname}</span>
                    </div>
                    <span className="text-slate-400 text-[10px]">{hop.latency_ms} ms</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Selected Node Details */}
          {selectedNode ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm text-white font-mono">{selectedNode.label}</h3>
                <StatusBadge status={selectedNode.status} />
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-slate-500">Management IP:</span>
                  <span className="text-slate-200">{selectedNode.management_ip}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Device Type:</span>
                  <span className="text-slate-200 uppercase">{selectedNode.device_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Fabric Tier:</span>
                  <span className="text-cyan-400 uppercase">{selectedNode.tier}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Vendor:</span>
                  <span className="text-slate-200">{selectedNode.vendor}</span>
                </div>
              </div>

              {/* SPOF Blast Radius Warning */}
              {spofNodeIds.has(selectedNode.id) && (
                <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-xs text-rose-300 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold">
                    <AlertCircle className="w-4 h-4" />
                    <span>Single Point of Failure (SPOF)</span>
                  </div>
                  <p className="text-[11px] text-rose-400">
                    Failure of this node will partition downstream spine/leaf access switches. Redundant link configuration recommended.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="p-6 text-center text-slate-500 text-xs">
              Click any switch or router node on the canvas to inspect interfaces, telemetry, and blast radius.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
