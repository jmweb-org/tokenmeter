"""Token counting behind a small interface.

The real encoder uses ``tiktoken``, imported lazily so the package installs and
imports without it and so the test suite can run with a fake encoder and no
network access. Counting is therefore exact for the supported OpenAI encodings
at run time, and deterministic in tests.
"""

from __future__ import annotations

from typing import Protocol

from tokenmeter.pricing import price_for


class Encoder(Protocol):
    def count(self, text: str) -> int: ...


class EncoderError(RuntimeError):
    """Raised when an encoder cannot be constructed."""


class TiktokenEncoder:
    """Count tokens with tiktoken for a given encoding name."""

    def __init__(self, encoding: str) -> None:
        self.encoding = encoding
        self._enc = None

    def _ensure(self):
        if self._enc is not None:
            return self._enc
        try:
            import tiktoken
        except ImportError as exc:  # pragma: no cover - import guard
            raise EncoderError(
                "tiktoken is not installed; install tokenmeter with its default "
                "dependencies to count tokens"
            ) from exc
        try:
            self._enc = tiktoken.get_encoding(self.encoding)
        except Exception as exc:  # pragma: no cover - needs network on first use
            raise EncoderError(f"could not load encoding {self.encoding!r}") from exc
        return self._enc

    def count(self, text: str) -> int:
        return len(self._ensure().encode(text))


def encoder_for_model(model: str) -> Encoder:
    return TiktokenEncoder(price_for(model).encoding)
