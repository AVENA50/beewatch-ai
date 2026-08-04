# M1 - T3 · Configurazione centralizzata e gestione dei segreti

**Milestone** M1 — Fondamenta e setup · **Priorità** P0 · **Owner** A
**Dipendenze** M1-T2 · **Periodo** 4 → 5 agosto 2026

---

## Obiettivo

Avere un unico punto di verità per la configurazione dell'applicazione, e
nessun segreto nel repository.

Il requisito nasce dalla slide 4 del PDF del docente («gestione degli errori»)
e da una regola pratica: un errore di configurazione scoperto a metà di una
demo è indistinguibile da un bug. Scoperto all'avvio, è una riga di messaggio.

---

## Descrizione

`beewatch/config.py` legge le variabili d'ambiente da `.env`, le valida e
restituisce un oggetto `Config` congelato. Se qualcosa manca o non è valido,
solleva `ConfigError` **una sola volta**, con l'elenco completo dei problemi.

Il file `.env.example` documenta tutte le variabili con valori fittizi ed è
committato. Il file `.env`, che contiene le credenziali vere, non lo è.

### Flusso

```
.env  ──►  load_dotenv()  ──►  validazione  ──►  Config (congelato)
                                    │
                                    └──► ConfigError con l'elenco dei problemi
```

---

## File coinvolti

| File | Stato | Committato |
|---|---|---|
| `beewatch/config.py` | creato | sì |
| `.env.example` | creato | sì |
| `.env` | creato in locale | **no**, già in `.gitignore` |

---

## Funzionalità implementate

- Caricamento da `.env` con precedenza alle variabili d'ambiente già presenti
  (`override=False`), così Docker e la CI possono sovrascrivere senza toccare
  il file.
- Validazione di dieci variabili: obbligatorietà, tipo, intervallo, valori
  ammessi.
- Raccolta di **tutti** gli errori prima di sollevare l'eccezione.
- `ConfigDatabase.descrizione()` e `ConfigLLM.descrizione()`: stringhe sicure
  per i log, in cui la password non compare mai.
- `Config.riepilogo()`: riga unica da stampare all'avvio.
- `ottieni()` con `lru_cache`: la configurazione si legge una volta sola e si
  può richiamare da qualsiasi modulo senza costi.

---

## Decisioni progettuali

**Dataclass congelati (`frozen=True`).** Una volta caricata, la configurazione
non si modifica. Se serve cambiarla si cambia `.env` e si riavvia. Così non
esistono mai due verità contemporaneamente — che è anche il motivo per cui la
linguetta *Database* della pagina Impostazioni (M6-T13) sarà di sola lettura.

**Tutti gli errori insieme, non il primo.** Chi installa il progetto li corregge
in un passaggio invece di scoprirli uno alla volta a ogni riavvio.

**`LLM_API_KEY` obbligatoria solo con OpenRouter.** Ollama gira in locale e non
richiede chiave; pretenderla sempre avrebbe costretto a inventare un valore
finto. Con OpenRouter invece la chiave manca all'avvio, non alla prima
richiesta dell'assistente.

**Confronto senza distinzione di maiuscole.** `LOG_LEVEL=debug` viene
normalizzato in `DEBUG`, la forma che il modulo `logging` si aspetta. Il primo
test scritto ha trovato proprio questo difetto.

**`ConfigError` è temporanea qui.** La gerarchia delle eccezioni nasce in
M1-T4. Allora `ConfigError` diventerà figlia di `BeeWatchError` e si sposterà
in `beewatch/exceptions.py`. Il resto del modulo non cambierà. L'alternativa —
invertire l'ordine delle due task — avrebbe rotto le dipendenze del backlog.

---

## Definition of Done

- [x] l'app fallisce all'avvio con messaggio chiaro se manca una variabile
- [x] `.env.example` completo e committato
- [x] `.env` presente in `.gitignore` e non tracciato da git
- [x] `git log` non contiene nessuna chiave o password

Verifiche eseguite:

| Caso | Esito |
|---|---|
| configurazione valida | `Config` costruito, password assente dal riepilogo |
| tre variabili mancanti | elencate tutte e tre in un'unica eccezione |
| porta 99999, provider inesistente, log level inventato | tre errori, messaggi con il valore trovato |
| OpenRouter senza chiave | errore dedicato |
| `LOG_LEVEL=debug` | normalizzato in `DEBUG` |
| `ruff check` | pulito |

---

## Miglioramenti futuri

- **M1-T4**: spostare `ConfigError` in `exceptions.py` come figlia di
  `BeeWatchError`.
- **M1-T5**: portare le sei verifiche qui sopra in `tests/test_config.py`, così
  diventano automatiche e girano in CI.
- **M7-T2**: verificare che `override=False` si comporti come atteso dentro
  `docker compose`, dove le variabili arrivano dall'ambiente e non dal file.

---

## Commit

```
feat(m1-t3): add centralized configuration with startup validation
```

---

## Screenshot

*(segnaposto — messaggio d'errore all'avvio con variabili mancanti)*
