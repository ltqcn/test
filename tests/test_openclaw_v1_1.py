from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.openclaw_v1_1 import build_v1_1_spec, load_spec_markdown


def test_spec_contains_panic_stop_section() -> None:
    markdown = load_spec_markdown()
    assert "一键安全按钮（Panic Stop）" in markdown


def test_required_layers_complete() -> None:
    spec = build_v1_1_spec()
    missing = spec.validate_minimum_layers(
        ["Tool Runtime", "Policy Engine", "Approval Gate", "Audit Ledger", "Sandbox / Isolation"]
    )
    assert missing == []


def test_high_risk_requires_approval() -> None:
    spec = build_v1_1_spec()
    high_risks = spec.high_risk_levels()
    assert {item.level for item in high_risks} == {"P2", "P3"}
    assert all(item.approval_required for item in high_risks)
