# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-26

### Added
- Docker image and a published container entry point.
- Continuous integration across Python 3.10, 3.11 and 3.12.
- Expanded documentation and usage examples.

## [0.1.0] - 2026-03-23

### Added
- `count` command: exact token counts for files, directories or stdin, with a
  per-model cost estimate.
- `budget` command: fail when the estimated cost exceeds a limit, for use as a
  CI gate.
- `models` command: list the known models and their dated prices.
- Token counting via tiktoken for the supported OpenAI encodings.

[0.2.0]: https://github.com/jmweb-org/tokenmeter/releases/tag/v0.2.0
[0.1.0]: https://github.com/jmweb-org/tokenmeter/releases/tag/v0.1.0
