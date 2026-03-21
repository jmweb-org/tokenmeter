"""Combine token counts with prices into measurements and a budget gate."""

from __future__ import annotations

from dataclasses import dataclass

from tokenmeter.encoder import Encoder
from tokenmeter.pricing import input_cost, output_cost


@dataclass(frozen=True, slots=True)
class Measurement:
    name: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float

    @property
    def total_cost(self) -> float:
        return self.input_cost + self.output_cost

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def measure(
    encoder: Encoder,
    model: str,
    name: str,
    text: str,
    *,
    output_tokens: int = 0,
) -> Measurement:
    input_tokens = encoder.count(text)
    return Measurement(
        name=name,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost=input_cost(model, input_tokens),
        output_cost=output_cost(model, output_tokens),
    )


def total_cost(measurements: list[Measurement]) -> float:
    return sum(m.total_cost for m in measurements)


def total_tokens(measurements: list[Measurement]) -> int:
    return sum(m.total_tokens for m in measurements)


def over_budget(measurements: list[Measurement], max_cost: float) -> bool:
    return total_cost(measurements) > max_cost
