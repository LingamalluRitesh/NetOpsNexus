# NetOps Nexus — REST & WebSocket API Reference

The NetOps Nexus backend exposes a comprehensive OpenAPI 3.1 compliant REST API and interactive WebSocket streaming interfaces.

## Base URLs
- **REST API Base**: `/api/v1`
- **WebSocket Gateway**: `/ws/telemetry`

---

## 1. Authentication & RBAC

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access & refresh tokens | Public |
| `POST` | `/api/v1/auth/refresh` | Refresh expired access token | Public |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile and permissions | Authenticated |
| `GET` | `/api/v1/rbac/roles` | List all system roles and permission matrices | `rbac.read` |
| `GET` | `/api/v1/rbac/users` | List and search user accounts | `rbac.read` |
| `POST` | `/api/v1/rbac/users` | Create a new user account with role assignment | `rbac.write` |

---

## 2. Device Inventory & Discovery

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/devices` | Query devices with filtering, pagination, and search | `devices.read` |
| `POST` | `/api/v1/devices` | Register a new device manually or from discovery | `devices.write` |
| `GET` | `/api/v1/devices/{id}` | Get detailed device profile, interfaces, and routes | `devices.read` |
| `PUT` | `/api/v1/devices/{id}` | Update device attributes, site assignment, or tags | `devices.write` |
| `DELETE` | `/api/v1/devices/{id}` | Decommission and delete device from inventory | `devices.delete` |
| `GET` | `/api/v1/devices/{id}/interfaces` | Retrieve all physical and logical interfaces | `devices.read` |
| `POST` | `/api/v1/discovery/scan` | Initiate a background multi-protocol network sweep | `discovery.run` |
| `GET` | `/api/v1/discovery/jobs` | List recent discovery jobs and statuses | `discovery.read` |
| `GET` | `/api/v1/discovery/jobs/{id}` | Get real-time status and logs of a discovery job | `discovery.read` |

---

## 3. Topology & Graph Engine

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/topology` | Fetch full topology graph (nodes, edges, metrics) | `topology.read` |
| `GET` | `/api/v1/topology/site/{site_id}` | Fetch site-specific topology subgraph | `topology.read` |
| `POST` | `/api/v1/topology/path-trace` | Compute shortest and redundant paths between nodes | `topology.read` |
| `GET` | `/api/v1/topology/dependencies/{device_id}` | Compute upstream & downstream blast radius | `topology.read` |
| `PUT` | `/api/v1/topology/layout` | Persist custom canvas node coordinates | `topology.write` |

---

## 4. IP Address Management (IPAM)

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/ipam/subnets` | List all subnets with utilization metrics | `ipam.read` |
| `POST` | `/api/v1/ipam/subnets` | Create a new IPv4/IPv6 subnet | `ipam.write` |
| `POST` | `/api/v1/ipam/subnets/split` | Split a subnet into smaller prefix blocks | `ipam.write` |
| `POST` | `/api/v1/ipam/subnets/merge` | Merge contiguous prefix blocks | `ipam.write` |
| `GET` | `/api/v1/ipam/subnets/{id}/ips` | Retrieve all IP allocations within a subnet | `ipam.read` |
| `POST` | `/api/v1/ipam/ips/allocate` | Allocate or reserve an IP address | `ipam.write` |
| `POST` | `/api/v1/ipam/ips/release` | Release an allocated IP address back to pool | `ipam.write` |
| `GET` | `/api/v1/ipam/conflicts` | Detect IP address collisions and duplicates | `ipam.read` |

---

## 5. Configuration Management (NCM)

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/configs/{device_id}/versions` | List configuration backup history | `configs.read` |
| `POST` | `/api/v1/configs/{device_id}/backup` | Trigger an immediate configuration snapshot | `configs.write` |
| `POST` | `/api/v1/configs/diff` | Compute side-by-side unified diff between versions | `configs.read` |
| `GET` | `/api/v1/configs/templates` | List Jinja2 configuration templates | `configs.read` |
| `POST` | `/api/v1/configs/templates` | Create or update a configuration template | `configs.write` |
| `POST` | `/api/v1/configs/deploy` | Stage and deploy configuration with validation | `configs.deploy` |
| `POST` | `/api/v1/configs/rollback` | Rollback device to a previous configuration version | `configs.rollback` |

---

## 6. Workflow Automation

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/automation/workflows` | List all automation workflows | `automation.read` |
| `POST` | `/api/v1/automation/workflows` | Create a visual DAG automation workflow | `automation.write` |
| `POST` | `/api/v1/automation/workflows/{id}/run` | Trigger workflow execution | `automation.execute` |
| `GET` | `/api/v1/automation/runs` | List workflow execution history | `automation.read` |
| `GET` | `/api/v1/automation/runs/{id}` | Get detailed execution logs and step output | `automation.read` |

---

## 7. Incidents, Alerts & Security

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/incidents` | List incidents with filtering by severity/status | `incidents.read` |
| `POST` | `/api/v1/incidents` | Create a new incident ticket | `incidents.create` |
| `PUT` | `/api/v1/incidents/{id}/assign` | Assign incident to an engineer | `incidents.assign` |
| `POST` | `/api/v1/incidents/{id}/resolve` | Resolve incident with notes and RCA data | `incidents.write` |
| `GET` | `/api/v1/alerts` | List active alarms and alerts | `alerts.read` |
| `POST` | `/api/v1/alerts/{id}/acknowledge` | Acknowledge active alert | `alerts.ack` |
| `GET` | `/api/v1/security/findings` | List security audit findings & CVE exposures | `security.read` |
| `GET` | `/api/v1/security/score` | Compute dynamic Network Security Score (0-100) | `security.read` |

---

## 8. Diagnostics, Health, Capacity & Reports

| Method | Endpoint | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/diagnostics/ping` | Execute live ICMP ping test | `diagnostics.run` |
| `POST` | `/api/v1/diagnostics/traceroute` | Execute live multi-hop traceroute | `diagnostics.run` |
| `POST` | `/api/v1/diagnostics/dns` | Execute DNS record resolution query | `diagnostics.run` |
| `POST` | `/api/v1/diagnostics/port-test` | Execute TCP port connectivity test | `diagnostics.run` |
| `GET` | `/api/v1/health` | Compute weighted dynamic Network Health Score | `health.read` |
| `GET` | `/api/v1/capacity/forecast` | Predict interface and device saturation dates | `capacity.read` |
| `POST` | `/api/v1/reports/generate` | Generate and export report (PDF, CSV, JSON) | `reports.export` |
| `GET` | `/api/v1/audit/logs` | Query immutable audit log trail | `audit.read` |
