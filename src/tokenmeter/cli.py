"""Command-line interface for tokenmeter."""

from __future__ import annotations

import json
import os
import sys

import typer
from rich.console import Console
from rich.table import Table

from tokenmeter import __version__
from tokenmeter.encoder import EncoderError, encoder_for_model
from tokenmeter.inputs import read_inputs
from tokenmeter.meter import measure, over_budget, total_cost
from tokenmeter.pricing import (
    PRICES_AS_OF,
    PriceFileError,
    UnknownModel,
    known_models,
    load_prices_file,
    price_for,
)
from tokenmeter.render import measurements_to_json, render_table

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Count tokens and estimate cost for prompts before you send them.",
)
_out = Console()
_err = Console(stderr=True)

EXIT_OK = 0
EXIT_OVER_BUDGET = 1
EXIT_BAD_INPUT = 2


def _version_callback(value: bool) -> None:
    if value:
        _out.print(f"tokenmeter {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """tokenmeter command-line interface."""


def _load_prices_or_exit(prices_file: str | None) -> None:
    prices_path = prices_file or os.environ.get("TOKENMETER_PRICES_FILE")
    if prices_path is None:
        return
    try:
        load_prices_file(prices_path)
    except PriceFileError as exc:
        _err.print(f"tokenmeter: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc


def _collect(paths, model, output_tokens):
    inputs = read_inputs(paths)
    encoder = encoder_for_model(model)
    return [
        measure(encoder, model, name, text, output_tokens=output_tokens) for name, text in inputs
    ]


@app.command("count")
def count(
    paths: list[str] = typer.Argument(..., help="Files, directories, or - for stdin."),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="Model to price against."),
    output_tokens: int = typer.Option(
        0, "--output-tokens", help="Assumed completion tokens, for cost only."
    ),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON."),
    prices_file: str | None = typer.Option(
        None,
        "--prices-file",
        help="JSON file with model prices to add or override.",
    ),
) -> None:
    """Count tokens and estimate cost for one or more inputs."""

    _load_prices_or_exit(prices_file)
    try:
        measurements = _collect(paths, model, output_tokens)
    except UnknownModel as exc:
        _err.print(f"tokenmeter: {exc}; try 'tokenmeter models'")
        raise typer.Exit(EXIT_BAD_INPUT) from exc
    except (OSError, EncoderError) as exc:
        _err.print(f"tokenmeter: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc

    if as_json:
        _out.print_json(json.dumps(measurements_to_json(measurements)))
    else:
        _out.print(render_table(measurements))


@app.command("budget")
def budget(
    paths: list[str] = typer.Argument(..., help="Files, directories, or - for stdin."),
    max_cost: float = typer.Option(..., "--max-cost", help="Fail above this USD cost."),
    model: str = typer.Option("gpt-4o", "--model", "-m", help="Model to price against."),
    output_tokens: int = typer.Option(0, "--output-tokens", help="Assumed completion tokens."),
    prices_file: str | None = typer.Option(
        None,
        "--prices-file",
        help="JSON file with model prices to add or override.",
    ),
) -> None:
    """Fail when the estimated cost of the inputs exceeds a budget."""

    _load_prices_or_exit(prices_file)
    try:
        measurements = _collect(paths, model, output_tokens)
    except UnknownModel as exc:
        _err.print(f"tokenmeter: {exc}; try 'tokenmeter models'")
        raise typer.Exit(EXIT_BAD_INPUT) from exc
    except (OSError, EncoderError) as exc:
        _err.print(f"tokenmeter: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc

    cost = total_cost(measurements)
    _err.print(f"tokenmeter: estimated ${cost:.6f} against a ${max_cost:.6f} budget")
    if over_budget(measurements, max_cost):
        raise typer.Exit(EXIT_OVER_BUDGET)


@app.command("models")
def models(
    prices_file: str | None = typer.Option(
        None,
        "--prices-file",
        help="JSON file with model prices to add or override.",
    ),
) -> None:
    """List the known models and their prices."""

    _load_prices_or_exit(prices_file)
    title = f"prices as of {PRICES_AS_OF} (USD per 1M tokens)"
    table = Table(box=None, pad_edge=False, title=title)
    table.add_column("model")
    table.add_column("encoding")
    table.add_column("input", justify="right")
    table.add_column("output", justify="right")
    for name in known_models():
        p = price_for(name)
        table.add_row(p.model, p.encoding, f"${p.input_per_mtok:g}", f"${p.output_per_mtok:g}")
    _out.print(table)


def entrypoint() -> None:
    try:
        app()
    except KeyboardInterrupt:  # pragma: no cover - interactive only
        print("tokenmeter: interrupted", file=sys.stderr)
        raise SystemExit(130) from None
