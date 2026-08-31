import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { NocDashboard } from './pages/NocDashboard';
import { TopologyCanvas } from './pages/TopologyCanvas';
import { DeviceInventory } from './pages/DeviceInventory';
import { DiscoveryScanner } from './pages/DiscoveryScanner';
import { IpamExplorer } from './pages/IpamExplorer';
import { ConfigManager } from './pages/ConfigManager';
import { AutomationWorkflows } from './pages/AutomationWorkflows';
import { IncidentManagement } from './pages/IncidentManagement';
import { AlertCenter } from './pages/AlertCenter';
import { SecurityCompliance } from './pages/SecurityCompliance';
import { TrafficAnalytics } from './pages/TrafficAnalytics';
import { DiagnosticsHub } from './pages/DiagnosticsHub';
import { CapacityPlanner } from './pages/CapacityPlanner';
import { ReportsCenter } from './pages/ReportsCenter';
import { AuditTrail } from './pages/AuditTrail';
import { RbacAdmin } from './pages/RbacAdmin';
import { Login } from './pages/Login';
import { wsClient } from './services/websocket';

export const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return !!localStorage.getItem('nexus_access_token');
  });

  useEffect(() => {
    if (isAuthenticated) {
      wsClient.connect('all');
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <Router>
      <div className="flex h-screen bg-slate-950 text-slate-100 font-sans antialiased overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Navbar />

          <main className="flex-1 overflow-y-auto custom-scrollbar bg-slate-950">
            <Routes>
              <Route path="/" element={<NocDashboard />} />
              <Route path="/topology" element={<TopologyCanvas />} />
              <Route path="/monitoring" element={<NocDashboard />} />
              <Route path="/devices" element={<DeviceInventory />} />
              <Route path="/discovery" element={<DiscoveryScanner />} />
              <Route path="/ipam" element={<IpamExplorer />} />
              <Route path="/configs" element={<ConfigManager />} />
              <Route path="/automation" element={<AutomationWorkflows />} />
              <Route path="/incidents" element={<IncidentManagement />} />
              <Route path="/alerts" element={<AlertCenter />} />
              <Route path="/security" element={<SecurityCompliance />} />
              <Route path="/traffic" element={<TrafficAnalytics />} />
              <Route path="/diagnostics" element={<DiagnosticsHub />} />
              <Route path="/capacity" element={<CapacityPlanner />} />
              <Route path="/reports" element={<ReportsCenter />} />
              <Route path="/audit" element={<AuditTrail />} />
              <Route path="/rbac" element={<RbacAdmin />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
