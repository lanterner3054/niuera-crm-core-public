#!/usr/bin/env python3
"""Offline n8n Outreach approval idempotency checker.

Public sanitized version. Reads only a local exported n8n workflow JSON file and
prints PASS / WARN / FAIL. It does not call n8n, Feishu, Dify, MCP, SMTP, IMAP,
production servers, or any network API.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NATIVE_IF_TYPE = "n8n-nodes-base.if"

DEFAULT_REQUIRED_NODE_NAMES = [
    "Lock Decision",
    "IF Should Attempt Lock",
    "Update record to sending",
    "Re-read record",
    "Verify Lock",
    "No-op Response",
]

DEFAULT_LOCK_GATE_PATTERN = r"^IF .*Lock Confirmed$|^IF Lock Confirmed$"
DEFAULT_LOCK_ATTEMPT_NODE = "IF Should Attempt Lock"

SEND_PATTERNS = [
    re.compile(r"发送开发信", re.I),
    re.compile(r"dry\s*run.*send", re.I),
    re.compile(r"\bsmtp\b", re.I),
    re.compile(r"\bemail\s*send\b", re.I),
    re.compile(r"\bemailSend\b", re.I),
]

WRITE_PATTERNS = [
    re.compile(r"写入发送记录", re.I),
    re.compile(r"\bwriteback\b", re.I),
    re.compile(r"update.*company.*status", re.I),
    re.compile(r"update.*contact.*status", re.I),
    re.compile(r"update.*status", re.I),
    re.compile(r"send\s*log", re.I),
]

SENSITIVE_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "bearer token": re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
    "webhook path": re.compile(r"(?i)/webhook(?:-test)?/[A-Za-z0-9._~:/?#[\]@!$&'()*+,;=%-]{8,}"),
    "ipv4 address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "possible table id": re.compile(r"\btbl[A-Za-z0-9]{8,}\b"),
    "possible app id": re.compile(r"\bcli_[A-Za-z0-9]{8,}\b"),
    "possible app key": re.compile(r"\bapp-[A-Za-z0-9]{12,}\b"),
    "long opaque id": re.compile(r"\b[A-Za-z0-9_-]{32,}\b"),
}


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    output_index: int


@dataclass
class Finding:
    level: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline n8n Outreach idempotency checker.")
    parser.add_argument("workflow_json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero for WARN as well as FAIL, useful for CI gates.",
    )
    parser.add_argument(
        "--required-node",
        action="append",
        default=None,
        help="Required node name. Can be repeated. Defaults to public generic idempotency node names.",
    )
    parser.add_argument(
        "--lock-gate-pattern",
        default=DEFAULT_LOCK_GATE_PATTERN,
        help="Regex used to find all native IF lock-confirmed gate nodes.",
    )
    parser.add_argument(
        "--lock-attempt-node",
        default=DEFAULT_LOCK_ATTEMPT_NODE,
        help="Native IF node that decides whether to attempt the lock.",
    )
    return parser.parse_args()


def load_workflow(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("workflow JSON root must be an object")
    return data


def get_nodes(workflow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = workflow.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("workflow JSON must include a nodes list")
    result: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if isinstance(node, dict) and isinstance(node.get("name"), str):
            result[node["name"]] = node
    return result


def build_edges(workflow: dict[str, Any]) -> list[Edge]:
    edges: list[Edge] = []
    connections = workflow.get("connections", {})
    if not isinstance(connections, dict):
        return edges
    for source, source_connections in connections.items():
        if not isinstance(source_connections, dict):
            continue
        main_outputs = source_connections.get("main", [])
        if not isinstance(main_outputs, list):
            continue
        for output_index, output_connections in enumerate(main_outputs):
            if not isinstance(output_connections, list):
                continue
            for connection in output_connections:
                if isinstance(connection, dict) and isinstance(connection.get("node"), str):
                    edges.append(Edge(source, connection["node"], output_index))
    return edges


def reachable_from(starts: list[str], edges: list[Edge], excluded: set[tuple[str, str, int]] | None = None) -> set[str]:
    excluded = excluded or set()
    graph: dict[str, list[Edge]] = defaultdict(list)
    for edge in edges:
        if (edge.source, edge.target, edge.output_index) not in excluded:
            graph[edge.source].append(edge)
    seen: set[str] = set()
    queue = deque(starts)
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(edge.target for edge in graph.get(node, []) if edge.target not in seen)
    return seen


def find_start_nodes(nodes: dict[str, dict[str, Any]], edges: list[Edge]) -> list[str]:
    incoming = {edge.target for edge in edges}
    trigger_nodes = [
        name for name, node in nodes.items()
        if "trigger" in str(node.get("type", "")).lower() or "webhook" in str(node.get("type", "")).lower()
    ]
    return trigger_nodes or [name for name in nodes if name not in incoming] or list(nodes)


def matches(name: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(name) for pattern in patterns)


def find_send_nodes(nodes: dict[str, dict[str, Any]]) -> list[str]:
    return [
        name for name, node in nodes.items()
        if matches(name, SEND_PATTERNS)
        or "emailsend" in str(node.get("type", "")).lower()
        or "smtp" in str(node.get("type", "")).lower()
    ]


def find_write_nodes(nodes: dict[str, dict[str, Any]]) -> list[str]:
    return [name for name in nodes if matches(name, WRITE_PATTERNS)]


def out_edges(edges: list[Edge], source: str, output_index: int | None = None) -> list[Edge]:
    return [
        edge for edge in edges
        if edge.source == source and (output_index is None or edge.output_index == output_index)
    ]


def non_true_edges(edges: list[Edge], source: str) -> list[Edge]:
    return [edge for edge in edges if edge.source == source and edge.output_index != 0]


def is_native_if_node(node: dict[str, Any]) -> bool:
    return str(node.get("type", "")) == NATIVE_IF_TYPE


def find_lock_gates(nodes: dict[str, dict[str, Any]], pattern: str) -> list[str]:
    compiled = re.compile(pattern)
    return [name for name in nodes if compiled.search(name)]


def check_sensitive_residue(workflow: dict[str, Any]) -> list[Finding]:
    text = json.dumps(workflow, ensure_ascii=False, sort_keys=True)
    findings: list[Finding] = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        count = len(pattern.findall(text))
        if count:
            findings.append(Finding("WARN", f"Potential sensitive residue detected: {label} ({count} match(es)); values not printed."))
    return findings


def check_if_node_type(nodes: dict[str, dict[str, Any]], node_name: str, findings: list[Finding]) -> None:
    node = nodes.get(node_name)
    if not node:
        return
    if not is_native_if_node(node):
        found = str(node.get("type", "<missing>"))
        findings.append(Finding("FAIL", f"{node_name} must be a native n8n IF node ({NATIVE_IF_TYPE}); found type={found}"))


def run_checks(
    workflow: dict[str, Any],
    required_nodes: list[str],
    lock_gate_pattern: str,
    lock_attempt_node: str,
) -> tuple[str, list[Finding], dict[str, Any]]:
    nodes = get_nodes(workflow)
    edges = build_edges(workflow)
    starts = find_start_nodes(nodes, edges)
    sends = find_send_nodes(nodes)
    writes = find_write_nodes(nodes)
    protected_targets = sorted(set(sends + writes))
    findings: list[Finding] = []

    for required in required_nodes:
        if required not in nodes:
            findings.append(Finding("FAIL", f"Required node missing: {required}"))

    if lock_attempt_node not in nodes:
        findings.append(Finding("FAIL", f"Lock-attempt IF node missing: {lock_attempt_node}"))
    else:
        check_if_node_type(nodes, lock_attempt_node, findings)

    lock_gates = find_lock_gates(nodes, lock_gate_pattern)
    if not lock_gates:
        findings.append(Finding("FAIL", f"No lock-confirmed IF gate matched pattern: {lock_gate_pattern}"))
    for gate in lock_gates:
        check_if_node_type(nodes, gate, findings)

    if not sends:
        findings.append(Finding("WARN", "No send-equivalent node detected; verify send path manually."))
    if not writes:
        findings.append(Finding("WARN", "No writeback/send-log node detected; verify writeback path manually."))

    all_gate_true_edges: list[Edge] = []
    send_reachable_from_any_true: set[str] = set()
    write_reachable_from_any_true: set[str] = set()

    for gate in lock_gates:
        gate_true_edges = out_edges(edges, gate, 0)
        gate_false_edges = non_true_edges(edges, gate)
        all_gate_true_edges.extend(gate_true_edges)

        if not gate_true_edges:
            findings.append(Finding("FAIL", f"{gate} has no True/output-0 branch."))
        if not gate_false_edges:
            findings.append(Finding("WARN", f"{gate} has no explicit False/non-zero branch."))

        true_reachable = reachable_from([edge.target for edge in gate_true_edges], edges)
        false_reachable = reachable_from([edge.target for edge in gate_false_edges], edges)
        send_reachable_from_any_true.update(set(sends) & true_reachable)
        write_reachable_from_any_true.update(set(writes) & true_reachable)

        for target in protected_targets:
            if target in false_reachable:
                findings.append(Finding("FAIL", f"Protected node is reachable from {gate} False/non-true branch: {target}"))

    true_edge_keys = {(edge.source, edge.target, edge.output_index) for edge in all_gate_true_edges}
    bypass_reachable = reachable_from(starts, edges, true_edge_keys)
    for send in sends:
        if send not in send_reachable_from_any_true:
            findings.append(Finding("FAIL", f"Send node is not reachable from any lock-confirmed True branch: {send}"))
        if send in bypass_reachable:
            findings.append(Finding("FAIL", f"Potential bypass reaches send without any confirmed-lock True branch: {send}"))
    for write in writes:
        if write in bypass_reachable:
            findings.append(Finding("FAIL", f"Potential bypass reaches writeback without any confirmed-lock True branch: {write}"))

    if "No-op Response" in nodes:
        noop_reachable = reachable_from(["No-op Response"], edges)
        for target in sorted(set(protected_targets) & noop_reachable):
            findings.append(Finding("FAIL", f"No-op Response can reach send/writeback node: {target}"))
    else:
        findings.append(Finding("FAIL", "No-op Response node missing."))

    if lock_attempt_node in nodes:
        blocked = reachable_from([edge.target for edge in non_true_edges(edges, lock_attempt_node)], edges)
        for target in protected_targets:
            if target in blocked:
                findings.append(Finding("FAIL", f"{lock_attempt_node} blocked branch can reach protected node: {target}"))

    findings.extend(check_sensitive_residue(workflow))

    fail_count = sum(1 for item in findings if item.level == "FAIL")
    warn_count = sum(1 for item in findings if item.level == "WARN")
    status = "FAIL" if fail_count else "WARN" if warn_count else "PASS"
    details = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "send_nodes": sends,
        "write_nodes": writes,
        "lock_gates": lock_gates,
        "fail_count": fail_count,
        "warn_count": warn_count,
    }
    return status, findings, details


def main() -> int:
    args = parse_args()
    required_nodes = args.required_node or DEFAULT_REQUIRED_NODE_NAMES

    try:
        status, findings, details = run_checks(
            load_workflow(Path(args.workflow_json)),
            required_nodes,
            args.lock_gate_pattern,
            args.lock_attempt_node,
        )
    except Exception as error:
        status = "FAIL"
        findings = [Finding("FAIL", f"Could not inspect workflow JSON: {error}")]
        details = {}

    if args.json:
        print(json.dumps({"status": status, "details": details, "findings": [item.__dict__ for item in findings]}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(status)
        if details:
            print(f"Nodes: {details['node_count']} | Edges: {details['edge_count']}")
            print("Lock gates: " + (", ".join(details["lock_gates"]) if details["lock_gates"] else "<none detected>"))
            print("Send nodes: " + (", ".join(details["send_nodes"]) if details["send_nodes"] else "<none detected>"))
            print("Writeback nodes: " + (", ".join(details["write_nodes"]) if details["write_nodes"] else "<none detected>"))
        for finding in findings:
            print(f"{finding.level}: {finding.message}")

    if status == "FAIL" or (status == "WARN" and args.strict):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
