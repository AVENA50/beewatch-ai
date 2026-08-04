# Documentazione di BeeWatch AI

Un documento per ogni task completata, nella cartella della propria milestone.
I codici sono gli stessi del backlog su GitHub e dei messaggi di commit.

## Indice

### M1 · Fondamenta e setup

| Task | Documento | Cosa contiene |
|---|---|---|
| M1-T1 | [Repository e convenzioni](markdown/M1-fondamenta/M1-T1_repository_e_convenzioni.md) | protezione di `main`, convenzioni di ramo e commit, moduli issue e PR, backlog |
| M1-T2 | [Struttura e packaging](markdown/M1-fondamenta/M1-T2_struttura_e_packaging.md) | albero delle cartelle, `pyproject.toml`, ruff e pytest |
| M1-T3 | [Configurazione](markdown/M1-fondamenta/M1-T3_configurazione.md) | lettura di `.env`, validazione all'avvio, gestione dei segreti |
| M1-T4 | [Eccezioni e logging](markdown/M1-fondamenta/M1-T4_eccezioni_logging.md) | gerarchia degli errori, logging centralizzato |
| M1-T5 | [Test e CI](markdown/M1-fondamenta/M1-T5_test_ci.md) | 42 test, workflow GitHub Actions |

### M2 · Dati e database

| Task | Documento | Cosa contiene |
|---|---|---|
| M2-T1 | [Analisi esplorativa](markdown/M2-dati/M2-T1_analisi_esplorativa.md) | com'è fatto il dataset USDA e cosa ne consegue |
| M2-T2 | [Dizionario e pulizia](markdown/M2-dati/M2-T2_dizionario_e_pulizia.md) | le dodici regole di trasformazione |
| M2-T3 | [Target e limiti](markdown/M2-dati/M2-T3_target_e_limiti.md) | cosa prevede il modello, e la soglia che deve battere |
| M2-T4 | [Schema relazionale](markdown/M2-dati/M2-T4_schema.md) | quattordici tabelle, undici query, diagramma ER |

### M6 · Interfaccia Streamlit

| Documento | Cosa contiene |
|---|---|
| [Specifica dell'interfaccia](markdown/M6-interfaccia/ui_spec.md) | palette, layout, componenti, comportamento delle schermate |

### Documenti di riferimento

Non appartengono a una singola task: crescono con il progetto.

| Documento | Cosa contiene |
|---|---|
| [`markdown/M2-dati/dati.md`](markdown/M2-dati/dati.md) | tutto ciò che sappiamo sui dati: fonte, dizionario, regole, target, limiti |
| [`markdown/M6-interfaccia/ui_spec.md`](markdown/M6-interfaccia/ui_spec.md) | la specifica dell'interfaccia |

## Come è organizzata la cartella

Tre cartelle, tre ruoli distinti: **i testi**, **gli allegati**, **i prodotti**.

```
docs/
├── README.md                  questo indice
│
├── markdown/                  I TESTI — l'unica fonte di verità
│   ├── M1-fondamenta/         un file per task
│   ├── M2-dati/
│   ├── M3-etl/                (vuote finché la milestone non inizia)
│   ├── M4-machine-learning/
│   ├── M5-ai-generativa/
│   ├── M6-interfaccia/
│   ├── M7-qualita-etica/
│   ├── M8-consegna/
│   └── MX-estensioni/
│
├── risorse/                   GLI ALLEGATI — immagini, diagrammi, schemi
│   ├── er_beewatch.png
│   └── schema.dbml
│
└── _word/                     I PRODOTTI — generati, ignorati da git
    ├── M1-fondamenta/         stessa struttura di markdown/
    └── ...
```

`markdown/` e `_word/` hanno **la stessa struttura di cartelle**: a ogni
`markdown/M2-dati/dati.md` corrisponde un `_word/M2-dati/dati.docx`. Il nome del
file non cambia mai, solo l'estensione.

`README.md` resta fuori da `markdown/` perché GitHub lo mostra automaticamente
quando si apre la cartella `docs/`: spostarlo significherebbe perdere l'indice
in bella vista.

**`risorse/`** tiene separati i documenti dagli allegati. Oggi contiene il
diagramma ER (`er_beewatch.png`) e la sua sorgente (`schema.dbml`); ci
finiranno gli screenshot dell'interfaccia e i grafici del modello.

## I due formati

La documentazione si scrive in **Markdown**, ed è l'unica fonte di verità: si
legge direttamente su GitHub, git ne mostra le differenze riga per riga e due
persone possono modificarla senza conflitti insanabili.

I **Word** servono per la consegna e per la stampa. Sono un **prodotto
generato**, non stanno in git e non si modificano a mano:

```
python scripts/genera_docx.py                               # tutti i documenti
python scripts/genera_docx.py docs/markdown/M2-dati/dati.md # uno solo
python scripts/genera_docx.py --verifica                    # sono allineati?
```

**Perché non stanno in git.** Un `.docx` è un file binario: in una pull request
comparirebbe come *«binary file not shown»*, nessuno potrebbe vedere cosa è
cambiato, e due persone che ne modificano uno insieme non avrebbero modo di
unire le versioni. Siccome sono comunque rigenerabili dal `.md` in due secondi,
tenerli sotto controllo di versione aggiunge peso e zero informazione.

## Convenzioni di scrittura

- **Nome del file**: `<codice-task>_<argomento>.md` per i documenti legati a una
  singola task, nome parlante per quelli di riferimento che crescono nel tempo.
- **Prima riga**: un titolo di livello 1 (`# ...`). Diventa il titolo del Word.
- **Subito dopo**: una citazione (`> ...`) con milestone, stato, commit e
  rimandi. Diventa il riquadro in cima al documento.
- **Sezioni**: livello 2 (`## ...`).
- Ogni decisione progettuale va scritta **con la sua motivazione**. Una
  decisione senza motivo, fra tre settimane, è indistinguibile da un caso.
- Ogni documento di task chiude con la **Definition of Done verificata** e i
  **miglioramenti futuri**: sapere cosa si è deciso di non fare vale quanto
  sapere cosa si è fatto.
