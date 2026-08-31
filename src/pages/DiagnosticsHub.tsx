import React, { useState } from 'react';
import {
  Wrench,
  Activity,
  Route,
  Globe,
  Radio,
  Play,
  CheckCircle2,
  AlertCircle,
  Clock,
} from 'lucide-react';
import { api } from '../services/api';

export const DiagnosticsHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'ping' | 'traceroute' | 'dns' | 'port'>('ping');

  // Ping State
  const [pingTarget, setPingTarget] = useState('10.100.0.1');
  const [pingCount, setPingCount] = useState(4);
  const [pingResult, setPingResult] = useState<any>(null);
  const [isPinging, setIsPinging] = useState(false);

  // Traceroute State
  const [traceTarget, setTraceTarget] = useState('8.8.8.8');
  const [traceResult, setTraceResult] = useState<any>(null);
  const [isTracing, setIsTracing] = useState(false);

  // DNS State
  const [dnsQuery, setDnsQuery] = useState('google.com');
  const [dnsType, setDnsType] = useState('A');
  const [dnsResult, setDnsResult] = useState<any>(null);
  const [isDnsLoading, setIsDnsLoading] = useState(false);

  // Port Probe State
  const [probeHost, setProbeHost] = useState('10.100.0.1');
  const [probePort, setProbePort] = useState(22);
  const [probeResult, setProbeResult] = useState<any>(null);
  const [isProbing, setIsProbing] = useState(false);

  const handlePing = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPinging(true);
    try {
      const res = await api.runPing(pingTarget, pingCount);
      setPingResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsPinging(false);
    }
  };

  const handleTrace = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTracing(true);
    try {
      const res = await api.runTraceroute(traceTarget);
      setTraceResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsTracing(false);
    }
  };

  const handleDns = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsDnsLoading(true);
    try {
      const res = await api.runDns(dnsQuery, dnsType);
      setDnsResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsDnsLoading(false);
    }
  };

  const handlePortProbe = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProbing(true);
    try {
      const res = await api.runPortProbe(probeHost, probePort);
      setProbeResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsProbing(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
          <Wrench className="w-5 h-5 text-cyan-400" />
          Network Diagnostics & Troubleshooting Toolkit
        </h2>
        <p className="text-xs text-slate-400">
          Precision ICMP latency measurements, multi-hop path traceroute, DNS query resolution, and TCP port prober.
        </p>
      </div>

      {/* Diagnostics Navigation Tabs */}
      <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
        {[
          { id: 'ping', label: 'ICMP / Precision Ping', icon: <Activity className="w-4 h-4" /> },
          { id: 'traceroute', label: 'Path Traceroute', icon: <Route className="w-4 h-4" /> },
          { id: 'dns', label: 'DNS Name Resolution', icon: <Globe className="w-4 h-4" /> },
          { id: 'port', label: 'TCP Socket Port Probe', icon: <Radio className="w-4 h-4" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-bold transition-all ${
              activeTab === tab.id
                ? 'bg-cyan-600 text-white shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white bg-slate-900 border border-slate-800'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      {activeTab === 'ping' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">ICMP Ping Settings</h3>
            <form onSubmit={handlePing} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Destination Host / IP</label>
                <input
                  type="text"
                  value={pingTarget}
                  onChange={(e) => setPingTarget(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Packet Count</label>
                <input
                  type="number"
                  min={1}
                  max={20}
                  value={pingCount}
                  onChange={(e) => setPingCount(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isPinging}
                className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold"
              >
                {isPinging ? 'Transmitting ICMP Probes...' : 'Send Ping Requests'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">Ping Statistics & Output</h3>
            {pingResult ? (
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-3 text-xs font-mono p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Packets Transmitted</span>
                    <p className="font-bold text-white">{pingResult.packets_sent}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Packets Received</span>
                    <p className="font-bold text-emerald-400">{pingResult.packets_received}</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Packet Loss</span>
                    <p className="font-bold text-cyan-400">{pingResult.packet_loss_percent}%</p>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase">Average Latency</span>
                    <p className="font-bold text-white">{pingResult.avg_rtt_ms} ms</p>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-black/90 border border-slate-800 font-mono text-xs text-emerald-400 space-y-1">
                  <p>PING {pingResult.target} (56 data bytes)</p>
                  {pingResult.rtt_samples?.map((s: number, idx: number) => (
                    <p key={idx}>64 bytes from {pingResult.target}: icmp_seq={idx + 1} ttl=64 time={s} ms</p>
                  ))}
                  <p className="pt-2 text-slate-400">
                    --- {pingResult.target} ping statistics ---
                    <br />
                    min/avg/max = {pingResult.min_rtt_ms}/{pingResult.avg_rtt_ms}/{pingResult.max_rtt_ms} ms
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-xs font-mono">
                Click 'Send Ping Requests' to measure round-trip times and packet loss.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'traceroute' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">Traceroute Parameters</h3>
            <form onSubmit={handleTrace} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Destination Host / IP</label>
                <input
                  type="text"
                  value={traceTarget}
                  onChange={(e) => setTraceTarget(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isTracing}
                className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold"
              >
                {isTracing ? 'Tracing Route Hops...' : 'Run Path Traceroute'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">Hop-by-Hop Route Trace</h3>
            {traceResult ? (
              <div className="space-y-2">
                {traceResult.hops.map((hop: any) => (
                  <div key={hop.hop_number} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-cyan-400">#{hop.hop_number}</span>
                      <span className="text-white font-bold">{hop.hostname || hop.ip_address}</span>
                      <span className="text-slate-500 font-sans">({hop.ip_address})</span>
                    </div>
                    <span className="text-emerald-400 font-bold">{hop.rtt_ms} ms</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-xs font-mono">
                Click 'Run Path Traceroute' to inspect multi-hop routing paths.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'dns' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">DNS Lookup</h3>
            <form onSubmit={handleDns} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Hostname Query</label>
                <input
                  type="text"
                  value={dnsQuery}
                  onChange={(e) => setDnsQuery(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Record Type</label>
                <select
                  value={dnsType}
                  onChange={(e) => setDnsType(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                >
                  <option value="A">A (IPv4 Address)</option>
                  <option value="AAAA">AAAA (IPv6 Address)</option>
                  <option value="CNAME">CNAME (Alias)</option>
                  <option value="MX">MX (Mail Exchange)</option>
                  <option value="TXT">TXT (SPF / Verification)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={isDnsLoading}
                className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold"
              >
                {isDnsLoading ? 'Querying DNS...' : 'Resolve DNS'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">Resolution Answers</h3>
            {dnsResult ? (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-3">
                <div className="flex justify-between text-slate-400">
                  <span>Server: {dnsResult.dns_server}</span>
                  <span className="text-emerald-400">{dnsResult.response_time_ms} ms</span>
                </div>
                <div className="space-y-1">
                  {dnsResult.answers.map((ans: string, idx: number) => (
                    <div key={idx} className="p-2 rounded bg-black/80 text-cyan-300 font-bold">
                      {dnsResult.query_name} IN {dnsResult.record_type} {ans}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-xs font-mono">
                Enter hostname and record type to perform authoritative DNS lookup.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'port' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">Socket Probe</h3>
            <form onSubmit={handlePortProbe} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Target IP</label>
                <input
                  type="text"
                  value={probeHost}
                  onChange={(e) => setProbeHost(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Port (TCP)</label>
                <input
                  type="number"
                  value={probePort}
                  onChange={(e) => setProbePort(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white font-mono"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isProbing}
                className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-bold"
              >
                {isProbing ? 'Connecting...' : 'Probe Socket Port'}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-5 space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-white font-mono">Socket Response</h3>
            {probeResult ? (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">{probeResult.target_ip}:{probeResult.port}</span>
                  <span className={`px-2 py-0.5 rounded font-bold uppercase ${probeResult.is_open ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-rose-950 text-rose-300 border border-rose-800'}`}>
                    {probeResult.is_open ? 'PORT OPEN' : 'CLOSED / FILTERED'}
                  </span>
                </div>
                <p className="text-slate-400">Service: <span className="text-cyan-400">{probeResult.service_name}</span></p>
                <p className="text-slate-500 text-[10px]">TCP handshake latency: {probeResult.latency_ms} ms</p>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-xs font-mono">
                Probe TCP ports to verify connectivity and firewalls.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
