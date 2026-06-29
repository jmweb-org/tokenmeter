# tokenmeter

[![CI](https://github.com/jmweb-org/tokenmeter/actions/workflows/ci.yml/badge.svg)](https://github.com/jmweb-org/tokenmeter/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tokenmeter-cli.svg)](https://pypi.org/project/tokenmeter-cli/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Count tokens and estimate cost for prompts before you send them, from the
command line or as a CI budget gate.

Prompt templates grow, a few-shot example gets added, a retrieved context
balloons, and suddenly every call costs more than you thought. `tokenmeter`
gives you the exact token count and a dollar estimate up front, for a single
prompt or a whole directory of templates.

```console
$ tokenmeter count prompts/system.txt --model gpt-4o
input            in tok   out tok   cost (USD)
prompts/system.txt  812         0   $0.002030

$ tokenmeter count prompts/ --model gpt-4o-mini --json
```

## Install

```console
$ pip install tokenmeter-cli                 # from PyPI, once released
$ pip install git+https://github.com/jmweb-org/tokenmeter   # latest, available now
```

Token counting is exact for the supported OpenAI encodings via `tiktoken`.

## Usage

```console
$ tokenmeter count system.txt -m gpt-4o          # one file
$ tokenmeter count prompts/ -m gpt-4o-mini       # every text file in a directory
$ cat prompt.txt | tokenmeter count - -m gpt-4o  # standard input
$ tokenmeter count p.txt --output-tokens 500     # include an assumed completion
$ tokenmeter models                              # list models and prices
```

### JSON output

Pass `--json` to emit a machine-readable summary that scripts and CI jobs can parse:

```console
$ tokenmeter count prompts/system.txt --model gpt-4o --output-tokens 500 --json
{
  "inputs": [
    {
      "name": "prompts/system.txt",
      "model": "gpt-4o",
      "input_tokens": 812,
      "output_tokens": 500,
      "input_cost": 0.00203,
      "output_cost": 0.005,
      "total_cost": 0.00703
    }
  ],
  "total_tokens": 1312,
  "total_cost": 0.00703
}
```

The top-level object contains:

| Field | Type | Description |
| --- | --- | --- |
| `inputs` | array | One object per input file, directory entry, or stdin stream. |
| `total_tokens` | integer | Sum of input and assumed output tokens across all inputs. |
| `total_cost` | number | Estimated total USD cost across all inputs, rounded to 6 decimal places. |

Each `inputs[]` object contains:

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Input name, such as a file path or `-` for stdin. |
| `model` | string | Model used for token counting and pricing. |
| `input_tokens` | integer | Counted prompt/input tokens. |
| `output_tokens` | integer | Assumed completion tokens from `--output-tokens` (defaults to `0`). |
| `input_cost` | number | Estimated USD input-token cost, rounded to 6 decimal places. |
| `output_cost` | number | Estimated USD output-token cost, rounded to 6 decimal places. |
| `total_cost` | number | Estimated USD cost for the input, rounded to 6 decimal places. |

### As a budget gate

Fail a build when a prompt set would cost more than you allow:

```console
$ tokenmeter budget prompts/ --model gpt-4o --max-cost 0.05
```

```yaml
- run: tokenmeter budget prompts/ --model gpt-4o --max-cost 0.05
```

## Cost model

Counts are real tokens. Cost multiplies tokens by a per-model rate from a small,
dated price table (`tokenmeter models` prints it with its "as of" date). By
default only input tokens are counted; pass `--output-tokens N` to add an
assumed completion length to the estimate. Prices change, so treat the dollar
figures as estimates and update the table when they move.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Counted; under budget (or `count` was used) |
| 1 | `budget` estimate exceeded `--max-cost` |
| 2 | An input was missing, or the model is unknown |

## License

MIT. See [LICENSE](LICENSE).
