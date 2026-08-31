"""
Workflow DAG Execution Engine coordinating topological node execution order,
context variable interpolation, condition gates, and automated recovery actions.
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime, timezone
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.automation.models import Workflow, WorkflowRun, WorkflowStepLog, WorkflowRunStatus
from backend.app.automation.action_catalog import ActionCatalog
from backend.app.websocket_manager import ws_manager


class DagEngine:
    @staticmethod
    async def execute_workflow(db: AsyncSession, run: WorkflowRun, definition: Dict[str, Any]) -> WorkflowRun:
        """Execute a directed acyclic graph of automation steps."""
        run.status = WorkflowRunStatus.RUNNING
        await db.commit()

        nodes_data = definition.get("nodes", [])
        edges_data = definition.get("edges", [])

        # Build NetworkX DiGraph for dependency resolution
        G = nx.DiGraph()
        node_map = {}
        for n in nodes_data:
            node_id = n["id"]
            G.add_node(node_id)
            node_map[node_id] = n

        for e in edges_data:
            G.add_edge(e["source"], e["target"], condition=e.get("condition", "on_success"))

        # Find topological execution order
        try:
            execution_order = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            # Graph has cycles, run in natural node list order
            execution_order = [n["id"] for n in nodes_data]

        context_vars: Dict[str, Any] = {"trigger": run.trigger_payload or {}}
        overall_success = True
        failed_node_id = None

        for node_id in execution_order:
            node = node_map.get(node_id)
            if not node:
                continue

            node_type = node.get("type", "action")
            action_name = node.get("action_name")
            params = node.get("parameters", {}).copy()

            # Skip trigger node execution
            if node_type == "trigger":
                continue

            # Interpolate context variables in parameters
            interpolated_params = {}
            for k, v in params.items():
                if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                    var_key = v[2:-2].strip()
                    interpolated_params[k] = context_vars.get(var_key, v)
                else:
                    interpolated_params[k] = v

            start_time = time.time()
            step_status = "success"
            output_data = {}
            err_msg = None

            try:
                if node_type == "condition":
                    # Evaluate condition
                    field = interpolated_params.get("field")
                    expected = interpolated_params.get("expected")
                    actual = context_vars.get(field)
                    if actual != expected:
                        step_status = "skipped"
                elif action_name:
                    output_data = await ActionCatalog.execute_action(db, action_name, interpolated_params)
                    context_vars[node_id] = output_data

            except Exception as e:
                step_status = "failed"
                err_msg = str(e)
                overall_success = False
                failed_node_id = node_id

            exec_time_ms = round((time.time() - start_time) * 1000, 2)
            
            # Record step log
            step_log = WorkflowStepLog(
                run_id=run.id,
                node_id=node_id,
                node_type=node_type,
                action_name=action_name,
                status=step_status,
                input_params=interpolated_params,
                output_data=output_data,
                execution_time_ms=exec_time_ms,
                completed_at=datetime.now(timezone.utc),
            )
            db.add(step_log)
            await db.commit()

            # Broadcast step progress over WebSocket
            await ws_manager.broadcast_automation_step(
                run_id=run.id,
                node_id=node_id,
                status=step_status,
                output=str(output_data) if output_data else err_msg,
            )

            if step_status == "failed":
                break

        run.status = WorkflowRunStatus.SUCCESS if overall_success else WorkflowRunStatus.FAILED
        if not overall_success:
            run.error_message = f"Step '{failed_node_id}' failed execution."
        run.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(run)
        return run
