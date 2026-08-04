# BeeWatch AI

Applicazione per apicoltori amatoriali: registra apiari, alveari, ispezioni e
raccolti, stima la resa attesa con un modello di regressione, e affianca un
assistente conversazionale che riassume le note di campo.

Progetto finale ITS · Python 3.11+ · Streamlit · MySQL · scikit-learn · LLM
locale via Ollama o remoto via OpenRouter.

---

## Stato del progetto

| Milestone | Contenuto | Stato |
|---|---|---|
| **M1** | Fondamenta e setup | ✅ completata |
| **M2** | Dati e database | 🔵 in corso — T1-T4 completate |
| M3 | Accesso ai dati ed ETL | ⬜ |
| M4 | Machine Learning | ⬜ |
| M5 | Componente AI generativa | ⬜ |
| M6 | Interfaccia Streamlit | ⬜ |
| M7 | Qualità, Docker, etica | ⬜ |
| M8 | Documentazione, demo e consegna | ⬜ |

Il backlog completo — 55 task su 9 milestone — è nelle
[issue](../../issues) e nella board *Projects* del repository.

## Come si avvia

### Requisiti

- **Python 3.11 o superiore**
- **Docker Desktop** — MySQL gira in un contenitore, non va installato (M2-T5)
- **Ollama**, se si vuole l'assistente in locale invece che via OpenRouter (M5)

### Installazione

```bash
git clone https://github.com/AVENA50/beewatch-ai.git
cd beewatch-ai

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS e Linux

pip install -e ".[dev]"
```

### Configurazione

```bash
cp .env.example .env            # copy .env.example .env  su Windows
```

Poi si aprono i valori in `.env` e si compilano. Le variabili sono documentate
una per una dentro `.env.example`; le obbligatorie sono tre: `DB_NAME`,
`DB_USER`, `DB_PASSWORD`.

L'applicazione **valida la configurazione all'avvio** e si ferma con un
messaggio che elenca tutti i problemi insieme, invece di scoprirli uno alla
volta.

### Il dataset

Il dataset USDA non è nel repository: ha una licenza propria e non è nostro da
ridistribuire. Si scarica da
[Kaggle](https://www.kaggle.com/datasets/jessicali9530/honey-production) e il
file `honeyproduction.csv` va messo in `data/`.

## Struttura

```
beewatch-ai/
├── app/           interfaccia Streamlit — nessuna logica applicativa
├── beewatch/      il pacchetto: configurazione, database, ML, AI
├── data/          dataset locali (ignorata da git)
├── docs/          documentazione: markdown/, diagrams/, images/
├── models/        modelli addestrati (.joblib)
├── notebooks/     analisi esplorative
├── scripts/       utilità eseguibili
├── sql/           schema e seed del database
└── tests/         test automatici
```

La separazione fra `app/` e `beewatch/` è deliberata: l'interfaccia chiama il
pacchetto, il pacchetto non sa che Streamlit esiste. I test girano senza
avviare l'interfaccia.

## Sviluppo

```bash
pytest                      # i test
ruff check .                # lint e ordine degli import
ruff check . --fix          # correzione automatica di ciò che è correggibile
```

Ogni pull request esegue automaticamente lint e test su una macchina pulita:
se il controllo `Lint e test` è rosso, il merge è bloccato.

Le convenzioni di ramo, commit e flusso di lavoro sono in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Documentazione

L'indice completo è in [`docs/README.md`](docs/README.md). I documenti che
conviene leggere per primi:

| Documento | Perché |
|---|---|
| [`docs/markdown/M2-dati/dati.md`](docs/markdown/M2-dati/dati.md) | tutto sui dati: da dove vengono, cosa dicono, cosa non possono dire |
| [`docs/markdown/M2-dati/M2-T4_schema.md`](docs/markdown/M2-dati/M2-T4_schema.md) | lo schema del database, con le query che lo giustificano |
| [`docs/markdown/M6-interfaccia/ui_spec.md`](docs/markdown/M6-interfaccia/ui_spec.md) | come deve comportarsi l'interfaccia |

## Avvertenza

Le stime prodotte da questo sistema sono **indicative** e si basano su dati di
apicoltura commerciale statunitense del periodo 1998-2012. Non descrivono un
apiario amatoriale italiano e vanno lette come ordine di grandezza, mai come
previsione puntuale.

**Questo software non è uno strumento diagnostico**: non sostituisce un
veterinario né un tecnico apistico.

## Licenza

MIT — vedi [`LICENSE`](LICENSE).
