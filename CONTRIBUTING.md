# Contribuire a BeeWatch AI

Questo documento definisce le convenzioni di lavoro del gruppo. Valgono per
tutti i membri, dal primo commit alla consegna.

---

## 1. Branch strategy

Il branch `main` e' **protetto**: nessuno vi scrive direttamente, ogni modifica
entra tramite pull request.

| Prefisso | Quando si usa                          | Esempio                          |
|----------|----------------------------------------|----------------------------------|
| `feat/`  | nuova funzionalita'                    | `feat/m3-t3-repositories`        |
| `fix/`   | correzione di un bug                   | `fix/m6-t5-crash-previsione`     |
| `docs/`  | solo documentazione                    | `docs/m7-t4-documento-etico`     |
| `chore/` | manutenzione, dipendenze, CI           | `chore/aggiorna-workflow-ci`     |
| `test/`  | solo test                              | `test/m3-t6-copertura-etl`       |

**Regola:** il nome del branch contiene sempre il codice della task del backlog
(`m3-t3`, `m6-t5`, ...). Cosi' branch, issue, commit e pull request restano
collegati senza doverlo spiegare a nessuno.

Un branch = una task del backlog. Niente branch che accorpano piu' task.

---

## 2. Convenzione dei commit

Usiamo **Conventional Commits**, in inglese, con il **codice della task come
ambito**.

```
<tipo>(<codice-task>): <descrizione breve all'imperativo>
```

Tipi ammessi: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `ci`.

Esempi:

```
chore(m1-t2): scaffold project structure and packaging
feat(m4-t2): add ColumnTransformer for feature preprocessing
fix(m3-t4): handle missing state names in USDA dataset
docs(m7-t4): add GDPR and EU AI Act section
test(m3-t6): cover ETL transform with edge cases
```

Regole:

- descrizione in **inglese**, all'imperativo, minuscola, senza punto finale;
- massimo 72 caratteri sulla prima riga;
- se serve piu' contesto, riga vuota e poi il corpo del messaggio;
- se il commit chiude una issue, aggiungi in fondo `Closes #12`.

### Perche' il codice della task sta nell'ambito

Il backlog impone Conventional Commits; il piano di lavoro chiede che ogni
commit sia riferito alla task completata. Mettendo il codice della task
(`m4-t2`) al posto dell'ambito si soddisfano entrambi con una convenzione sola,
e la history diventa filtrabile:

```bash
git log --oneline --grep="m4-t"     # tutti i commit della milestone M4
```

**Commit frequenti e piccoli.** La commit history e' un criterio di valutazione
esplicito: un solo commit finale vale meno di trenta commit distribuiti.

---

## 3. Pull request

1. Crea il branch dalla `main` aggiornata.
2. Lavora e committa.
3. Apri la pull request compilando il template.
4. **Richiedi la review a un altro membro del gruppo.**
5. Alla approvazione, merge con **Squash and merge**.
6. Elimina il branch.

### Code review incrociata: obbligatoria

Ogni pull request va rivista da un membro che **non** l'ha scritta.

Non e' burocrazia: la valutazione dell'esame prevede domande individuali a
ciascun membro. La review incrociata e' l'unico meccanismo che garantisce che
tutti abbiano visto passare tutto il codice. Costa dieci minuti a PR.

Cosa guardare in review:

- la Definition of Done della task e' davvero soddisfatta?
- la UI resta separata dalla logica (nessun SQL, `joblib.load` o chiamata LLM
  dentro `app/`)?
- gli errori sono gestiti e tradotti in eccezioni di `beewatch`?
- c'e' almeno un test per il comportamento aggiunto?
- ho capito cosa fa questo codice abbastanza da spiegarlo all'esame?

---

## 4. Issue

Ogni task del backlog e' una issue. Si apre con il template `Task del backlog`,
che riporta il codice (`M3 - T3`), la milestone, la Definition of Done a
checkbox e le dipendenze.

Una issue si chiude **solo** quando tutte le caselle della Definition of Done
sono spuntate. Niente "quasi".

---

## 5. Ambiente di sviluppo

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate      # macOS / Linux

pip install -e ".[dev]"
```

Prima di aprire una pull request:

```bash
ruff check .
ruff format .
pytest -m "not integration"
```

---

## 6. Segreti

Nessuna credenziale entra nel repository, mai. Le variabili stanno in `.env`
(ignorato da git); `.env.example` documenta i nomi con valori fittizi.

Se per errore committi una chiave: **rigenerala subito**. Rimuoverla con un
commit successivo non serve a niente, resta nella history.
