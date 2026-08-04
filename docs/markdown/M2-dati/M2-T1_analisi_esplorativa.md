# M2 - T1 · Dataset USDA e analisi esplorativa

> **Milestone** M2 · Dati e database
> **Stato** completata
> **Commit** `M2 - T1 : add USDA dataset exploratory analysis and data documentation`
> **Risultati completi** → [`dati.md`](dati.md), sezioni *Fonte*, *Struttura*, *Osservazioni*, *Anomalie*
> **Procedimento** → [`../../notebooks/01_eda.ipynb`](../../../notebooks/01_eda.ipynb)

## Obiettivo

Capire con che dati abbiamo a che fare **prima** di progettare il database
(M2-T4) e il modello (M4). Quattro domande: il dataset è completo e coerente?
Quali colonne portano informazione indipendente? Che andamenti mostra? Quanto è
trasferibile a un apiario amatoriale italiano?

## Cosa è stato fatto

Scaricato *Honey Production in the USA (1998-2012)* da Kaggle — 626 righe, 8
colonne, 44 stati — e analizzato in un notebook eseguibile dall'inizio alla
fine: struttura, valori mancanti, copertura temporale, coerenza interna,
distribuzioni, outlier, andamenti, geografia, correlazioni, anomalie puntuali.

Le conclusioni sono raccolte in `dati.md` come **nove osservazioni motivate** e
**sei anomalie classificate**, ciascuna con la propria conseguenza sul progetto.

## Le tre cose che hanno cambiato il progetto

**Tre colonne su otto sono calcolate dalle altre.** Verificato su tutte le 626
righe con scarto zero: `totalprod = numcol × yieldpercol`, e
`prodvalue ≈ totalprod × priceperlb`. Un modello che prevedesse `totalprod`
ricevendo i suoi due fattori otterrebbe R² pari a 1 senza aver imparato nulla.
È **data leakage**, ed è la prima cosa che un esaminatore nota. Da qui la scelta
del target in M2-T3.

**Gli outlier non sono errori.** La regola IQR segnala il 12 % delle righe su
`totalprod`, ma provengono da North Dakota, California, South Dakota e Florida
in **tutti e quindici gli anni**: sono i grandi produttori. Rimuoverli
cancellerebbe oltre metà della produzione nazionale.

**Il dataset è completo ma sbilanciato.** Zero valori mancanti — sembra
perfetto. Però solo 40 stati su 44 hanno tutti gli anni: la Carolina del Sud ne
ha tre. Sommare la produzione anno per anno produce una serie in cui parte del
calo è dovuta all'uscita di stati dal campione, non a un fenomeno reale.

## File prodotti

| File | Contenuto |
|---|---|
| `notebooks/01_eda.ipynb` | 40 celle, 5 grafici, eseguibile dall'inizio alla fine |
| `docs/markdown/M2-dati/dati.md` | 9 osservazioni motivate, 6 anomalie classificate |
| `data/honeyproduction.csv` | il dataset, **ignorato da git** |
| `pyproject.toml` | aggiunte le dipendenze `jupyterlab`, `ipykernel`, `matplotlib` |

## Decisioni progettuali

**Si parte dal file già ripulito**, non dai tre `honeyraw_*` presenti
nell'archivio. La nostra task non è ricostruire il dataset ma capirlo.

**Il CSV non entra nel repository.** Si scarica da Kaggle, ha una licenza propria
e non è nostro da ridistribuire. Il README dirà dove prenderlo.

**Il notebook si committa con gli output dentro**, così su GitHub si legge senza
doverlo eseguire — pur restando eseguibile da capo.

**`matplotlib` per l'analisi, `plotly` per l'interfaccia.** Due librerie con due
scopi: grafici statici per il notebook, grafici interattivi per Streamlit.

## Definition of Done

| Verifica | Esito |
|---|---|
| Il notebook gira dall'inizio alla fine senza errori | ✅ 20 celle con output, 5 grafici |
| `dati.md` contiene almeno 5 osservazioni motivate | ✅ nove |
| Anomalie e valori sospetti elencati | ✅ sei, classificate |
| Il CSV è in `data/` ed è ignorato da git | ✅ `.gitignore:229 data/*` |
| Lint pulito, anche sul notebook | ✅ ruff controlla anche i `.ipynb` |

## Miglioramenti futuri

- **Grafico su mappa degli Stati Uniti**: richiede `geopandas`, dipendenza pesante
  per un solo grafico.
- **Confronto con dati ISTAT** sull'apicoltura italiana, se reperibili: darebbe
  un numero all'osservazione 9 invece di una considerazione qualitativa.
