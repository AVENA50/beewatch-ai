"""
Configurazione centralizzata del logging.

Un solo punto in cui si decide *dove* finiscono i messaggi e *con che formato*.
I moduli non configurano nulla: chiedono il proprio logger e scrivono.

    from beewatch.logging_config import ottieni_logger

    logger = ottieni_logger(__name__)
    logger.info("Alveare %s aggiornato", codice)

Due destinazioni:

    - il terminale, per lo sviluppo e per la demo davanti al docente;
    - `logs/beewatch.log`, a rotazione, per ricostruire cosa è successo dopo.

Nota su Streamlit
-----------------
A ogni interazione dell'utente Streamlit riesegue lo script dall'inizio. Se
`configura()` non fosse idempotente, a ogni click aggiungerebbe un handler in
più e le righe di log si moltiplicherebbero (due, tre, dieci copie della stessa
riga). Per questo la funzione controlla se ha già lavorato e in tal caso esce
subito.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from beewatch.config import RADICE, ottieni

# --------------------------------------------------------------------------- #
# Costanti
# --------------------------------------------------------------------------- #

# Il nome del logger di pacchetto. Ogni modulo che chiama ottieni_logger(__name__)
# ottiene un figlio di questo (es. "beewatch.database.repository") e ne eredita
# livello e handler.
NOME_LOGGER = "beewatch"

FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FORMATO_DATA = "%Y-%m-%d %H:%M:%S"

CARTELLA_LOG = RADICE / "logs"
FILE_LOG = CARTELLA_LOG / "beewatch.log"

# Un file da 1 MB tiene circa 10.000 righe: abbastanza per una sessione di
# lavoro, poco abbastanza da restare leggibile. Ne conserviamo tre storici.
DIMENSIONE_MASSIMA_BYTE = 1_000_000
COPIE_STORICHE = 3

# Librerie di terze parti troppo loquaci quando il livello globale è DEBUG:
# senza questo, i messaggi dell'applicazione si perdono nel rumore.
LIBRERIE_SILENZIATE = ("urllib3", "httpx", "httpcore", "matplotlib", "PIL")


# --------------------------------------------------------------------------- #
# Configurazione
# --------------------------------------------------------------------------- #


def configura(livello: str | None = None, *, su_file: bool = True) -> logging.Logger:
    """Prepara il logger di pacchetto e restituisce il logger radice.

    Va chiamata una volta sola, il più presto possibile all'avvio
    dell'applicazione (in `app.py`, prima di qualunque altra cosa).

    Args:
        livello: forza un livello specifico. Se omesso si usa `LOG_LEVEL`
            dalla configurazione, cioè dal file `.env`.
        su_file: se False scrive solo a terminale. Serve ai test, che non
            devono sporcare `logs/`.

    Returns:
        Il logger di pacchetto, già configurato.
    """
    radice = logging.getLogger(NOME_LOGGER)

    # Guardia di idempotenza: se ci sono già handler, la configurazione è
    # stata fatta (vedi la nota su Streamlit in cima al modulo).
    if radice.handlers:
        return radice

    livello_effettivo = livello or ottieni().livello_log
    radice.setLevel(livello_effettivo)

    # Il logger di pacchetto non propaga al logger root: senza questo, in
    # presenza di una configurazione di root (Streamlit ne installa una) ogni
    # riga verrebbe stampata due volte.
    radice.propagate = False

    formattatore = logging.Formatter(FORMATO, FORMATO_DATA)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formattatore)
    radice.addHandler(console)

    if su_file:
        CARTELLA_LOG.mkdir(parents=True, exist_ok=True)
        su_disco = RotatingFileHandler(
            FILE_LOG,
            maxBytes=DIMENSIONE_MASSIMA_BYTE,
            backupCount=COPIE_STORICHE,
            encoding="utf-8",
        )
        su_disco.setFormatter(formattatore)
        radice.addHandler(su_disco)

    for nome_libreria in LIBRERIE_SILENZIATE:
        logging.getLogger(nome_libreria).setLevel(logging.WARNING)

    radice.debug(
        "Logging configurato: livello=%s, file=%s",
        livello_effettivo,
        FILE_LOG if su_file else "disattivato",
    )
    return radice


def ottieni_logger(nome: str) -> logging.Logger:
    """Logger da usare dentro un modulo.

    Uso previsto, in cima a ogni modulo che deve scrivere qualcosa:

        logger = ottieni_logger(__name__)

    Passando `__name__` il logger eredita automaticamente la configurazione
    del pacchetto e il messaggio porta con sé il modulo che l'ha prodotto.
    """
    return logging.getLogger(nome)


def azzera() -> None:
    """Rimuove gli handler del logger di pacchetto.

    Serve soltanto ai test, che devono poter riconfigurare il logging da capo
    fra un caso e l'altro. Non va chiamata dall'applicazione.
    """
    radice = logging.getLogger(NOME_LOGGER)
    for handler in list(radice.handlers):
        handler.close()
        radice.removeHandler(handler)
