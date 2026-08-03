"""Fixture condivise da tutti i test di BeeWatch AI.

Il problema che risolvono: la configurazione legge da `os.environ` e dal file
`.env` dello sviluppatore. Senza isolamento, gli stessi test passerebbero sul
computer di chi ha un `.env` completo e fallirebbero sulla CI, che non ce l'ha.
Qui l'ambiente viene azzerato e ricostruito caso per caso.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from beewatch import logging_config
from beewatch.config import ottieni

# Tutte le variabili lette da beewatch.config. Vanno tolte dall'ambiente prima
# di ogni test, altrimenti il .env dello sviluppatore falsa il risultato.
VARIABILI_BEEWATCH = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_API_KEY",
    "LLM_TIMEOUT",
    "MODEL_PATH",
    "LOG_LEVEL",
)


@pytest.fixture
def ambiente_pulito(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rimuove ogni variabile BeeWatch dall'ambiente e azzera la cache.

    `ottieni()` è memorizzata con lru_cache: senza `cache_clear()` il secondo
    test riceverebbe la configurazione letta dal primo.
    """
    for nome in VARIABILI_BEEWATCH:
        monkeypatch.delenv(nome, raising=False)
    ottieni.cache_clear()
    yield
    ottieni.cache_clear()


@pytest.fixture
def scrivi_env(tmp_path: Path) -> Callable[..., Path]:
    """Fabbrica di file `.env` temporanei.

    Uso:
        percorso = scrivi_env(DB_NAME="x", DB_USER="y", DB_PASSWORD="z")
        config = carica(percorso)
    """

    def _scrivi(**valori: object) -> Path:
        percorso = tmp_path / ".env"
        righe = "\n".join(f"{chiave}={valore}" for chiave, valore in valori.items())
        percorso.write_text(righe + "\n", encoding="utf-8")
        return percorso

    return _scrivi


@pytest.fixture
def logging_azzerato() -> None:
    """Riporta il logging allo stato iniziale prima e dopo il test.

    Serve perché gli handler vivono a livello di modulo: senza azzeramento il
    secondo test troverebbe quelli installati dal primo e la verifica
    sull'idempotenza non proverebbe nulla.
    """
    logging_config.azzera()
    yield
    logging_config.azzera()
