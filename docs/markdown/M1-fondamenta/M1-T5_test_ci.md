# M1 - T5 · Test automatici e integrazione continua

## Obiettivo

Trasformare le verifiche manuali di M1-T3 e M1-T4 in una suite di test che gira
da sola, e farla eseguire da GitHub a ogni push e a ogni pull request.

È l'ultima task di M1: da qui in avanti ogni modifica al progetto viene
controllata automaticamente prima di entrare in `main`.

## Descrizione

Fino a ora la correttezza si verificava a mano, incollando comandi nel
terminale e leggendo l'output. Funziona una volta; non funziona fra tre
settimane, quando il progetto avrà quaranta moduli e nessuno si ricorderà
quali comandi lanciare.

La task introduce due strati.

**I test.** Quarantadue casi che coprono i due moduli scritti finora:
configurazione (valori predefiniti, validazione, mascheramento dei segreti,
precedenza dell'ambiente, cache) ed eccezioni e logging (gerarchia,
idempotenza, livelli, scrittura su file).

**La CI.** Un workflow che su una macchina Ubuntu pulita installa il progetto
da zero con `pip install -e ".[dev]"`, lancia `ruff` e lancia `pytest`. È la
sola prova che il progetto si installa davvero: sul computer di chi sviluppa
funziona sempre, perché lì tutto è già installato.

## File coinvolti

| File | Azione |
|---|---|
| `tests/conftest.py` | creato — fixture condivise |
| `tests/test_config.py` | creato — 20 casi |
| `tests/test_exceptions.py` | creato — 14 casi |
| `tests/test_logging_config.py` | creato — 8 casi |
| `.github/workflows/ci.yml` | creato |
| `beewatch/logging_config.py` | modificato — guardia di idempotenza resa esplicita |
| `docs/markdown/M1-fondamenta/M1-T5_test_ci.md` | creato |

Nessuna nuova dipendenza: `pytest`, `pytest-cov` e `ruff` erano già in
`pyproject.toml` sotto `[project.optional-dependencies] dev`.

## Funzionalità implementate

### Isolamento dell'ambiente

Il problema principale di questi test è che `config.py` legge da `os.environ` e
dal file `.env`. Senza isolamento, gli stessi test passerebbero sul computer di
chi ha un `.env` completo e fallirebbero sulla CI, che non ce l'ha.

La fixture `ambiente_pulito` toglie tutte le variabili BeeWatch dall'ambiente e
azzera la cache di `ottieni()`. La fixture `scrivi_env` costruisce un `.env`
temporaneo per il singolo test. Ogni caso parte quindi da uno stato noto.

### Cosa viene verificato

| Area | Casi |
|---|---|
| Configurazione valida | valori letti correttamente, valori predefiniti applicati |
| Validazione | variabili obbligatorie mancanti elencate tutte insieme, porta non numerica, porta e timeout fuori intervallo, provider e livello di log non ammessi |
| Regole del provider | OpenRouter senza chiave fallisce all'avvio, Ollama non richiede chiave |
| Segreti | password e chiave API non compaiono mai nel riepilogo |
| Immutabilità | la configurazione non si può modificare dopo il caricamento |
| Precedenza | le variabili d'ambiente vincono sul file, come in Docker e in CI |
| Eccezioni | ogni sottoclasse è catturata da `except BeeWatchError`, i bug no |
| Logging | idempotenza su dieci riesecuzioni, livelli, scrittura su file, librerie silenziate |

### Il workflow

Tre passaggi in ordine di velocità, così un errore banale si scopre in venti
secondi invece che in tre minuti: `ruff` prima, `pytest` poi, con la copertura
stampata a fine esecuzione.

I test marcati `integration` sono esclusi (`-m "not integration"`): richiedono
MySQL o la rete, che qui non ci sono. Verranno abilitati in M2 aggiungendo un
servizio MySQL al workflow.

## Decisioni progettuali

**1. La guardia di idempotenza è stata riscritta.**
`configura()` controllava «esistono già handler su questo logger?». Il test
`test_configura_e_idempotente` ha mostrato che è sbagliato: pytest installa i
propri handler sullo stesso logger, quindi la guardia scattava e la
configurazione non veniva mai applicata. In produzione sarebbe successo lo
stesso con Streamlit. Ora i nostri handler portano un marcatore e la guardia
risponde alla domanda giusta: «ho già configurato *io*?».

È il primo bug trovato da un test in questo progetto, ed è esattamente il tipo
di bug che a mano non si vede: il codice sembrava funzionare.

**2. Perché i test non usano il `.env` reale.**
Un test che dipende dal file `.env` dello sviluppatore non è un test: è una
fotografia di una macchina. La fixture `ambiente_pulito` rende ogni caso
riproducibile ovunque.

**3. Perché la copertura si misura ma non si impone una soglia.**
Una soglia (`--cov-fail-under=80`) su un progetto ancora piccolo produce solo
test scritti per alzare il numero. La copertura si guarda come indicatore; la
soglia si valuterà quando il progetto sarà completo.

**4. Perché un solo Python e non una matrice di versioni.**
`requires-python = ">=3.11"` e la consegna gira su una versione sola. Una
matrice 3.11/3.12/3.13 raddoppierebbe i tempi senza dire nulla di utile.

**5. Perché `concurrency` con `cancel-in-progress`.**
Pushando due volte di fila sullo stesso branch, la prima esecuzione viene
annullata: non serve il risultato di un commit già superato.

## Definition of Done

| Verifica | Comando | Esito atteso |
|---|---|---|
| I test passano | `pytest` | `42 passed` |
| Il lint è pulito | `ruff check .` | `All checks passed!` |
| I test sono isolati | `pytest` senza `.env` nella cartella | stesso risultato |
| La CI è verde | aprire la PR su GitHub | check `Lint e test` verde |
| La copertura è misurata | `pytest --cov=beewatch` | tabella di copertura stampata |

## Miglioramenti futuri

- **MySQL nel workflow** come `services:`, per abilitare i test `integration`
  in M2.
- **Il check della CI reso obbligatorio** nel ruleset di `main`: la PR non si
  può mergiare se i test falliscono. Da attivare dopo la prima esecuzione
  verde, quando GitHub conosce il nome del check.
- **Soglia di copertura** a progetto completo.
- **`pre-commit`** per lanciare ruff prima del commit invece che in CI, se il
  ciclo di feedback risultasse troppo lento.

## Commit

```
M1 - T5 : add test suite and continuous integration workflow
```

## Screenshot

_(segnaposto: esecuzione di `pytest` con i 42 test verdi, e la pagina della
pull request con il check `Lint e test` completato)_
