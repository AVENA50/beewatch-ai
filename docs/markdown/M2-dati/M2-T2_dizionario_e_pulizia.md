# M2 - T2 · Data dictionary e regole di pulizia

> **Milestone** M2 · Dati e database
> **Stato** completata
> **Commit** `M2 - T2 : add column data dictionary and documented cleaning rules`
> **Risultati completi** → [`dati.md`](dati.md), sezioni *Dizionario delle colonne*, *Regole di pulizia*, *Conversioni di unità*

## Obiettivo

In M2-T1 abbiamo **osservato**; qui si **decide**. Ogni riga di questa task
diventerà una riga di codice in M3-T4 (l'ETL) e un vincolo nello schema (M2-T4).
Una decisione non scritta viene improvvisata al momento dell'implementazione, e
sarà diversa da quella che aveva in mente l'altro membro del gruppo.

## Cosa è stato fatto

**Dizionario delle otto colonne**: significato, tipo, unità di misura, range
osservato, **range accettato dall'ETL** e nome interno che useremo nel codice
(`yieldpercol` → `resa_per_colonia_kg`).

Il range accettato è volutamente più largo di quello osservato: serve a
validare i dati in ingresso senza rifiutare valori legittimi che il file
attuale non contiene. Un valore fuori da quell'intervallo è un errore di
formato, non un caso raro.

**Dodici regole di pulizia**, ciascuna con la propria motivazione, che
costituiscono la specifica di `transform()` in M3-T4.

**Conversioni di unità verificate a mano** su tre righe — la prima, una centrale
e l'ultima del file — con controllo di coerenza e verifica di plausibilità.

## Le decisioni che contano

| Regola | Decisione | Motivo |
|---|---|---|
| R1 | Nessuno scarto per outlier | Sono grandi produttori, non errori |
| R3 | Quantità convertite in kg (× 0,45359237) | L'utente è italiano |
| R4 | Prezzo in USD/kg, **valuta non convertita** | Il cambio storico di quindici anni sarebbe un'assunzione arbitraria |
| R5 | Colonne derivate conservate ma escluse dai predittori | Fedeltà alla fonte senza data leakage |
| R6 | Nessun arrotondamento nell'ETL | L'arrotondamento è presentazione, non trasformazione |
| R10 | Stati con copertura parziale conservati | Il dato è valido, è il confronto fra anni a non esserlo |

Le altre sei riguardano valori mancanti, validazione di stato e anno, chiave
naturale, scorte anomale e tipi.

**Un risultato inatteso**: nessuna anomalia richiede la rimozione di righe. Il
lavoro di pulizia in M3-T4 sarà di **conversione e normalizzazione**, non di
scarto.

## La verifica che smaschera l'errore più comune

Il prezzo si **divide** per 0,45359237, non si moltiplica: se un chilo pesa più
di una libbra, un chilo costa più di una libbra.

Le tre rese convertite valgono 32, 40 e 23 kg per colonia — valori credibili per
un alveare in una stagione. Con la conversione invertita si otterrebbero 157,
194 e 112 kg, impossibili. **La plausibilità del risultato è la verifica**, non
la formula sulla carta.

I tre casi diventeranno altrettanti test in M3-T4: i numeri sono già scritti.

## Il dettaglio sulla precisione

`numcol`, `totalprod`, `stocks` e `prodvalue` sono **tutti multipli di 1000**
nella fonte: il NASS arrotonda al migliaio.

Il dato di partenza ha quindi una precisione grossolana, e una previsione con
tre cifre decimali darebbe un'impressione di accuratezza che i dati non
giustificano. È il primo dei vincoli che porteranno alla regola di M2-T3: mai un
numero secco.

## File prodotti

| File | Contenuto |
|---|---|
| `docs/markdown/M2-dati/dati.md` | tre sezioni nuove: dizionario, dodici regole, conversioni verificate |

## Definition of Done

| Verifica | Esito |
|---|---|
| Tabella completa di tutte le colonne | ✅ significato, tipo, unità, range, nome interno |
| Ogni decisione di pulizia ha una motivazione | ✅ dodici regole, dodici motivazioni |
| Conversioni verificate a mano su 3 righe | ✅ prima, centrale, ultima, con controllo di coerenza |

## Miglioramenti futuri

- Le dodici regole diventeranno **test parametrici** in M3-T4: una regola, un
  caso di prova.
- Il dizionario potrà generare la validazione automaticamente, invece di essere
  ricopiato a mano nel codice. Da valutare solo se le colonne cresceranno.
