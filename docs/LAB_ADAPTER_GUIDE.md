# NetOps Nexus — Network Lab Adapter Guide

## Overview

The **Network Lab Adapter** (`LabNetworkAdapter`) is a carrier-grade network simulation subsystem embedded in the NetOps Nexus architecture. It implements the exact same `DeviceAdapter` protocol interface used by physical SNMP, SSH, and ICMP drivers.

### Architecture

```
                      DeviceAdapter (Protocol)
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │                           │                           │
SNMPAdapter                 SSHAdapter               LabNetworkAdapter
(PySNMP RFC1213 / IF-MIB)  (Paramiko / AsyncSSH)     (Realistic Multi-Tier Simulation)
                                                             │
                                         ┌───────────────────┼───────────────────┐
                                         │                   │                   │
                                  Simulated Devices   Dynamic Telemetry   CLI Emulation
                                  (Core, Spines, Leaf, (Bitrates, Jitter, (Cisco IOS,
                                   Firewalls, APs)     CRC, Drops, BGP)   EOS, Junos)
```

## Seed Topology

When running in lab mode (`LAB_MODE=true`), NetOps Nexus boots with a realistic multi-tier enterprise network:

1. **HQ Data Center**:
   - `RTR-CORE-01` (Cisco Catalyst 8500 Edge Core)
   - `RTR-CORE-02` (Cisco Catalyst 8500 Redundant Core)
   - `SW-SPINE-01` & `SW-SPINE-02` (Arista 7050X3 100G Spines)
   - `SW-LEAF-01` to `SW-LEAF-04` (Arista 7050SX 10G/25G Leaf Switches)
   - `FW-DC-PRI-01` & `FW-DC-SEC-02` (Palo Alto PA-5450 Next-Gen Firewalls)
   - `LB-APP-01` (F5 BIG-IP i5800 Load Balancer)

2. **Regional Campus (San Jose)**:
   - `RTR-CAMPUS-01` (Juniper MX204 Router)
   - `SW-DIST-01` & `SW-DIST-02` (Cisco Catalyst 9500 Distribution)
   - `SW-ACC-01` to `SW-ACC-04` (Cisco Catalyst 9300 Access Switches with PoE)
   - `WAP-FLOOR1-01` & `WAP-FLOOR2-01` (Cisco Catalyst 9130AX APs)

3. **Branch Office (London / Remote)**:
   - `RTR-BR-LON-01` (Cisco ISR 4451 SD-WAN Gateway)
   - `SW-BR-LON-01` (Cisco Catalyst 9200 Switch)
   - `FW-BR-LON-01` (Fortinet FortiGate 100F)

## Simulated Dynamic Telemetry

The Lab Adapter continuously generates realistic fluctuations:
- **Interface Throughput**: Sine-wave diurnal curves simulating working hours vs off-peak hours with random burst spikes.
- **Packet Error & CRC Drifts**: Micro-burst drops and CRC errors on degraded links to test alerting and health degradation.
- **BGP Peerings & OSPF Adjancies**: Simulates eBGP neighbor state transitions (Established, Active, Idle) and route convergence.
- **Interactive CLI Emulation**: Supports `show running-config`, `show ip interface brief`, `show ip route`, `show ip bgp summary`, `show mac address-table`, `show lldp neighbors`, and configuration mutation commands (`configure terminal`, `interface Gi0/1`, `no shutdown`, etc.).
