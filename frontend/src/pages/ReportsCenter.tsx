import React from 'react';
import {
  FileText,
  Download,
  FileSpreadsheet,
  FileCode,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../services/api';

export const ReportsCenter: React.FC = () => {
  const handleDownloadPdf = async () => {
    try {
      await api.downloadExecutivePdf();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDownloadCsv = async () => {
    try {
      await api.downloadDevicesCsv();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white font-mono flex items-center gap-2">
          <FileText className="w-5 h-5 text-cyan-400" />
          Executive Intelligence Reports & Export Hub
        </h2>
        <p className="text-xs text-slate-400">
          Export formal compliance reports, operational summaries, and full inventory spreadsheets.
        </p>
      </div>

      {/* Report Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* PDF Executive Report Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-6 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-cyan-950/80 border border-cyan-800/80 flex items-center justify-center text-cyan-400 shadow-md">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-white">Executive Network Operations Summary (PDF)</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Publication-grade executive document featuring overall Fleet Health grade, CIS Hardening compliance breakdown, 30-day MTTR metrics, and WAN backbone utilization highlights.
            </p>
          </div>

          <button
            onClick={handleDownloadPdf}
            className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold font-mono flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/10"
          >
            <Download className="w-4 h-4" />
            <span>Download Executive PDF Report</span>
          </button>
        </div>

        {/* CSV Inventory Export Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 backdrop-blur-md p-6 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center text-emerald-400 shadow-md">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-white">Device Hardware Inventory (CSV Export)</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Complete tabular export of all managed routers, switches, and firewalls with serial numbers, management IPs, vendor models, OS versions, and site assignments.
            </p>
          </div>

          <button
            onClick={handleDownloadCsv}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold font-mono flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/10"
          >
            <Download className="w-4 h-4" />
            <span>Download Device Inventory (.csv)</span>
          </button>
        </div>
      </div>
    </div>
  );
};
