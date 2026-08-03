"""Test della configurazione del logging (M1-T4).

Il test più importante è quello sull'idempotenza: Streamlit riesegue lo script
a ogni interazione, e un `configura()` non protetto moltiplicherebbe gli
handler — quindi le righe di log — a ogni click dell'utente.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from beewatch import logging_config
from beewatch.logging_config import NOME_LOGGER, configura, ottieni_logger

pytestmark = pytest.mark.usefixtures("logging_azzerato")


def nostri(logger: logging.Logger) -> list[logging.Handler]:
    """Solo gli handler installati da BeeWatch.

    pytest e Streamlit aggiungono i propri handler allo stesso logger: contarli
    tutti renderebbe i test dipendenti da strumenti esterni.
    """
    return logging_config._nostri_handler(logger)


def test_configura_installa_terminale_e_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(logging_config, "CARTELLA_LOG", tmp_path / "logs")
    monkeypatch.setattr(logging_config, "FILE_LOG", tmp_path / "logs" / "beewatch.log")

    radice = configura(livello="INFO")

    assert len(nostri(radice)) == 2
    assert (tmp_path / "logs" / "beewatch.log").exists()


def test_senza_file_resta_solo_il_terminale() -> None:
    radice = configura(livello="INFO", su_file=False)
    assert len(nostri(radice)) == 1
    assert isinstance(nostri(radice)[0], logging.StreamHandler)


def test_configura_e_idempotente() -> None:
    """Dieci riesecuzioni di Streamlit non devono produrre dieci handler."""
    radice = configura(livello="INFO", su_file=False)
    for _ in range(10):
        configura(livello="INFO", su_file=False)
    assert len(nostri(radice)) == 1


def test_il_livello_richiesto_viene_applicato() -> None:
    radice = configura(livello="WARNING", su_file=False)
    assert radice.level == logging.WARNING
    assert radice.isEnabledFor(logging.WARNING)
    assert not radice.isEnabledFor(logging.INFO)


def test_il_livello_arriva_dalla_configurazione(monkeypatch) -> None:
    """Senza argomento, il livello è quello di LOG_LEVEL nel file `.env`."""
    finta = type("FintaConfig", (), {"livello_log": "ERROR"})()
    monkeypatch.setattr(logging_config, "ottieni", lambda: finta)

    assert configura(su_file=False).level == logging.ERROR


def test_non_propaga_al_logger_root() -> None:
    """Streamlit configura il root: propagando, ogni riga uscirebbe due volte."""
    assert configura(livello="INFO", su_file=False).propagate is False


def test_ottieni_logger_restituisce_un_figlio() -> None:
    configura(livello="INFO", su_file=False)
    figlio = ottieni_logger("beewatch.database.repository")

    assert figlio.name.startswith(NOME_LOGGER)
    assert figlio.getEffectiveLevel() == logging.INFO


def test_il_messaggio_finisce_nel_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(logging_config, "CARTELLA_LOG", tmp_path / "logs")
    monkeypatch.setattr(logging_config, "FILE_LOG", tmp_path / "logs" / "beewatch.log")
    configura(livello="INFO")

    ottieni_logger("beewatch.ml.previsione").warning("modello assente")
    for handler in nostri(logging.getLogger(NOME_LOGGER)):
        handler.flush()

    contenuto = (tmp_path / "logs" / "beewatch.log").read_text(encoding="utf-8")
    assert "modello assente" in contenuto
    assert "WARNING" in contenuto
    assert "beewatch.ml.previsione" in contenuto


def test_le_librerie_rumorose_sono_silenziate() -> None:
    configura(livello="DEBUG", su_file=False)
    for nome in logging_config.LIBRERIE_SILENZIATE:
        assert logging.getLogger(nome).level == logging.WARNING
