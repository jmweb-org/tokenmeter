from __future__ import annotations

import pytest

from tokenmeter.meter import measure, over_budget, total_cost, total_tokens


def test_measure_counts_input_tokens(encoder):
    m = measure(encoder, "gpt-4o", "p", "one two three four five")
    assert m.input_tokens == 5
    assert m.output_tokens == 0
    assert m.input_cost == pytest.approx(2.50 * 5 / 1_000_000)
    assert m.total_cost == m.input_cost


def test_measure_includes_output_tokens_in_cost(encoder):
    m = measure(encoder, "gpt-4o", "p", "one two", output_tokens=1_000)
    assert m.output_tokens == 1_000
    assert m.output_cost == pytest.approx(10.00 * 1_000 / 1_000_000)
    assert m.total_tokens == 1_002


def test_totals_across_measurements(encoder):
    ms = [
        measure(encoder, "gpt-4o", "a", "one two three"),
        measure(encoder, "gpt-4o", "b", "four five"),
    ]
    assert total_tokens(ms) == 5
    assert total_cost(ms) == pytest.approx(2.50 * 5 / 1_000_000)


def test_over_budget(encoder):
    ms = [measure(encoder, "gpt-4o", "a", "word " * 1_000_000)]
    assert over_budget(ms, max_cost=1.0) is True
    assert over_budget(ms, max_cost=100.0) is False
