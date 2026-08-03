# Documentazione di BeeWatch AI

I documenti sono organizzati per **milestone**, con lo stesso codice usato nel
backlog su GitHub e nei messaggi di commit.

| Cartella | Milestone | Contenuto |
|---|---|---|
| `M1-fondamenta/` | M1 · Fondamenta e setup | configurazione, eccezioni e logging, test e CI |
| `M2-dati/` | M2 · Dati e database | analisi del dataset USDA, dizionario, regole di pulizia |
| `M3-etl/` | M3 · Accesso ai dati ed ETL | — |
| `M4-machine-learning/` | M4 · Machine Learning | — |
| `M5-ai-generativa/` | M5 · Componente AI generativa | — |
| `M6-interfaccia/` | M6 · Interfaccia Streamlit | specifica dell'interfaccia |
| `M7-qualita-etica/` | M7 · Qualità, Docker, etica | — |
| `M8-consegna/` | M8 · Documentazione, demo e consegna | — |
| `MX-estensioni/` | MX · Estensioni opzionali | — |

## Due formati, una sola fonte

Ogni documento esiste in due versioni con lo stesso nome:

- **`.md`** — la versione di lavoro. È **l'unica fonte di verità**: si legge
  direttamente su GitHub, git ne mostra le differenze riga per riga e due
  persone possono modificarla senza conflitti insanabili.
- **`.docx`** — la versione da consegnare e da stampare. È un **prodotto
  generato**, non si modifica a mano: qualunque modifica fatta in Word andrebbe
  persa alla rigenerazione successiva.

### Rigenerare i Word

Dopo aver modificato un `.md`:

```
python scripts/genera_docx.py                      # tutti i documenti
python scripts/genera_docx.py docs/M2-dati/dati.md # uno solo
python scripts/genera_docx.py --verifica           # controlla se sono allineati
```

`--verifica` esce con codice 1 se un `.docx` manca o è più vecchio del suo
`.md`: è pensato per essere aggiunto alla CI quando la documentazione sarà
stabile.

## Convenzioni di scrittura

- **Nome del file**: `<codice-task>_<argomento>.md` per i documenti legati a una
  singola task (`M1-T3_configurazione.md`), nome parlante per quelli trasversali
  che crescono nel tempo (`dati.md`, `ui_spec.md`).
- **Prima riga**: un titolo di livello 1 (`# ...`). Diventa il titolo del Word.
- **Seconda riga**: una citazione (`> ...`) con i riferimenti alla task, ai file
  coinvolti e allo stato. Diventa il riquadro in cima al documento.
- **Sezioni**: livello 2 (`## ...`) per le sezioni principali.
- Ogni decisione progettuale va scritta **con la sua motivazione**. Una
  decisione senza motivo, fra tre settimane, è indistinguibile da un caso.
