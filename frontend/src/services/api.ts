import axios from 'axios';
import * as Types from '../types';

const API_BASE = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('nexus_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  login: async (username: string, password: string): Promise<Types.AuthTokens> => {
    const res = await apiClient.post('/auth/token', { username, password });
    return res.data;
  },
  getCurrentUser: async (): Promise<Types.User> => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  // Devices & Sites
  getDevices: async (site_id?: number, type?: string, status?: string): Promise<Types.Device[]> => {
    const res = await apiClient.get('/devices', { params: { site_id, device_type: type, status } });
    return res.data;
  },
  getDevice: async (id: number): Promise<Types.Device> => {
    const res = await apiClient.get(`/devices/${id}`);
    return res.data;
  },
  getSites: async (): Promise<Types.Site[]> => {
    const res = await apiClient.get('/sites');
    return res.data;
  },
  executeCli: async (deviceId: number, command: string) => {
    const res = await apiClient.post(`/devices/${deviceId}/cli`, { command });
    return res.data;
  },
  syncDevice: async (deviceId: number) => {
    const res = await apiClient.post(`/devices/${deviceId}/sync`);
    return res.data;
  },

  // Discovery
  startScan: async (payload: { name: string; scan_type: string; target_subnet: string; ports?: number[]; snmp_communities?: string[] }) => {
    const res = await apiClient.post('/discovery/scans', payload);
    return res.data;
  },
  getScanJobs: async () => {
    const res = await apiClient.get('/discovery/jobs');
    return res.data;
  },
  getDiscoveredDevices: async (job_id?: number) => {
    const res = await apiClient.get('/discovery/devices', { params: { job_id } });
    return res.data;
  },
  importDiscoveredDevice: async (deviceId: number, site_id?: number) => {
    const res = await apiClient.post(`/discovery/devices/${deviceId}/import`, null, { params: { site_id } });
    return res.data;
  },

  // Topology
  getTopologyGraph: async (site_id?: number): Promise<Types.TopologyGraph> => {
    const res = await apiClient.get('/topology', { params: { site_id } });
    return res.data;
  },
  tracePath: async (source_id: number, target_id: number): Promise<Types.PathTraceResponse> => {
    const res = await apiClient.post('/topology/path-trace', { source_device_id: source_id, target_device_id: target_id });
    return res.data;
  },
  getSpofReport: async (): Promise<Types.SpofReport> => {
    const res = await apiClient.get('/topology/spof');
    return res.data;
  },
  saveLayout: async (nodes: Array<{ node_id: string; x: number; y: number }>) => {
    const res = await apiClient.post('/topology/layout', { nodes });
    return res.data;
  },

  // Monitoring
  getMonitoringOverview: async (): Promise<Types.MonitoringOverview> => {
    const res = await apiClient.get('/monitoring/overview');
    return res.data;
  },
  getDeviceTelemetry: async (deviceId: number, hours: number = 24) => {
    const res = await apiClient.get(`/monitoring/devices/${deviceId}`, { params: { hours } });
    return res.data;
  },
  triggerPollCycle: async () => {
    const res = await apiClient.post('/monitoring/poll-now');
    return res.data;
  },

  // IPAM
  getSubnets: async (vrf_id?: number, site_id?: number): Promise<Types.Subnet[]> => {
    const res = await apiClient.get('/ipam/subnets', { params: { vrf_id, site_id } });
    return res.data;
  },
  createSubnet: async (data: any) => {
    const res = await apiClient.post('/ipam/subnets', data);
    return res.data;
  },
  splitSubnet: async (subnet_id: number, new_prefix_len: number) => {
    const res = await apiClient.post('/ipam/subnets/split', { subnet_id, new_prefix_len });
    return res.data;
  },
  allocateIp: async (data: any) => {
    const res = await apiClient.post('/ipam/ips/allocate', data);
    return res.data;
  },
  calculateCidr: async (cidr: string) => {
    const res = await apiClient.post('/ipam/calculate-cidr', { cidr });
    return res.data;
  },
  getConflicts: async () => {
    const res = await apiClient.get('/ipam/conflicts');
    return res.data;
  },

  // Configurations (NCM)
  getConfigVersions: async (deviceId: number): Promise<Types.ConfigVersion[]> => {
    const res = await apiClient.get(`/configs/devices/${deviceId}/versions`);
    return res.data;
  },
  takeBackup: async (deviceId: number, comment?: string) => {
    const res = await apiClient.post(`/configs/devices/${deviceId}/backup`, null, { params: { comment } });
    return res.data;
  },
  compareConfigs: async (source_text: string, target_text: string): Promise<Types.ConfigDiff> => {
    const res = await apiClient.post('/configs/diff', { source_text, target_text });
    return res.data;
  },
  getTemplates: async (): Promise<Types.ConfigTemplate[]> => {
    const res = await apiClient.get('/configs/templates');
    return res.data;
  },
  createTemplate: async (data: any) => {
    const res = await apiClient.post('/configs/templates', data);
    return res.data;
  },
  renderTemplate: async (template_id: number, variables: any) => {
    const res = await apiClient.post('/configs/templates/render', { template_id, variables });
    return res.data;
  },
  deployConfig: async (data: any) => {
    const res = await apiClient.post('/configs/deploy', data);
    return res.data;
  },
  rollbackConfig: async (deviceId: number, target_version_id: number, comment?: string) => {
    const res = await apiClient.post('/configs/rollback', { device_id: deviceId, target_version_id, comment });
    return res.data;
  },

  // Automation
  getWorkflows: async (): Promise<Types.Workflow[]> => {
    const res = await apiClient.get('/automation/workflows');
    return res.data;
  },
  createWorkflow: async (data: any) => {
    const res = await apiClient.post('/automation/workflows', data);
    return res.data;
  },
  triggerWorkflow: async (id: number, payload?: any): Promise<Types.WorkflowRun> => {
    const res = await apiClient.post(`/automation/workflows/${id}/run`, { trigger_payload: payload });
    return res.data;
  },
  getWorkflowRuns: async (workflow_id?: number): Promise<Types.WorkflowRun[]> => {
    const res = await apiClient.get('/automation/runs', { params: { workflow_id } });
    return res.data;
  },
  getActionCatalog: async () => {
    const res = await apiClient.get('/automation/actions');
    return res.data;
  },

  // Incidents & Alerts
  getIncidents: async (status?: string, severity?: string): Promise<Types.Incident[]> => {
    const res = await apiClient.get('/incidents', { params: { status, severity } });
    return res.data;
  },
  createIncident: async (data: any): Promise<Types.Incident> => {
    const res = await apiClient.post('/incidents', data);
    return res.data;
  },
  getIncident: async (id: number): Promise<Types.Incident> => {
    const res = await apiClient.get(`/incidents/${id}`);
    return res.data;
  },
  assignIncident: async (id: number, assignee_id: number) => {
    const res = await apiClient.put(`/incidents/${id}/assign`, null, { params: { assignee_id } });
    return res.data;
  },
  resolveIncident: async (id: number, notes: string) => {
    const res = await apiClient.post(`/incidents/${id}/resolve`, null, { params: { notes } });
    return res.data;
  },
  generateRca: async (id: number, data: any) => {
    const res = await apiClient.post(`/incidents/${id}/rca`, data);
    return res.data;
  },
  getMttrAnalytics: async () => {
    const res = await apiClient.get('/incidents/analytics/mttr');
    return res.data;
  },
  getAlerts: async (status?: string, severity?: string): Promise<Types.Alert[]> => {
    const res = await apiClient.get('/alerts', { params: { status, severity } });
    return res.data;
  },
  getAlertRules: async () => {
    const res = await apiClient.get('/alerts/rules');
    return res.data;
  },
  createAlertRule: async (data: any) => {
    const res = await apiClient.post('/alerts/rules', data);
    return res.data;
  },
  acknowledgeAlerts: async (alert_ids: number[]) => {
    const res = await apiClient.post('/alerts/acknowledge', { alert_ids });
    return res.data;
  },
  silenceAlerts: async (deviceId: number, minutes: number, reason: string) => {
    const res = await apiClient.post('/alerts/silence', { device_id: deviceId, duration_minutes: minutes, reason });
    return res.data;
  },

  // Security & Traffic
  getSecurityOverview: async (): Promise<Types.SecurityScoreOverview> => {
    const res = await apiClient.get('/security/overview');
    return res.data;
  },
  runSecurityAudit: async (deviceId: number) => {
    const res = await apiClient.post(`/security/devices/${deviceId}/audit`);
    return res.data;
  },
  analyzeAcl: async (deviceId: number, acl_name: string, rules: any[]) => {
    const res = await apiClient.post('/security/acl/analyze', { device_id: deviceId, acl_name, rules });
    return res.data;
  },
  getRogueDevices: async () => {
    const res = await apiClient.get('/security/rogue-devices');
    return res.data;
  },
  getTopTalkers: async (hours: number = 24): Promise<Types.TopTalkersResponse> => {
    const res = await apiClient.get('/traffic/top-talkers', { params: { hours } });
    return res.data;
  },

  // Diagnostics & Health
  runPing: async (target: string, count: number = 4, source_device_id?: number) => {
    const res = await apiClient.post('/diagnostics/ping', { target, count, source_device_id });
    return res.data;
  },
  runTraceroute: async (target: string, max_hops: number = 15) => {
    const res = await apiClient.post('/diagnostics/traceroute', { target, max_hops });
    return res.data;
  },
  runDns: async (query_name: string, record_type: string = 'A') => {
    const res = await apiClient.post('/diagnostics/dns', { query_name, record_type });
    return res.data;
  },
  runPortProbe: async (target_ip: string, port: number) => {
    const res = await apiClient.post('/diagnostics/port-probe', { target_ip, port });
    return res.data;
  },
  getFleetHealth: async (): Promise<Types.FleetHealthOverview> => {
    const res = await apiClient.get('/health/fleet');
    return res.data;
  },
  getDeviceHealth: async (deviceId: number) => {
    const res = await apiClient.get(`/health/devices/${deviceId}`);
    return res.data;
  },
  getCapacityOverview: async (): Promise<Types.CapacityOverview> => {
    const res = await apiClient.get('/capacity/overview');
    return res.data;
  },

  // Reports & Audit
  downloadExecutivePdf: async () => {
    const res = await apiClient.get('/reports/executive-summary/pdf', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'netops_executive_summary.pdf');
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  downloadDevicesCsv: async () => {
    const res = await apiClient.get('/reports/devices/csv', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'netops_device_inventory.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  getAuditLogs: async (resource_type?: string, action?: string): Promise<Types.AuditLog[]> => {
    const res = await apiClient.get('/audit/logs', { params: { resource_type, action } });
    return res.data;
  },
};
