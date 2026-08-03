"""Configurazione centralizzata di BeeWatch AI.

Unico punto di verità per la configurazione dell'applicazione. Legge le
variabili da `.env`, le valida all'avvio e fallisce subito con un messaggio
comprensibile se qualcosa manca o non è valido.

Perché fallire subito e non alla prima query:
    un errore di configurazione scoperto a metà di una demo è indistinguibile
    da un bug. Scoperto all'avvio, è una riga di messaggio.

Uso tipico:

    from beewatch.config import ottieni

    cfg = ottieni()
    print(cfg.database.host)

La configurazione viene letta una sola volta e messa in cache: `ottieni()` si
può chiamare da qualsiasi modulo senza costi.

Gli errori di configurazione sono segnalati con `ConfigError`, che vive in
`beewatch/exceptions.py` insieme al resto della gerarchia (M1-T4).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from beewatch.exceptions import ConfigError

# Radice del progetto: due livelli sopra questo file (beewatch/config.py).
RADICE = Path(__file__).resolve().parent.parent

PROVIDER_AMMESSI = ("ollama", "openrouter")
LIVELLI_LOG = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


# --------------------------------------------------------------------------- #
# Lettura e validazione delle singole variabili
# --------------------------------------------------------------------------- #
# Ogni funzione accumula gli errori nella lista `errori` invece di sollevare
# subito: l'eccezione arriva alla fine, con il quadro completo.


def _testo(nome: str, errori: list[str], predefinito: str | None = None) -> str:
    valore = os.getenv(nome, "").strip()
    if valore:
        return valore
    if predefinito is not None:
        return predefinito
    errori.append(f"{nome} è obbligatoria e non è impostata")
    return ""


def _intero(nome: str, errori: list[str], predefinito: int, minimo: int, massimo: int) -> int:
    grezzo = os.getenv(nome, "").strip()
    if not grezzo:
        return predefinito
    try:
        valore = int(grezzo)
    except ValueError:
        errori.append(f"{nome} deve essere un numero intero, trovato «{grezzo}»")
        return predefinito
    if not minimo <= valore <= massimo:
        errori.append(f"{nome} deve essere fra {minimo} e {massimo}, trovato {valore}")
        return predefinito
    return valore


def _scelta(nome: str, errori: list[str], ammessi: tuple[str, ...], predefinito: str) -> str:
    """Valore fra quelli ammessi, ignorando maiuscole e minuscole.

    Restituisce sempre la forma canonica: chi scrive `info` in .env ottiene
    `INFO`, che è la forma che il modulo logging si aspetta.
    """
    grezzo = os.getenv(nome, "").strip() or predefinito
    canoniche = {a.casefold(): a for a in ammessi}
    valore = canoniche.get(grezzo.casefold())
    if valore is None:
        errori.append(f"{nome} deve essere uno fra {', '.join(ammessi)}, trovato «{grezzo}»")
        return predefinito
    return valore


# --------------------------------------------------------------------------- #
# Sezioni di configurazione
# --------------------------------------------------------------------------- #
# I dataclass sono congelati: una volta caricata, la configurazione non si
# modifica. Se serve cambiarla, si cambia `.env` e si riavvia — così non
# esistono due verità contemporaneamente.


@dataclass(frozen=True)
class ConfigDatabase:
    """Credenziali e coordinate del database MySQL."""

    host: str
    porta: int
    nome: str
    utente: str
    password: str

    def descrizione(self) -> str:
        """Stringa sicura da mostrare nei log: la password non compare mai."""
        return f"mysql://{self.utente}:***@{self.host}:{self.porta}/{self.nome}"


@dataclass(frozen=True)
class ConfigLLM:
    """Provider e modello del linguaggio naturale."""

    provider: str
    modello: str
    api_key: str | None
    timeout: int

    @property
    def in_locale(self) -> bool:
        """True se il provider gira sulla macchina, senza inviare dati fuori."""
        return self.provider == "ollama"

    def descrizione(self) -> str:
        if self.in_locale:
            chiave = "non richiesta"
        else:
            chiave = "impostata" if self.api_key else "MANCANTE"
        return f"{self.modello} via {self.provider} (chiave: {chiave})"


@dataclass(frozen=True)
class Config:
    """Configurazione completa dell'applicazione."""

    database: ConfigDatabase
    llm: ConfigLLM
    percorso_modello: Path
    livello_log: str

    def riepilogo(self) -> str:
        """Riga di riepilogo per il log d'avvio. Non contiene segreti."""
        return (
            f"database={self.database.descrizione()}  ·  "
            f"llm={self.llm.descrizione()}  ·  "
            f"modello={self.percorso_modello}  ·  "
            f"log={self.livello_log}"
        )


# --------------------------------------------------------------------------- #
# Caricamento
# --------------------------------------------------------------------------- #


def carica(percorso_env: Path | None = None) -> Config:
    """Legge `.env`, valida tutto e restituisce la configurazione.

    Solleva `ConfigError` con l'elenco completo dei problemi se qualcosa manca
    o non è valido. Il parametro `percorso_env` serve ai test per puntare a un
    file diverso da quello di progetto.
    """
    env = percorso_env or (RADICE / ".env")
    # override=False: le variabili già presenti nell'ambiente (Docker, CI)
    # hanno la precedenza sul file .env di sviluppo.
    load_dotenv(env, override=False)

    errori: list[str] = []

    database = ConfigDatabase(
        host=_testo("DB_HOST", errori, "localhost"),
        porta=_intero("DB_PORT", errori, 3306, 1, 65535),
        nome=_testo("DB_NAME", errori),
        utente=_testo("DB_USER", errori),
        password=_testo("DB_PASSWORD", errori),
    )

    provider = _scelta("LLM_PROVIDER", errori, PROVIDER_AMMESSI, "ollama")
    api_key = os.getenv("LLM_API_KEY", "").strip() or None
    # Ollama gira in locale e non richiede chiave. OpenRouter sì: senza,
    # l'assistente fallirebbe alla prima richiesta invece che all'avvio.
    if provider == "openrouter" and not api_key:
        errori.append("LLM_API_KEY è obbligatoria quando LLM_PROVIDER è openrouter")

    llm = ConfigLLM(
        provider=provider,
        modello=_testo("LLM_MODEL", errori, "llama3.1:8b"),
        api_key=api_key,
        timeout=_intero("LLM_TIMEOUT", errori, 60, 5, 600),
    )

    percorso_modello = RADICE / os.getenv("MODEL_PATH", "models/produzione_v1.joblib").strip()
    livello_log = _scelta("LOG_LEVEL", errori, LIVELLI_LOG, "INFO")

    if errori:
        elenco = "\n".join(f"  · {e}" for e in errori)
        raise ConfigError(
            f"Configurazione non valida: {len(errori)} problema/i trovato/i.\n"
            f"{elenco}\n\n"
            f"File letto: {env}\n"
            f"Copia .env.example in .env e compila i valori mancanti."
        )

    return Config(
        database=database,
        llm=llm,
        percorso_modello=percorso_modello,
        livello_log=livello_log,
    )


@lru_cache(maxsize=1)
def ottieni() -> Config:
    """Configurazione dell'applicazione, letta una sola volta.

    È il punto di ingresso da usare ovunque nel progetto. La cache evita di
    rileggere `.env` a ogni chiamata; `ottieni.cache_clear()` la azzera nei test.
    """
    return carica()
