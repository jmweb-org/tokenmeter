from __future__ import annotations

import json

import pytest
from tests.conftest import WordEncoder
from typer.testing import CliRunner

from tokenmeter import __version__
from tokenmeter import cli as cli_module
from tokenmeter import encoder as encoder_module

runner = CliRunner()


@pytest.fixture(autouse=True)
def patch_encoder(monkeypatch):
    monkeypatch.setattr(cli_module, "encoder_for_model", lambda model: WordEncoder())
    monkeypatch.setattr(encoder_module, "encoder_for_model", lambda model: WordEncoder())


def test_version():
    result = runner.invoke(cli_module.app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_count_file_json(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("one two three four")
    result = runner.invoke(cli_module.app, ["count", str(f), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["total_tokens"] == 4
    assert payload["inputs"][0]["input_tokens"] == 4


def test_count_unknown_model_is_bad_input(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("hello")
    result = runner.invoke(cli_module.app, ["count", str(f), "--model", "nope"])
    assert result.exit_code == cli_module.EXIT_BAD_INPUT


def test_count_uses_custom_prices_file(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("one two three four")
    prices = tmp_path / "prices.json"
    prices.write_text(
        '{"local-model": {"encoding": "cl100k_base", "input_per_mtok": 1.0, '
        '"output_per_mtok": 3.0}}'
    )

    result = runner.invoke(
        cli_module.app,
        [
            "count",
            str(f),
            "--model",
            "local-model",
            "--output-tokens",
            "2",
            "--prices-file",
            str(prices),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["inputs"][0]["model"] == "local-model"
    assert payload["inputs"][0]["input_cost"] == 0.000004
    assert payload["inputs"][0]["output_cost"] == 0.000006
    assert payload["total_cost"] == 0.00001


def test_prices_file_schema_error_is_bad_input(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("hello")
    prices = tmp_path / "prices.json"
    prices.write_text('{"broken": {"encoding": "cl100k_base"}}')

    result = runner.invoke(
        cli_module.app,
        ["count", str(f), "--model", "broken", "--prices-file", str(prices)],
    )

    assert result.exit_code == cli_module.EXIT_BAD_INPUT
    assert "missing required" in result.stderr


def test_budget_passes_under_limit(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("one two three")
    result = runner.invoke(cli_module.app, ["budget", str(f), "--max-cost", "1.0"])
    assert result.exit_code == 0


def test_budget_fails_over_limit(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("word " * 100000)
    result = runner.invoke(cli_module.app, ["budget", str(f), "--max-cost", "0.0001"])
    assert result.exit_code == cli_module.EXIT_OVER_BUDGET


def test_models_lists_prices():
    result = runner.invoke(cli_module.app, ["models"])
    assert result.exit_code == 0
    assert "gpt-4o" in result.stdout
