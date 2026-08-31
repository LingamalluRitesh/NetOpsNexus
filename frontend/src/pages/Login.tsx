import React, { useState } from 'react';
import { Network, Lock, User, Key, ArrowRight, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

interface LoginProps {
  onLoginSuccess: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('SuperAdmin2026!');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');
    try {
      const res = await api.login(username, password);
      localStorage.setItem('nexus_access_token', res.access_token);
      localStorage.setItem('nexus_user', JSON.stringify(res.user));
      onLoginSuccess();
    } catch (e: any) {
      setErrorMsg(e?.response?.data?.detail || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background ambient gradient glow */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-cyan-600/20 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-xl border border-slate-800 p-8 rounded-2xl shadow-2xl space-y-6 z-10">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 mx-auto">
            <Network className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-xl font-extrabold text-white font-mono tracking-wider">
            NETOPS <span className="text-cyan-400">NEXUS</span>
          </h1>
          <p className="text-xs text-slate-400">Enterprise Network Intelligence & Observability Platform</p>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300 font-mono text-center">
            {errorMsg}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Operator Username</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase font-mono mb-1.5">Security Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/10 transition-all disabled:opacity-50"
          >
            <span>{isLoading ? 'Authenticating...' : 'Sign In to Command Center'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Credentials Helper */}
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-[10px] text-slate-500 font-mono space-y-1">
          <div className="flex items-center gap-1.5 text-slate-400 font-bold">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>Default Demo Credentials</span>
          </div>
          <p>User: <span className="text-cyan-300">admin</span> • Pass: <span className="text-cyan-300">SuperAdmin2026!</span></p>
        </div>
      </div>
    </div>
  );
};
