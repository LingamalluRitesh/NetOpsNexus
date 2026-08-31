# NetOps Nexus — Enterprise RBAC & Security Guide

## Role-Based Access Control Matrix

NetOps Nexus enforces 7 discrete enterprise roles with granular permissions checked on every REST and WebSocket API invocation.

| Permission / Action | Super Admin | Network Admin | Network Engineer | Security Engineer | NOC Engineer | Auditor | Read Only |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `devices.read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `devices.write` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `devices.delete` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `discovery.run` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `configs.read` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `configs.deploy` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `configs.rollback` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `ipam.read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ipam.write` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `automation.read`| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `automation.execute` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `incidents.create` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `incidents.assign` | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `security.read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `security.write` | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `diagnostics.run` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `reports.export` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `audit.read` | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| `rbac.write` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## Security Hardening
- Passwords are encrypted using modern `bcrypt` key derivation with configurable rounds.
- JWT tokens expire automatically and support instant revocation.
- Every state mutation triggers a structured, immutable audit log entry containing the user ID, client IP, action name, target entity, before/after diffs, and timestamp.
