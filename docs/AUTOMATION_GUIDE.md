# NetOps Nexus — Workflow Automation Engine

## 1. DAG Workflow Lifecycle

NetOps Nexus features a DAG-based (Directed Acyclic Graph) workflow engine for automated network operations:

```
[Trigger]
   │ (Webhook, Schedule, Alert, Manual, Config Drift)
   ▼
[Condition Evaluation]
   │ (Device Role == "access_switch", Packet Loss > 10%, Ping == Fail)
   ▼
[Pre-Validation Gate]
   │ (Check reachability, backup running config, verify credentials)
   ▼
[Action Execution]
   │ (Execute CLI snippet, restart interface, push ACL rule, capture logs)
   ▼
[Post-Verification Gate]
   │ (Verify BGP established, interface up, zero drops)
   ▼
┌───────────────────┴───────────────────┐
│ Success                               │ Failure
▼                                       ▼
[Create Audit Event]            [Automatic Rollback]
[Close Alert / Resolve Ticket]  [Dispatch P1 Incident]
```

## 2. Action Catalog

| Action Identifier | Parameters | Description |
| :--- | :--- | :--- |
| `cli.execute_command` | `device_id`, `command` | Execute arbitrary CLI command and capture output |
| `config.backup` | `device_id`, `label` | Take instantaneous configuration snapshot |
| `config.deploy_template` | `device_id`, `template_id`, `vars` | Render Jinja2 template and push configuration |
| `config.rollback` | `device_id`, `target_version_id` | Atomic revert to specified configuration version |
| `interface.set_state` | `device_id`, `interface_name`, `state` | Admin enable/disable interface (`no shutdown` / `shutdown`) |
| `diagnostic.run_ping` | `source_id`, `target_ip`, `count` | Run diagnostic ping and assert packet loss < threshold |
| `incident.create` | `title`, `severity`, `device_id` | Automatically open an incident ticket |
| `notification.webhook` | `url`, `payload`, `headers` | Dispatch HTTP POST webhook notification |
