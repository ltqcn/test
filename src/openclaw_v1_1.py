"""OpenClaw v1.1 spec-driven baseline module.

This module keeps the v1.1 specification as data and provides lightweight
validators that can be reused by scripts/CI checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

SPEC_FILE = Path(__file__).resolve().parent.parent / "docs" / "openclaw_spec_v1.md"


@dataclass(frozen=True)
class MetricTarget:
    name: str
    target: str


@dataclass(frozen=True)
class SecurityGate:
    level: str
    description: str
    approval_required: bool


@dataclass
class OpenClawSpec:
    version: str
    status: str
    objective: str
    p0_browser_requirement: str
    required_layers: tuple[str, ...]
    success_metrics: tuple[MetricTarget, ...]
    risk_levels: tuple[SecurityGate, ...]
    raw_markdown: str = field(repr=False)

    def validate_minimum_layers(self, observed_layers: Iterable[str]) -> list[str]:
        observed = set(observed_layers)
        return [layer for layer in self.required_layers if layer not in observed]

    def high_risk_levels(self) -> tuple[SecurityGate, ...]:
        return tuple(g for g in self.risk_levels if g.level in {"P2", "P3"})


def load_spec_markdown() -> str:
    return SPEC_FILE.read_text(encoding="utf-8")


def build_v1_1_spec() -> OpenClawSpec:
    markdown = load_spec_markdown()
    return OpenClawSpec(
        version="v1.1",
        status="可实现草案（Implementation-ready Draft）",
        objective="在安全可信前提下交付具备 OpenClaw 级任务能力的单设备个人智能代理",
        p0_browser_requirement="网页填表必须稳定可用（多步骤、控件选择、上传、提交前校验）",
        required_layers=(
            "Tool Runtime",
            "Policy Engine",
            "Approval Gate",
            "Audit Ledger",
            "Sandbox / Isolation",
        ),
        success_metrics=(
            MetricTarget("周期任务按时触发率", ">=99%"),
            MetricTarget("端到端成功率", ">=85%"),
            MetricTarget("结果可直接使用率", ">=70%"),
            MetricTarget("高风险未授权执行", "=0"),
            MetricTarget("一键撤离完成率", "=100%"),
            MetricTarget("Panic Stop 生效延迟 P95", "<2秒"),
        ),
        risk_levels=(
            SecurityGate("P0", "只读查询", False),
            SecurityGate("P1", "本地写入", False),
            SecurityGate("P2", "外部写入/批量操作", True),
            SecurityGate("P3", "破坏性操作", True),
        ),
        raw_markdown=markdown,
    )


def summarize() -> str:
    spec = build_v1_1_spec()
    metrics = "\n".join(f"- {m.name}: {m.target}" for m in spec.success_metrics)
    return (
        f"OpenClaw {spec.version}\n"
        f"状态: {spec.status}\n"
        f"目标: {spec.objective}\n"
        f"P0浏览器要求: {spec.p0_browser_requirement}\n"
        f"关键指标:\n{metrics}"
    )


if __name__ == "__main__":
    print(summarize())
