# NetOps Nexus — Architectural Specification

## 1. System Overview

NetOps Nexus is built upon a decoupled, domain-driven service architecture designed to deliver sub-second observability, scalable network discovery, zero-downtime configuration deployments, and automated incident remediation.

### High-Level Component Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Presentation Layer                               │
│  React 18 SPA + TypeScript + Tailwind CSS + Cytoscape Graph Engine + WS     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / WebSockets
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                              API Gateway & Router                            │
│  FastAPI Async Handlers + JWT Bearer Auth + Granular RBAC Dependency Checks │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
┌───────▼──────────────┐   ┌───────────▼──────────┐   ┌───────────────▼──────┐
│  Core Domain Layer   │   │ Automation & Config  │   │ Security & Analytics │
│  - Device Inventory  │   │ - Jinja2 NCM Engine  │   │ - CIS Benchmark Aud  │
│  - Graph Topology    │   │ - DAG Workflow Exec  │   │ - Shadow ACL Engine  │
│  - IPAM IPv4/IPv6    │   │ - Auto Rollback      │   │ - NetFlow Ingestion  │
│  - Time-Series Mon   │   │ - Action Catalog     │   │ - Health Calculator  │
└───────┬──────────────┘   └───────────┬──────────┘   └───────────────┬──────┘
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                       Device Adapter Abstraction Layer                      │
│   ┌───────────────────┬────────────────────┬─────────────────────────────┐  │
│   │   SNMP Adapter    │    SSH Adapter     │     Lab Network Adapter     │  │
│   │   (PySNMP Walks)  │ (Paramiko/AsyncSSH)│  (Multi-Tier Simulated NOC) │  │
│   └───────────────────┴────────────────────┴─────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                          Data & Event Persistence                           │
│   PostgreSQL 16 (Relational/JSONB) + Redis 7 (Pub/Sub & Task Queue)         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Domain Data Flow

1. **Discovery Ingestion**:
   - Operator submits CIDR sweep (e.g., `10.100.0.0/24`).
   - Discovery worker scans targets asynchronously using ICMP, TCP port probes (22, 23, 80, 443, 161, 830), and SNMP OID queries.
   - Discovered devices, interfaces, ARP entries, and LLDP neighbors are correlated and ingested into the inventory database.
   - Topology graph is rebuilt incrementally using NetworkX.

2. **Telemetry Streaming**:
   - Monitoring collector polls devices or reads telemetry streams every 5–15 seconds.
   - Time-series metrics (CPU, RAM, Interface bps/pps, Drops, CRC, BGP state) are stored in PostgreSQL / Redis buffers.
   - Real-time multiplexer pushes differential telemetry updates over WebSockets to all subscribed frontend clients.

3. **Rule Evaluation & Incidents**:
   - Alert Engine evaluates metric streams against defined threshold rules (e.g. `packet_loss > 5% for 300s`).
   - Correlation engine suppresses duplicate alerts from downstream devices if an upstream core router is offline.
   - Escalation policies trigger P1/P2/P3/P4 incident tickets, notify engineers via webhooks, and launch automated remediation runbooks.

4. **Configuration Lifecycle**:
   - Engineers author configuration templates using Jinja2 with schema-validated parameter bindings.
   - Deployment preview computes a unified side-by-side diff against the device's running configuration.
   - Deployment orchestrator executes staged rollout with pre-checks, configuration push, and post-validation.
   - If health checks fail (e.g., routing loss, interface flap), the system triggers an instantaneous atomic rollback to the previous version.
