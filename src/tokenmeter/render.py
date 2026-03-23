"""Render measurements for the terminal and as JSON."""

from __future__ import annotations

from rich.console import Group
from rich.table import Table

from tokenmeter.meter import Measurement, total_cost, total_tokens


def measurements_to_json(measurements: list[Measurement]) -> dict:
    return {
        "inputs": [
            {
                "name": m.name,
                "model": m.model,
                "input_tokens": m.input_tokens,
                "output_tokens": m.output_tokens,
                "input_cost": round(m.input_cost, 6),
                "output_cost": round(m.output_cost, 6),
                "total_cost": round(m.total_cost, 6),
            }
            for m in measurements
        ],
        "total_tokens": total_tokens(measurements),
        "total_cost": round(total_cost(measurements), 6),
    }


def render_table(measurements: list[Measurement]) -> Group:
    table = Table(box=None, pad_edge=False)
    table.add_column("input")
    table.add_column("in tok", justify="right")
    table.add_column("out tok", justify="right")
    table.add_column("cost (USD)", justify="right")
    for m in measurements:
        table.add_row(
            m.name,
            f"{m.input_tokens}",
            f"{m.output_tokens}",
            f"${m.total_cost:.6f}",
        )
    if len(measurements) != 1:
        table.add_section()
        table.add_row(
            "total",
            f"{sum(m.input_tokens for m in measurements)}",
            f"{sum(m.output_tokens for m in measurements)}",
            f"${total_cost(measurements):.6f}",
        )
    return Group(table)
