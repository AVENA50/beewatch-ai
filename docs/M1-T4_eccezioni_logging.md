# M1 - T4 · Eccezioni personalizzate e logging

## Obiettivo

Dotare il progetto di un modo unico e prevedibile di **segnalare** gli errori
(gerarchia di eccezioni) e di **registrarli** (logging configurato in un solo
punto), prima che il resto del codice cominci a inventarsi soluzioni locali.

È il requisito «gestione degli errori» richiesto dal docente, risolto a livello
di architettura invece che con `try/except` sparsi nei singoli file.

## Descrizione

La task introduce due moduli.

**`beewatch/exceptions.py`** definisce una radice comune, `BeeWatchError`, e
cinque sottoclassi che coprono i domini del progetto: configurazione, database,
validazione dei dati, modello di machine learning, modello di linguaggio.

Avere una radice unica permette all'interfaccia di distinguere in due righe i
problemi previsti dai bug:

```python
try:
    alveari = repository.elenca()
except BeeWatchError as errore:
    # problema previsto: l'utente legge un messaggio in italiano
    st.error(str(errore))
except Exception:
    # imprevisto: è un bug, va nel log con lo stack completo
    logger.exception("Errore non gestito")
    st.error("Errore imprevisto. Controlla il file di log.")
```

Il messaggio dell'eccezione è pensato per l'utente finale: niente nomi di
tabelle, niente traceback, niente gergo. I dettagli tecnici vanno nel log.

**`beewatch/logging_config.py`** configura il logger di pacchetto `beewatch`:
formato unico, livello letto da `LOG_LEVEL`, doppia destinazione (terminale e
`logs/beewatch.log` a rotazione). I moduli non configurano niente, chiedono il
loro logger con `ottieni_logger(__name__)` e scrivono.

## File coinvolti

| File | Azione |
|---|---|
| `beewatch/exceptions.py` | creato |
| `beewatch/logging_config.py` | creato |
| `beewatch/config.py` | modificato — `ConfigError` rimossa e importata da `exceptions.py` |
| `.gitignore` | modificato — aggiunta la riga `logs/` |
| `docs/M1-T4_eccezioni_logging.md` | creato |

Nessuna nuova dipendenza: `logging` fa parte della libreria standard.

## Funzionalità implementate

### Gerarchia delle eccezioni

| Eccezione | Quando si solleva |
|---|---|
| `BeeWatchError` | mai direttamente: è la radice da intercettare |
| `ConfigError` | configurazione assente o con valori non validi (M1-T3) |
| `DatabaseError` | connessione MySQL rifiutata, credenziali errate, query fallita |
| `ValidationError` | dato inserito dall'utente non valido; porta il nome del campo |
| `ModelError` | file `.joblib` mancante o incompatibile |
| `LLMError` | Ollama spento, chiave OpenRouter rifiutata, timeout, risposta malformata |

`ValidationError` accetta un secondo argomento `campo`, così il form che la
riceve può evidenziare la casella giusta invece di mostrare un messaggio
generico in cima alla pagina.

### Logging

- **Formato unico**: `data | LIVELLO | modulo | messaggio`. Il nome del modulo
  arriva gratis passando `__name__`, quindi si sa sempre chi ha scritto cosa.
- **Livello da `.env`**: `LOG_LEVEL=DEBUG` in sviluppo, `INFO` per la demo.
- **Due destinazioni**: terminale e `logs/beewatch.log`.
- **Rotazione**: 1 MB per file, tre copie storiche. Il log non cresce senza
  controllo e resta leggibile.
- **Librerie di terze parti silenziate** a `WARNING`: con `LOG_LEVEL=DEBUG`,
  `urllib3` e `PIL` da soli sommergerebbero i messaggi dell'applicazione.
- **Idempotenza**, spiegata sotto.

## Decisioni progettuali

**1. Perché una radice comune e non le eccezioni standard di Python.**
Con `ValueError` e `RuntimeError` l'interfaccia non può distinguere «il
database è spento» da «ho scritto una riga di codice sbagliata»: intercettare
`Exception` nasconderebbe i bug, non intercettare niente farebbe esplodere la
pagina. La radice comune risolve entrambi i casi con due `except`.

**2. Perché `configura()` è idempotente.**
Streamlit riesegue lo script dall'inizio a ogni interazione dell'utente. Senza
guardia, ogni click aggiungerebbe un handler e la stessa riga comparirebbe due,
tre, dieci volte. La funzione controlla `radice.handlers` ed esce subito se ha
già lavorato. È il tipo di bug che si scopre tardi e fa perdere un pomeriggio.

**3. Perché `propagate = False`.**
Streamlit installa una propria configurazione sul logger root. Lasciando la
propagazione attiva, ogni messaggio verrebbe stampato una volta dal nostro
handler e una seconda volta da quello di Streamlit, con formato diverso.

**4. Perché il logging dipende da `config` e non viceversa.**
`LOG_LEVEL` è una variabile d'ambiente come le altre, quindi appartiene a
`config.py`. La direzione della dipendenza è `logging_config → config →
exceptions`: nessun ciclo, e `exceptions.py` resta senza import.

**5. Perché `ConfigError` si sposta qui.**
In M1-T3 viveva dentro `config.py` come soluzione provvisoria, con una nota che
lo dichiarava. Ora trova la sua collocazione definitiva insieme alle altre.
`config.py` la importa, quindi il codice già scritto continua a funzionare
senza modifiche.

**6. Perché `logs/` non va su Git.**
Contiene dati di esecuzione della singola macchina, cambia a ogni avvio e
sporcherebbe ogni diff. La cartella viene creata a runtime da `configura()`.

## Definition of Done

| Verifica | Comando | Esito atteso |
|---|---|---|
| La gerarchia regge | `python -c "from beewatch.exceptions import *; assert issubclass(LLMError, BeeWatchError)"` | nessun output |
| Il logging scrive | `python -c "from beewatch.logging_config import configura; configura().info('prova')"` | riga formattata a terminale |
| Il file nasce | `type logs\beewatch.log` | contiene la stessa riga |
| Nessun duplicato | chiamare `configura()` cinque volte | sempre 2 handler |
| Il livello si rispetta | `configura(livello="WARNING")` poi `.info(...)` | nessun output |
| `logs/` è ignorato | `git status` | la cartella non compare |
| Lint pulito | `ruff check .` | `All checks passed!` |

## Miglioramenti futuri

- **Log strutturato in JSON** per il file, mantenendo il formato leggibile a
  terminale. Utile solo se il progetto arrivasse a un'analisi automatica dei
  log: oggi sarebbe over-engineering.
- **`request_id` per sessione Streamlit**, così da seguire una singola sessione
  utente dentro un log condiviso. Da valutare in M6.
- **Traduzione dei messaggi**: oggi sono in italiano nel codice. Se servisse
  l'inglese, si passerebbe a codici di errore più un dizionario.
- **Test automatici** dei due moduli: arrivano in M1-T5, dove le verifiche
  della tabella qui sopra diventano casi di `pytest`.

## Commit

```
M1 - T4 : add exception hierarchy and centralized logging
```

## Screenshot

_(segnaposto: terminale con le righe di log formattate e il file `logs/beewatch.log` aperto in VS Code)_
