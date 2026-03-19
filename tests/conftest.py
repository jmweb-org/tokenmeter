from __future__ import annotations

import pytest

from tokenmeter.encoder import Encoder


class WordEncoder(Encoder):
    """A deterministic fake encoder: one token per whitespace-separated word.

    Keeps tests free of tiktoken and network access while exercising all the
    counting, pricing and budget logic.
    """

    def count(self, text: str) -> int:
        return len(text.split())


@pytest.fixture
def encoder():
    return WordEncoder()
