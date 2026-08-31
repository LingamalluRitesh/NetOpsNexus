/**
 * NetOps Nexus — TypeScript Type Definitions
 */

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  roles: string[];
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Site {
  id: number;
  name: string;
  code: string;
  location?: string;
  country?: string;
  device_count?: number;
}

export interface NetworkInterface {
  id: number;
  device_id: number;
  name: string;
  mac_address?: string;
  ip_address?: string;
  admin_status: 'up' | 'down';
  oper_status: 'up' | 'down';
  speed_mbps: number;
  duplex: string;
  rx_bps: number;
  tx_bps: number;
  rx_pps: number;
  tx_pps: number;
  rx_errors: number;
  tx_errors: number;
}

export interface Device {
  id: number;
  hostname: string;
  management_ip: string;
  device_type: string;
  vendor: string;
  model: string;
  os_type: string;
  os_version?: string;
  serial_number?: string;
  site_id?: number;
  site_name?: string;
  status: 'online' | 'warning' | 'critical' | 'maintenance' | 'offline';
  cpu_utilization: number;
  memory_utilization: number;
  temperature_celsius?: number;
  uptime_seconds?: number;
  interfaces?: NetworkInterface[];
  last_seen?: string;
}

export interface TopologyNode {
  id: string;
  label: string;
  device_id: number;
  device_type: string;
  status: string;
  management_ip: string;
  site_id?: number;
  vendor: string;
  x?: number;
  y?: number;
  tier: 'core' | 'spine' | 'leaf' | 'access' | 'wan' | 'endpoint';
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  link_type: string;
  bandwidth_mbps: number;
  utilization_pct: number;
  status: 'up' | 'down' | 'degraded';
  latency_ms: number;
}

export interface TopologyGraph {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface PathHop {
  hop_number: number;
  device_id: number;
  hostname: string;
  ip_address: string;
  latency_ms: number;
  packet_loss_pct: number;
  interface_name: string;
  status: string;
}

export interface PathTraceResponse {
  source_device_id: number;
  target_device_id: number;
  path_found: boolean;
  total_hops: number;
  total_latency_ms: number;
  path: PathHop[];
  redundant_paths_count: number;
}

export interface SpofReport {
  single_points_of_failure: Array<{
    device_id: number;
    hostname: string;
    device_type: string;
    impact_level: string;
    blast_radius_nodes_count: number;
    isolated_sites: string[];
  }>;
  critical_bridge_links: Array<{
    link_id: string;
    source: string;
    target: string;
    status: string;
  }>;
}

export interface MonitoringOverview {
  total_devices_monitored: number;
  devices_online: number;
  devices_warning: number;
  devices_critical: number;
  average_network_cpu: number;
  average_network_memory: number;
  average_latency_ms: number;
  total_throughput_gbps: number;
  total_packet_errors_1h: number;
  top_utilized_interfaces: Array<{
    device_hostname: string;
    interface_name: string;
    rx_mbps: number;
    tx_mbps: number;
    utilization_pct: number;
  }>;
  active_bgp_sessions: number;
}

export interface Subnet {
  id: number;
  network_address: string;
  prefix_len: number;
  ip_version: number;
  name: string;
  description?: string;
  gateway_ip?: string;
  total_ips: number;
  used_ips: number;
  reserved_ips: number;
  available_ips: number;
  utilization_pct: number;
  status: 'active' | 'reserved' | 'deprecated';
}

export interface IpAddress {
  id: number;
  subnet_id: number;
  address: string;
  status: 'allocated' | 'reserved' | 'free' | 'conflict';
  fqdn?: string;
  mac_address?: string;
  description?: string;
  allocated_to?: string;
  last_seen: string;
}

export interface ConfigVersion {
  id: number;
  device_id: number;
  version_number: number;
  config_text: string;
  config_hash: string;
  backup_type: string;
  comment?: string;
  created_at: string;
}

export interface ConfigDiff {
  unified_diff: string;
  diff_lines: Array<{
    line_number_src?: number;
    line_number_dst?: number;
    type: 'unchanged' | 'added' | 'removed' | 'modified';
    content: string;
  }>;
  additions: number;
  deletions: number;
  modifications: number;
  is_identical: boolean;
}

export interface ConfigTemplate {
  id: number;
  name: string;
  vendor: string;
  os_type: string;
  template_text: string;
  description?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description?: string;
  trigger_type: string;
  is_active: boolean;
  definition: {
    nodes: Array<{ id: string; type: string; label: string; action_name?: string; parameters?: any }>;
    edges: Array<{ id: string; source: string; target: string }>;
  };
}

export interface WorkflowRun {
  id: number;
  workflow_id: number;
  trigger_source: string;
  status: 'running' | 'success' | 'failed' | 'rolled_back' | 'cancelled';
  started_at: string;
  completed_at?: string;
  error_message?: string;
  step_logs: Array<{
    id: number;
    node_id: string;
    node_type: string;
    action_name?: string;
    status: string;
    execution_time_ms: number;
    output_data?: any;
  }>;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  priority: 'p1' | 'p2' | 'p3' | 'p4';
  status: 'open' | 'investigating' | 'mitigating' | 'resolved' | 'closed';
  assigned_to_id?: number;
  affected_device_id?: number;
  opened_at: string;
  resolved_at?: string;
  mttr_seconds?: number;
  resolution_notes?: string;
  root_cause_analysis?: {
    root_cause_summary: string;
    impacted_services?: string[];
    remediation_steps_taken?: string[];
    preventative_actions?: string[];
  };
  events?: Array<{
    id: number;
    event_type: string;
    message: string;
    created_at: string;
  }>;
}

export interface Alert {
  id: number;
  rule_id?: number;
  device_id: number;
  device_hostname?: string;
  message: string;
  metric_name: string;
  metric_value: number;
  severity: 'critical' | 'warning' | 'info';
  status: 'active' | 'acknowledged' | 'silenced' | 'resolved';
  triggered_at: string;
}

export interface SecurityScoreOverview {
  overall_fleet_score: number;
  grade: string;
  total_devices_audited: number;
  compliant_devices_count: number;
  vulnerable_devices_count: number;
  critical_findings_count: number;
  top_vulnerabilities: Array<{ title: string; affected_devices: number; severity: string }>;
}

export interface TopTalkersResponse {
  time_window_hours: number;
  total_volume_gigabytes: number;
  top_sources: Array<{ entity: string; megabytes_total: number; percentage: number; flows_count: number }>;
  top_destinations: Array<{ entity: string; megabytes_total: number; percentage: number; flows_count: number }>;
  top_applications: Array<{ entity: string; megabytes_total: number; percentage: number; flows_count: number }>;
  top_protocols: Array<{ entity: string; megabytes_total: number; percentage: number; flows_count: number }>;
}

export interface FleetHealthOverview {
  fleet_health_score: number;
  fleet_health_grade: string;
  healthy_devices_count: number;
  warning_devices_count: number;
  critical_devices_count: number;
  lowest_scoring_devices: Array<{ device_id: number; hostname: string; score: number; grade: string }>;
}

export interface CapacityOverview {
  total_resources_analyzed: number;
  critical_saturation_count: number;
  warning_saturation_count: number;
  top_critical_forecasts: Array<{
    resource_type: string;
    resource_name: string;
    current_utilization_pct: number;
    daily_growth_rate_pct: number;
    days_to_threshold_80?: number;
    days_to_saturation_100?: number;
    projected_exhaustion_date?: string;
    urgency_level: string;
    recommendation: string;
  }>;
}

export interface AuditLog {
  id: number;
  username: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details: any;
  ip_address?: string;
  timestamp: string;
}
