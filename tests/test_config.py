"""Test della configurazione centralizzata (M1-T3).

Sono le stesse verifiche fatte a mano quando il modulo è nato, trasformate in
codice: ogni volta che qualcuno tocca `config.py`, girano da sole.

Tutti i test usano la fixture `ambiente_pulito`, che toglie le variabili
BeeWatch da `os.environ`. Senza, il `.env` dello sviluppatore renderebbe i
risultati diversi da quelli della CI.
"""

from __future__ import annotations

import dataclasses

import pytest

from beewatch.config import Config, carica, ottieni
from beewatch.exceptions import ConfigError

# Il minimo indispensabile perché la configurazione sia valida: le tre
# variabili che non hanno un valore predefinito.
MINIMI = {
    "DB_NAME": "beewatch_test",
    "DB_USER": "tester",
    "DB_PASSWORD": "segreta",
}

pytestmark = pytest.mark.usefixtures("ambiente_pulito")


# --------------------------------------------------------------------------- #
# Caso felice
# --------------------------------------------------------------------------- #


def test_configurazione_completa(scrivi_env) -> None:
    percorso = scrivi_env(
        DB_HOST="db.example.com",
        DB_PORT=3307,
        DB_NAME="apiario",
        DB_USER="mario",
        DB_PASSWORD="segreta",
        LLM_PROVIDER="ollama",
        LLM_MODEL="llama3.1:8b",
        LLM_TIMEOUT=90,
        LOG_LEVEL="DEBUG",
    )
    config = carica(percorso)

    assert config.database.host == "db.example.com"
    assert config.database.porta == 3307
    assert config.database.nome == "apiario"
    assert config.llm.provider == "ollama"
    assert config.llm.timeout == 90
    assert config.livello_log == "DEBUG"


def test_valori_predefiniti(scrivi_env) -> None:
    """Chi compila solo le tre variabili obbligatorie deve ottenere un avvio valido."""
    config = carica(scrivi_env(**MINIMI))

    assert config.database.host == "localhost"
    assert config.database.porta == 3306
    assert config.llm.provider == "ollama"
    assert config.llm.timeout == 60
    assert config.livello_log == "INFO"
    assert config.percorso_modello.name == "produzione_v1.joblib"


# --------------------------------------------------------------------------- #
# Validazione: tutti gli errori insieme, non uno alla volta
# --------------------------------------------------------------------------- #


def test_variabili_obbligatorie_mancanti(scrivi_env) -> None:
    """L'eccezione elenca *tutti* i problemi: si correggono in un passaggio."""
    with pytest.raises(ConfigError) as info:
        carica(scrivi_env(DB_HOST="localhost"))

    messaggio = str(info.value)
    assert "DB_NAME" in messaggio
    assert "DB_USER" in messaggio
    assert "DB_PASSWORD" in messaggio
    assert "3 problema/i" in messaggio


def test_il_messaggio_dice_cosa_fare(scrivi_env) -> None:
    """Chi installa il progetto deve capire la soluzione senza leggere il codice."""
    with pytest.raises(ConfigError) as info:
        carica(scrivi_env())
    assert ".env.example" in str(info.value)


def test_porta_non_numerica(scrivi_env) -> None:
    with pytest.raises(ConfigError, match="DB_PORT"):
        carica(scrivi_env(**MINIMI, DB_PORT="tremilatrecentosei"))


def test_porta_fuori_intervallo(scrivi_env) -> None:
    with pytest.raises(ConfigError, match="65535"):
        carica(scrivi_env(**MINIMI, DB_PORT=70000))


def test_timeout_fuori_intervallo(scrivi_env) -> None:
    with pytest.raises(ConfigError, match="LLM_TIMEOUT"):
        carica(scrivi_env(**MINIMI, LLM_TIMEOUT=1))


def test_provider_non_ammesso(scrivi_env) -> None:
    with pytest.raises(ConfigError, match="LLM_PROVIDER"):
        carica(scrivi_env(**MINIMI, LLM_PROVIDER="chatgpt"))


def test_livello_log_non_ammesso(scrivi_env) -> None:
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        carica(scrivi_env(**MINIMI, LOG_LEVEL="VERBOSE"))


@pytest.mark.parametrize("scritto,atteso", [("info", "INFO"), ("Warning", "WARNING")])
def test_livello_log_insensibile_alle_maiuscole(scrivi_env, scritto: str, atteso: str) -> None:
    """Chi scrive `info` non deve essere punito: si restituisce la forma canonica."""
    assert carica(scrivi_env(**MINIMI, LOG_LEVEL=scritto)).livello_log == atteso


# --------------------------------------------------------------------------- #
# Regola specifica del provider LLM
# --------------------------------------------------------------------------- #


def test_openrouter_senza_chiave_fallisce_allavvio(scrivi_env) -> None:
    """Meglio fallire subito che alla prima domanda dell'utente in demo."""
    with pytest.raises(ConfigError, match="LLM_API_KEY"):
        carica(scrivi_env(**MINIMI, LLM_PROVIDER="openrouter"))


def test_openrouter_con_chiave(scrivi_env) -> None:
    config = carica(scrivi_env(**MINIMI, LLM_PROVIDER="openrouter", LLM_API_KEY="sk-finta"))
    assert config.llm.api_key == "sk-finta"
    assert config.llm.in_locale is False


def test_ollama_non_richiede_chiave(scrivi_env) -> None:
    config = carica(scrivi_env(**MINIMI))
    assert config.llm.api_key is None
    assert config.llm.in_locale is True


# --------------------------------------------------------------------------- #
# Segreti e immutabilità
# --------------------------------------------------------------------------- #


def test_la_password_non_compare_mai_nel_riepilogo(scrivi_env) -> None:
    """Il riepilogo finisce nel log d'avvio: deve essere sicuro da condividere."""
    config = carica(scrivi_env(**{**MINIMI, "DB_PASSWORD": "password_segretissima"}))
    riepilogo = config.riepilogo()

    assert "password_segretissima" not in riepilogo
    assert "***" in riepilogo


def test_la_chiave_api_non_compare_nel_riepilogo(scrivi_env) -> None:
    config = carica(scrivi_env(**MINIMI, LLM_PROVIDER="openrouter", LLM_API_KEY="sk-vera"))
    assert "sk-vera" not in config.riepilogo()


def test_la_configurazione_e_immutabile(scrivi_env) -> None:
    """Una sola verità: se serve cambiarla si modifica `.env` e si riavvia."""
    config = carica(scrivi_env(**MINIMI))
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.database.host = "altro"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Precedenza e cache
# --------------------------------------------------------------------------- #


def test_lambiente_ha_la_precedenza_sul_file(scrivi_env, monkeypatch) -> None:
    """In Docker e in CI le variabili arrivano dall'ambiente, non da `.env`."""
    monkeypatch.setenv("DB_NAME", "da_ambiente")
    config = carica(scrivi_env(**{**MINIMI, "DB_NAME": "da_file"}))
    assert config.database.nome == "da_ambiente"


def test_ottieni_legge_una_volta_sola(monkeypatch) -> None:
    """`ottieni()` si può chiamare ovunque senza costo: la cache lo garantisce."""
    for chiave, valore in MINIMI.items():
        monkeypatch.setenv(chiave, valore)
    ottieni.cache_clear()

    primo = ottieni()
    secondo = ottieni()

    assert isinstance(primo, Config)
    assert primo is secondo
