# M1 - T2 · Struttura del progetto e packaging

> **Milestone** M1 · Fondamenta e setup
> **Stato** completata
> **Commit** `chore(m1-t2): scaffold project structure and packaging`

## Obiettivo

Creare l'impalcatura del progetto: cartelle, file di configurazione, packaging
Python. Serve a rispondere in anticipo alla domanda *«dove va questo file?»*,
che altrimenti riceve tre risposte diverse da tre persone diverse.

## Cosa è stato fatto

### La struttura

```
beewatch-ai/
├── app/                 interfaccia Streamlit (pagine e componenti)
├── beewatch/            il pacchetto applicativo: tutta la logica
│   ├── ai/              assistente LLM
│   ├── database/        accesso ai dati
│   └── ml/              modello di regressione
├── data/                dataset locali — ignorata da git
├── docs/                documentazione
├── models/             modelli addestrati (.joblib) — questi sì committati
├── notebooks/           analisi esplorative
├── scripts/             utilità eseguibili una tantum
├── sql/                 schema e seed del database
└── tests/               test automatici
```

**La separazione fra `app/` e `beewatch/` è la scelta strutturale più
importante.** L'interfaccia Streamlit non contiene logica: chiama funzioni del
pacchetto. Il pacchetto non sa che esiste Streamlit. Il vantaggio si vede in due
momenti: i test girano senza avviare l'interfaccia, e se un giorno l'interfaccia
cambiasse tecnologia, la logica resterebbe intatta.

### Packaging

`pyproject.toml` dichiara il progetto come pacchetto Python installabile:

```
pip install -e ".[dev]"
```

L'installazione in modalità *editable* fa sì che `import beewatch` funzioni da
qualsiasi cartella — dai test, dai notebook, dall'interfaccia — senza
manipolare `sys.path` a mano, che è la soluzione che tutti provano per prima e
che poi si rompe.

Le dipendenze sono divise in due gruppi:

| Gruppo | Contenuto | Chi lo installa |
|---|---|---|
| principale | streamlit, pandas, scikit-learn, mysql-connector, python-dotenv, plotly… | chi usa l'applicazione |
| `dev` | pytest, pytest-cov, ruff, jupyterlab, matplotlib, python-docx | chi la sviluppa |

Chi vuole solo far girare l'app non si tira dietro Jupyter.

### Strumenti di qualità

Configurati nello stesso `pyproject.toml`, così esiste un file solo da guardare:

- **ruff** — linter e ordinatore di import. Regole `E, W, F, I, UP, B`, righe da
  100 caratteri, target Python 3.11.
- **pytest** — `testpaths = ["tests"]`, marcatori `integration` e `slow`
  dichiarati in anticipo (`--strict-markers` rifiuta i marcatori non dichiarati,
  così un refuso non passa inosservato).
- **coverage** — misura solo `beewatch/`, escludendo gli `__init__.py`.

### `.gitignore`

Alla parte standard per Python è stata aggiunta una sezione di progetto:

```gitignore
data/*
!data/.gitkeep

logs/
*.log
reports/
*.egg-info/
.ruff_cache/
```

## Il dettaglio che ha richiesto una correzione

La prima versione ignorava il dataset con `data/`. **Non funziona**: git non
permette di reincludere un file se la sua cartella è esclusa, quindi
`!data/.gitkeep` non aveva alcun effetto e chi clonava non trovava la cartella.

La forma corretta ignora il **contenuto**, non la cartella:

```gitignore
data/*
!data/.gitkeep
```

È stato verificato con una prova pratica su un repository di test, non
deducendolo dalla documentazione.

## File e artefatti prodotti

| File | Contenuto |
|---|---|
| `pyproject.toml` | packaging, dipendenze, ruff, pytest, coverage |
| `requirements.txt` | dipendenze bloccate, per chi non usa il packaging |
| `.gitignore` | sezione BeeWatch in coda a quella standard |
| `.dockerignore` | cosa non entra nell'immagine (M7) |
| `README.md` | descrizione del progetto |
| l'albero delle cartelle | con un `.gitkeep` in quelle ancora vuote |

## Decisioni progettuali

**I modelli addestrati si committano, i dati no.** Il `.joblib` deve essere nel
repository perché il docente possa clonare e avviare l'applicazione senza
riaddestrare. Il dataset USDA no: si scarica da Kaggle, ha una licenza propria e
non è nostro da ridistribuire.

**Le cartelle vuote esistono lo stesso.** Git non traccia le cartelle, solo i
file: un `.gitkeep` le fa sopravvivere al clone. Chi arriva vede subito dove
andranno le cose.

**Una sola fonte di configurazione per gli strumenti.** ruff, pytest e coverage
sono tutti in `pyproject.toml` invece che in `setup.cfg`, `.ruff.toml` e
`pytest.ini`. Meno file da cercare quando qualcosa non va.

## Definition of Done

| Verifica | Comando | Esito |
|---|---|---|
| Il progetto si installa | `pip install -e ".[dev]"` | ✅ |
| `import beewatch` funziona ovunque | `python -c "import beewatch"` | ✅ |
| Il lint è pulito | `ruff check .` | ✅ `All checks passed!` |
| Il dataset è ignorato | `git check-ignore -v data/*.csv` | ✅ |
| `data/.gitkeep` è tracciato | `git status` | ✅ |

## Miglioramenti futuri

- **`pre-commit`** per lanciare ruff prima del commit invece che in CI. Da
  valutare se il ciclo di feedback risultasse troppo lento.
- **Blocco delle versioni** delle dipendenze: oggi sono `>=`, il che va bene in
  sviluppo. Prima della consegna conviene fissarle, così la demo non dipende da
  un aggiornamento uscito il giorno prima.
