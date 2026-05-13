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

REQUIRED_NODE_NAMES = [
    "Lock Decision",
    "IF Should Attempt Lock",
    "更新公司状态为发送中",
    "重新读取公司记录",
    "Verify Lock",
    "IF Lock Confirmed",
    "No-op Response",
]

SEND_PATTERNS = [
    re.compile(r"发送开发信", re.I),
    re.compile(r"dry\s*run.*send", re.I),
    re.compile(r"\bsmtp\b", re.I),
    re.compile(r"\bemail\s*send\b", re.I),
    re.compile(r"\bemailSend\b", re.I),
]

WRITE_PATTERNS = [
    re.compile(r"写入发送记录", re.I),
    re.compile(r"更新公司状态", re.I),
    re.compile(r"更新联系人状态", re.I),
    re.compile(r"update.*status", re.I),
    re.compile(r"send\s*log", re.I),
]

SENSITIVE_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "bearer token": re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"),
    "webhook path": re.compile(r"(?i)/webhook(?:-test)?/[A-Za-z0-9._~:/?#[\]@!$&'()*+,;=%-]{8,}"),
    "ipv4 address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "possible table id": re.compile(r"\btbl[A-Za-z0-9]{8,}\b"),
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


def load_workflow(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("workflow JSON root must be an object")
    return data


def get_nodes(workflow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = workflow.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("workflow JSON must include a nodes list")
    return {node["name"]: node for node in nodes if isinstance(node, dict) and isinstance(node.get("name"), str)}


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
        if matches(name, SEND_PATTERNS) or "emailsend" in str(node.get("type", "")).lower() or "smtp" in str(node.get("type", "")).lower()
    ]


def find_write_nodes(nodes: dict[str, dict[str, Any]]) -> list[str]:
    return [name for name in nodes if matches(name, WRITE_PATTERNS)]


def true_edges(edges: list[Edge], source: str) -> list[Edge]:
    return [edge for edge in edges if edge.source == source and edge.output_index == 0]


def false_edges(edges: list[Edge], source: str) -> list[Edge]:
    return [edge for edge in edges if edge.source == source and edge.output_index != 0]


def run_checks(workflow: dict[str, Any]) -> tuple[str, list[Finding], dict[str, Any]]:
    nodes = get_nodes(workflow)
    edges = build_edges(workflow)
    starts = find_start_nodes(nodes, edges)
    sends = find_send_nodes(nodes)
    writes = find_write_nodes(nodes)
    findings: list[Finding] = []

    for required in REQUIRED_NODE_NAMES:
        if required not in nodes:
            findings.append(Finding("FAIL", f"Required node missing: {required}"))

    if not sends:
        findings.append(Finding("WARN", "No send-equivalent node detected; verify send path manually."))
    if not writes:
        findings.append(Finding("WARN", "No writeback/send-log node detected; verify writeback path manually."))

    if "IF Lock Confirmed" in nodes:
        t_edges = true_edges(edges, "IF Lock Confirmed")
        f_edges = false_edges(edges, "IF Lock Confirmed")
        if not t_edges:
            findings.append(Finding("FAIL", "IF Lock Confirmed has no True/output-0 branch."))
        if not f_edges:
            findings.append(Finding("WARN", "IF Lock Confirmed has no explicit False/non-zero branch."))
        true_reachable = reachable_from([edge.target for edge in t_edges], edges)
        false_reachable = reachable_from([edge.target for edge in f_edges], edges)
        bypass_reachable = reachable_from(starts, edges, {(edge.source, edge.target, edge.output_index) for edge in t_edges})
        for send in sends:
            if send not in true_reachable:
                findings.append(Finding("FAIL", f"Send node is not reachable from IF Lock Confirmed True branch: {send}"))
            if send in false_reachable:
                findings.append(Finding("FAIL", f"Send node is reachable from IF Lock Confirmed False branch: {send}"))
            if send in bypass_reachable:
                findings.append(Finding("FAIL", f"Potential bypass reaches send without confirmed-lock True branch: {send}"))

    if "No-op Response" in nodes:
        noop_reachable = reachable_from(["No-op Response"], edges)
        for target in sorted(set(sends + writes) & noop_reachable):
            findings.append(Finding("FAIL", f"No-op Response can reach send/writeback node: {target}"))
    else:
        findings.append(Finding("FAIL", "No-op Response node missing."))

    if "IF Should Attempt Lock" in nodes:
        blocked = reachable_from([edge.target for edge in false_edges(edges, "IF Should Attempt Lock")], edges)
        for send in sends:
            if send in blocked:
                findings.append(Finding("FAIL", f"IF Should Attempt Lock blocked branch can reach send node: {send}"))
    else:
        findings.append(Finding("FAIL", "IF Should Attempt Lock node missing."))

    text = json.dumps(workflow, ensure_ascii=False, sort_keys=True)
    for label, pattern in SENSITIVE_PATTERNS.items():
        count = len(pattern.findall(text))
        if count:
            findings.append(Finding("WARN", f"Potential sensitive residue detected: {label} ({count} match(es)); values not printed."))

    fail_count = sum(1 for item in findings if item.level == "FAIL")
    warn_count = sum(1 for item in findings if item.level == "WARN")
    status = "FAIL" if fail_count else "WARN" if warn_count else "PASS"
    details = {"node_count": len(nodes), "edge_count": len(edges), "send_nodes": sends, "write_nodes": writes, "fail_count": fail_count, "warn_count": warn_count}
    return status, findings, details


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline n8n Outreach idempotency checker.")
    parser.add_argument("workflow_json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        status, findings, details = run_checks(load_workflow(Path(args.workflow_json)))
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
            print("Send nodes: " + (", ".join(details["send_nodes"]) if details["send_nodes"] else "<none detected>"))
            print("Writeback nodes: " + (", ".join(details["write_nodes"]) if details["write_nodes"] else "<none detected>"))
        for finding in findings:
            print(f"{finding.level}: {finding.message}")

    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
