# NetOps Nexus — Enterprise Network Intelligence, Automation & Observability Platform

[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.12-blue.svg)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript%20%7C%20Tailwind-emerald.svg)](https://react.dev)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2016%20%7C%20SQLAlchemy%202.0-indigo.svg)](https://www.postgresql.org)
[![Realtime](https://img.shields.io/badge/Realtime-WebSockets%20%7C%20Redis-rose.svg)](https://redis.io)

**NetOps Nexus** is a carrier-grade, full-lifecycle Enterprise Network Operations Center (NOC), Network Automation, Network Observability, Network Security, and IP Address Management (IPAM) platform. It provides real-time topology visualization, active telemetry monitoring, multi-vendor configuration management with automatic rollback, visual DAG workflow automation, incident correlation, threat intelligence, and a high-fidelity Network Lab Simulation Adapter.

---

## 🌟 Key Architecture & Capabilities

```
                         NetOps Nexus Architecture
                                     │
             ┌───────────────────────┼───────────────────────┐
             │                       │                       │
     NOC Web Dashboard      REST & WebSockets API       CLI / Automation
   (React + TS + Tailwind)   (FastAPI + AsyncIO)        (Python / Webhook)
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     │
                             API Gateway / RBAC
                    (7 Roles + Granular Permission Matrix)
                                     │
     ┌───────────────────┬───────────────────┬───────────────────┐
     │                   │                   │                   │
Network Discovery  Topology Engine    Monitoring & Flow   IPAM & Subnets
(CIDR / SNMP /     (NetworkX Graph,   (Time-Series Stats, (IPv4/v6, Split/
 SSH / LLDP / ARP)  Path Trace, SPOF)  Throughput, Jitter) Merge, Conflicts)
     │                   │                   │                   │
     └───────────────────┴───────────────────┼───────────────────┘
                                             │
     ┌───────────────────┬───────────────────┼───────────────────┐
     │                   │                   │                   │
Configuration (NCM) Automation Engine  Incident & Alerts   Security & Audit
(Diff, Jinja, Staged (Visual DAG, SSH,  (Lifecycle, MTTR,   (CIS Benchmark,
 Rollout, Rollback)   Verify, Revert)    Correlation, RCA)   Score, ACL Audit)
     │                   │                   │                   │
     └───────────────────┴───────────────────┼───────────────────┘
                                             │
                              Device Adapter Layer
                                             │
             ┌───────────────────────┼───────────────────────┐
             │                       │                       │
       SNMP Adapter            SSH Adapter          Lab Network Adapter
     (PySNMP / MIBs)      (AsyncSSH / Paramiko)   (Multi-Tier Simulation)
                                     │
                            PostgreSQL 16 + Redis 7
                                     │
                        Async Background Task Workers
```

---

## 🚀 Major Modules

1. **Enterprise RBAC & Auth**: 7 granular roles (`Super Admin`, `Network Admin`, `Network Engineer`, `Security Engineer`, `NOC Engineer`, `Auditor`, `Read Only`) with strict backend permission enforcement.
2. **Device Inventory**: Multi-vendor routers, switches, firewalls, load balancers, and access points with full interface, routing table, and VLAN inventory.
3. **Network Discovery**: Multi-protocol discovery engine executing CIDR sweeps, ICMP ping, TCP port probing, SNMP v2c/v3 walk, SSH probe, and LLDP/CDP neighbor discovery.
4. **Network Lab Simulation Adapter**: Built-in enterprise network simulation generating real-time interface telemetry, packet counter drift, synthetic route flaps, and multi-vendor CLI emulation (Cisco IOS, Arista EOS, Juniper Junos).
5. **Interactive Network Topology**: Force-directed and hierarchical graph engine with live link health, traffic utilization heatmaps, path tracing (Dijkstra), dependency analysis, and blast radius calculation.
6. **Network Observability & Monitoring**: Sub-second telemetry streaming for CPU, memory, interface bit/packet rates, errors, CRC discards, BGP/OSPF states, and optical power levels via WebSockets.
7. **IP Address Management (IPAM)**: IPv4/IPv6 CIDR math, visual subnet tree, subnet splitting & merging, IP reservation, conflict detection, and DHCP pool tracking.
8. **Network Configuration Management (NCM)**: Configuration backup snapshots, side-by-side syntax-highlighted diff engine, Jinja2 configuration templates, staged rollouts, and automatic rollback on verification failure.
9. **Visual Network Automation**: DAG-based workflow builder with triggers, conditions, validation gates, CLI actions, interface controls, notification webhooks, and automated recovery actions.
10. **Incident Lifecycle & Correlation**: Automatic alert deduplication, incident creation, engineer assignment, MTTR analytics, interactive investigation timelines, and root cause analysis (RCA) generation.
11. **Rule-Based Alert Engine**: Threshold evaluation, hysteresis, maintenance window suppression, alert correlation, escalation chains, and webhook delivery.
12. **Defensive Security & Compliance**: Automated CIS configuration benchmarks, unauthorized device detection, weak protocol warnings, shadowed ACL analysis, and a dynamic 0-100 Network Security Score.
13. **Traffic Intelligence**: NetFlow/sFlow style flow records ingestion, Top Talkers, Top Destinations, Layer 4/7 protocol breakdown, conversation chord matrix, and volumetric anomaly detection.
14. **Diagnostics Toolkit**: Interactive Ping, hop-by-hop Traceroute, multi-type DNS resolver (A, AAAA, MX, TXT, NS), Port connectivity tester, Route lookup, and Path Analysis.
15. **Network Health Engine**: Dynamically computed score weighted across Availability (25%), Performance (20%), Packet Loss (15%), Interface Health (15%), Configuration Health (10%), Security Posture (10%), and Capacity Headroom (5%).
16. **Capacity Planning**: Trend regression models forecasting interface saturation dates, CPU/RAM exhaustion, and automated hardware upgrade suggestions.
17. **Enterprise Reports**: PDF, CSV, and JSON report generation for Network Health, Device Inventory, SLA Availability, Interface Saturation, Security Audit, and IPAM.
18. **Immutable Audit Trail**: Structured event logging capturing every state mutation with user identity, IP address, before/after diffs, and execution timestamps.
19. **NOC Dashboard**: High-density operational dashboard featuring live status matrices, throughput sparklines, active alert tickers, and instant action drawers.

---

## 🛠️ Quickstart & Local Installation

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm 10+
- (Optional) Docker & Docker Compose
- (Optional) PostgreSQL 16 & Redis 7

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/LingamalluRitesh/NetOpsNexus.git
   cd NetOpsNexus
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   ```

3. **Install Dependencies**:
   ```bash
   # Using Makefile
   make install

   # Or manually
   pip install -r requirements.txt
   npm install
   ```

4. **Initialize Database & Seed Lab Topology**:
   ```bash
   make migrate
   make seed
   ```

5. **Start Development Servers**:
   ```bash
   # Starts backend on http://localhost:8000 and frontend on http://localhost:5173
   make dev
   ```

---

## 🐳 Docker Deployment

To spin up the complete multi-service stack with PostgreSQL, Redis, FastAPI Backend, Async Worker, and Nginx Frontend:

```bash
make docker-up
```

Access the services:
- **Web Interface**: `http://localhost`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/telemetry`

To stop the containers:
```bash
make docker-down
```

---

## 🧪 Testing & Validation

Run the automated test suite and quality validation benchmarks:

```bash
# Run complete test suite
make test

# Run tests with HTML coverage report
make coverage

# Run project quality and LOC validation benchmark
make validate
```

---

## 📚 Technical Documentation

Detailed architecture specifications, guides, and API documentation:
- [Architecture Overview](docs/ARCHITECTURE.md)
- [REST & WebSocket API Reference](docs/API_REFERENCE.md)
- [Network Lab Simulation Guide](docs/LAB_ADAPTER_GUIDE.md)
- [Workflow Automation Guide](docs/AUTOMATION_GUIDE.md)
- [RBAC & Security Guide](docs/RBAC_SECURITY.md)

---

## 👥 Default Credentials (Development / Lab Mode)

| Role | Username | Default Password | Granular Permissions |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `NexusAdmin2026!` | All permissions (`*`) |
| **Network Admin** | `netadmin` | `NetAdmin2026!` | `devices.*`, `configs.*`, `ipam.*`, `topology.*`, `monitoring.*` |
| **Network Engineer** | `neteng` | `NetEng2026!` | `devices.read/write`, `configs.read/deploy`, `automation.execute` |
| **Security Engineer** | `seceng` | `SecEng2026!` | `security.*`, `audit.*`, `devices.read`, `incidents.create` |
| **NOC Engineer** | `noc` | `NocUser2026!` | `monitoring.*`, `alerts.*`, `incidents.*`, `diagnostics.*` |
| **Auditor** | `auditor` | `Auditor2026!` | `audit.read`, `reports.export`, `*.read` |
| **Read Only** | `viewer` | `Viewer2026!` | `*.read` |
