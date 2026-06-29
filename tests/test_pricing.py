from __future__ import annotations

import pytest

from tokenmeter.pricing import (
    PriceFileError,
    UnknownModel,
    input_cost,
    known_models,
    load_prices_file,
    output_cost,
    price_for,
    total_cost,
)


def test_known_models_sorted_and_nonempty():
    models = known_models()
    assert models == sorted(models)
    assert "gpt-4o" in models


def test_price_for_unknown_model_raises():
    with pytest.raises(UnknownModel) as info:
        price_for("does-not-exist")
    assert "does-not-exist" in str(info.value)


def test_input_cost_scales_with_tokens():
    # gpt-4o input is $2.50 per million tokens.
    assert input_cost("gpt-4o", 1_000_000) == pytest.approx(2.50)
    assert input_cost("gpt-4o", 500_000) == pytest.approx(1.25)


def test_output_cost_uses_output_rate():
    assert output_cost("gpt-4o", 1_000_000) == pytest.approx(10.00)


def test_total_cost_adds_input_and_output():
    cost = total_cost("gpt-4o", 1_000_000, 1_000_000)
    assert cost == pytest.approx(12.50)


def test_embeddings_have_no_output_cost():
    assert output_cost("text-embedding-3-small", 1_000_000) == 0.0


def test_load_prices_file_adds_custom_model(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text(
        '{"custom-fast": {"encoding": "cl100k_base", "input_per_mtok": 1.25, '
        '"output_per_mtok": 2.5}}'
    )

    load_prices_file(prices)

    assert "custom-fast" in known_models()
    price = price_for("custom-fast")
    assert price.encoding == "cl100k_base"
    assert input_cost("custom-fast", 1_000_000) == pytest.approx(1.25)
    assert output_cost("custom-fast", 1_000_000) == pytest.approx(2.5)


def test_load_prices_file_rejects_bad_schema(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text('{"broken": {"encoding": "cl100k_base"}}')

    with pytest.raises(PriceFileError, match="missing required"):
        load_prices_file(prices)
