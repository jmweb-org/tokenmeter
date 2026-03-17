"""Per-model token prices and the cost arithmetic on top of them.

Prices are expressed in US dollars per million tokens and carry an "as of"
date so a stale table is obvious. The numbers are easy to override or extend;
the cost functions are pure and do not care where the rates came from.
"""

from __future__ import annotations

from dataclasses import dataclass

PRICES_AS_OF = "2025-08-01"


@dataclass(frozen=True, slots=True)
class ModelPrice:
    """Input and output price in USD per million tokens."""

    model: str
    encoding: str
    input_per_mtok: float
    output_per_mtok: float


# A small, explicit table. Values are USD per 1,000,000 tokens.
_PRICES: dict[str, ModelPrice] = {
    "gpt-4o": ModelPrice("gpt-4o", "o200k_base", 2.50, 10.00),
    "gpt-4o-mini": ModelPrice("gpt-4o-mini", "o200k_base", 0.15, 0.60),
    "gpt-4-turbo": ModelPrice("gpt-4-turbo", "cl100k_base", 10.00, 30.00),
    "gpt-3.5-turbo": ModelPrice("gpt-3.5-turbo", "cl100k_base", 0.50, 1.50),
    "text-embedding-3-small": ModelPrice("text-embedding-3-small", "cl100k_base", 0.02, 0.0),
    "text-embedding-3-large": ModelPrice("text-embedding-3-large", "cl100k_base", 0.13, 0.0),
}


class UnknownModel(KeyError):
    """Raised when a model has no entry in the price table."""

    def __init__(self, model: str) -> None:
        self.model = model
        super().__init__(model)

    def __str__(self) -> str:
        return f"unknown model: {self.model}"


def known_models() -> list[str]:
    return sorted(_PRICES)


def price_for(model: str) -> ModelPrice:
    try:
        return _PRICES[model]
    except KeyError as exc:
        raise UnknownModel(model) from exc


def input_cost(model: str, tokens: int) -> float:
    return price_for(model).input_per_mtok * tokens / 1_000_000


def output_cost(model: str, tokens: int) -> float:
    return price_for(model).output_per_mtok * tokens / 1_000_000


def total_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    return input_cost(model, input_tokens) + output_cost(model, output_tokens)
