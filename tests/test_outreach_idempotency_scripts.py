"""Offline tests for public Outreach idempotency helper scripts.

The fixtures and inline workflows in this module are deliberately fake public data.
They do not require production services, environment variables, or private repos.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check_n8n_outreach_idempotency.py"
SANITIZE_SCRIPT = REPO_ROOT / "scripts" / "sanitize_n8n_workflow.py"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"
FAKE_RESIDUE_FIXTURE = FIXTURE_DIR / "fake_outreach_workflow_with_residue.json"


class ScriptTestCase(unittest.TestCase):
    script: Path

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.script.exists():
            raise unittest.SkipTest(
                f"{cls.script.relative_to(REPO_ROOT)} is not present; "
                "these tests are intended to run with the public PR #19 assets."
            )

    def run_cli(self, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            input=input_text,
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
            check=False,
        )


class CheckOutreachIdempotencyTests(ScriptTestCase):
    script = CHECK_SCRIPT

    def write_workflow(self, workflow: dict) -> Path:
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", prefix="fake-outreach-", delete=False, encoding="utf-8"
        )
        with handle:
            json.dump(workflow, handle, indent=2)
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return Path(handle.name)

    def workflow(
        self,
        *,
        send_from_true: bool = True,
        noop_to_side_effect: bool = False,
        gate_type: str = "n8n-nodes-base.if",
        additional_gate: bool = False,
        residue: bool = False,
    ) -> dict:
        nodes = [
            self.node("Start", "n8n-nodes-base.manualTrigger"),
            self.node("IF Should Attempt Lock", gate_type),
            self.node("Acquire Lock", "n8n-nodes-base.httpRequest"),
            self.node("IF Lock Confirmed", gate_type),
            self.node("Send Email", "n8n-nodes-base.emailSend"),
            self.node("Writeback Result", "n8n-nodes-base.httpRequest"),
            self.node("No-op Response", "n8n-nodes-base.respondToWebhook"),
        ]
        if additional_gate:
            nodes.append(self.node("IF Lock Confirmed Backup", "n8n-nodes-base.if"))

        connections = {
            "Start": {"main": [[{"node": "IF Should Attempt Lock", "type": "main", "index": 0}]]},
            "IF Should Attempt Lock": {
                "main": [
                    [{"node": "Acquire Lock", "type": "main", "index": 0}],
                    [{"node": "No-op Response", "type": "main", "index": 0}],
                ]
            },
            "Acquire Lock": {"main": [[{"node": "IF Lock Confirmed", "type": "main", "index": 0}]]},
            "IF Lock Confirmed": {"main": [[], [{"node": "No-op Response", "type": "main", "index": 0}]]},
            "Send Email": {"main": [[{"node": "Writeback Result", "type": "main", "index": 0}]]},
            "Writeback Result": {"main": [[]]},
            "No-op Response": {"main": [[]]},
        }
        if send_from_true:
            connections["IF Lock Confirmed"]["main"][0].append(
                {"node": "Send Email", "type": "main", "index": 0}
            )
        else:
            connections["Acquire Lock"]["main"][0].append(
                {"node": "Send Email", "type": "main", "index": 0}
            )
        if additional_gate:
            connections["IF Lock Confirmed"]["main"][0].append(
                {"node": "IF Lock Confirmed Backup", "type": "main", "index": 0}
            )
            connections["IF Lock Confirmed Backup"] = {
                "main": [[{"node": "Writeback Result", "type": "main", "index": 0}], []]
            }
        if noop_to_side_effect:
            connections["No-op Response"]["main"][0].append(
                {"node": "Writeback Result", "type": "main", "index": 0}
            )
        parameters = {"note": "dummy public fixture"}
        if residue:
            parameters.update(
                {
                    "token": "dummy-token-public-fixture",
                    "webhookUrl": "dummy-webhook.example.invalid/path/REDACTED",
                    "ownerEmail": "reviewer@example.invalid",
                }
            )
        nodes[0]["parameters"] = parameters
        return {"name": "Fake Outreach Idempotency Fixture", "nodes": nodes, "connections": connections}

    @staticmethod
    def node(name: str, node_type: str) -> dict:
        return {"id": f"dummy-{name.lower().replace(' ', '-')}", "name": name, "type": node_type, "parameters": {}}

    def test_passes_when_side_effects_only_follow_native_lock_confirmed_true_branch(self) -> None:
        result = self.run_cli(str(self.write_workflow(self.workflow())))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout + result.stderr)

    def test_fails_when_send_can_bypass_lock_confirmed_true_branch(self) -> None:
        result = self.run_cli(str(self.write_workflow(self.workflow(send_from_true=False))))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Send Email", result.stdout + result.stderr)

    def test_fails_when_noop_response_can_reach_side_effects(self) -> None:
        result = self.run_cli(str(self.write_workflow(self.workflow(noop_to_side_effect=True))))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No-op Response", result.stdout + result.stderr)

    def test_fails_when_required_if_gates_are_not_native_if_nodes(self) -> None:
        result = self.run_cli(str(self.write_workflow(self.workflow(gate_type="n8n-nodes-base.code"))))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("IF Lock Confirmed", result.stdout + result.stderr)
        self.assertIn("IF Should Attempt Lock", result.stdout + result.stderr)

    def test_allows_multiple_lock_confirmed_gates(self) -> None:
        result = self.run_cli(str(self.write_workflow(self.workflow(additional_gate=True))))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_sensitive_residue_warning_reports_categories_and_counts_only(self) -> None:
        result = self.run_cli(str(self.write_workflow(self.workflow(residue=True))))
        combined = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, combined)
        self.assertIn("WARN", combined)
        self.assertIn("token", combined.lower())
        self.assertIn("webhook", combined.lower())
        self.assertNotIn("dummy-token-public-fixture", combined)
        self.assertNotIn("dummy-webhook.example.invalid/path/REDACTED", combined)
        self.assertNotIn("reviewer@example.invalid", combined)

    def test_strict_returns_nonzero_when_warnings_exist(self) -> None:
        result = self.run_cli("--strict", str(self.write_workflow(self.workflow(residue=True))))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WARN", result.stdout + result.stderr)


class SanitizeN8nWorkflowTests(ScriptTestCase):
    script = SANITIZE_SCRIPT

    def test_removes_runtime_state_and_redacts_sensitive_public_fixture_values(self) -> None:
        result = self.run_cli("--stdout", str(FAKE_RESIDUE_FIXTURE))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        sanitized = json.loads(result.stdout)
        self.assertEqual(sanitized["name"], "Fake Outreach Review Fixture")
        self.assertEqual(sanitized["nodes"][0]["name"], "Manual Trigger")
        for removed_key in ("credentials", "pinData", "staticData", "runtimeData", "executionData", "binaryData"):
            self.assertNotIn(removed_key, sanitized)
        node = sanitized["nodes"][0]
        self.assertNotIn("credentials", node)
        serialized = json.dumps(sanitized, sort_keys=True)
        for raw_value in (
            "dummy-token-public-fixture",
            "dummy-webhook.example.invalid/path/REDACTED",
            "reviewer@example.invalid",
            "192.0.2.10",
            "tbl_dummy_public_fixture",
            "cli_dummy_public_fixture",
            "key_dummy_public_fixture",
            "rec_dummy_public_fixture",
            "Example Fixture Customer",
            "Example Fixture Contact",
            "Public fixture payload",
        ):
            self.assertNotIn(raw_value, serialized)
        self.assertIn("REDACTED", serialized)

    def test_aggregate_summary_hides_redacted_key_names(self) -> None:
        result = self.run_cli("--summary-format", "aggregate", "--check", str(FAKE_RESIDUE_FIXTURE))
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + result.stderr
        self.assertIn("redacted", combined.lower())
        for key_name in ("webhookUrl", "ownerEmail", "serverIp", "tableId", "appId", "appKey", "opaqueId"):
            self.assertNotIn(key_name, combined)

    def test_stdout_and_check_are_mutually_exclusive(self) -> None:
        result = self.run_cli("--stdout", "--check", str(FAKE_RESIDUE_FIXTURE))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not allowed", (result.stdout + result.stderr).lower())

    def test_normal_summary_does_not_print_complete_secret_values(self) -> None:
        result = self.run_cli("--check", str(FAKE_RESIDUE_FIXTURE))
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + result.stderr
        for raw_value in (
            "dummy-token-public-fixture",
            "dummy-webhook.example.invalid/path/REDACTED",
            "reviewer@example.invalid",
            "tbl_dummy_public_fixture",
            "Example Fixture Customer",
        ):
            self.assertNotIn(raw_value, combined)


if __name__ == "__main__":
    unittest.main()
