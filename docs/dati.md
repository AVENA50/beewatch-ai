# I dati di BeeWatch AI

> **Task M2-T1** · Dataset USDA e analisi esplorativa
> **Procedimento completo:** `notebooks/01_eda.ipynb` (eseguibile dall'inizio alla fine)
> **File analizzato:** `data/honeyproduction.csv` — 32 KB, ignorato da git
> **Stato:** questo documento verrà esteso in M2-T2 con il dizionario colonna per
> colonna e le regole di pulizia, e in M2-T3 con la scelta motivata del target.

## Fonte

*Honey Production in the USA (1998-2012)*, pubblicato su Kaggle da Jessica Li,
ricavato dai rilevamenti del **National Agricultural Statistics Service (NASS)**
del Dipartimento dell'Agricoltura degli Stati Uniti.

Il file `honeyproduction.csv` è la versione già ripulita dall'autrice; nello
stesso archivio ci sono tre file `honeyraw_*` con i dati grezzi, che **non
usiamo**: partire dal file tidy è una scelta deliberata, perché la nostra task
non è ricostruire il dataset ma capirlo.

Ogni riga è la sintesi di **uno stato in un anno**. Non esistono righe per
singolo apiario o per singolo alveare: è un dato aggregato, e questo è il fatto
più importante di tutta l'analisi.

## Struttura in breve

| | |
|---|---|
| Righe | 626 |
| Colonne | 8 |
| Stati | 44 |
| Anni | 1998 – 2012 (15) |
| Valori mancanti | **0** |
| Duplicati su (`state`, `year`) | **0** |
| Unità di misura | libbre (produzione), dollari (prezzo e valore) |

Le colonne: `state`, `numcol` (numero di colonie), `yieldpercol` (resa per
colonia in libbre), `totalprod` (produzione totale in libbre), `stocks` (scorte
a fine anno in libbre), `priceperlb` (prezzo per libbra in dollari), `prodvalue`
(valore della produzione in dollari), `year`.

---

## Osservazioni

### 1. Il dataset è completo, ma il pannello è sbilanciato

Zero valori mancanti e zero duplicati: un caso raro, che si spiega col fatto che
il file è già stato ripulito a monte. Sarebbe però un errore concluderne che i
dati sono "completi".

Solo **40 stati su 44** hanno tutti e 15 gli anni. Gli altri quattro compaiono a
intermittenza:

| Stato | Anni presenti |
|---|---|
| South Carolina (SC) | 3 |
| Maryland (MD) | 6 |
| Oklahoma (OK) | 6 |
| Nevada (NV) | 11 |

Il numero di stati rilevati scende da 43 nel 1998 a **40 dal 2009 in poi**.

**Perché conta.** Sommare la produzione anno per anno su tutti gli stati
disponibili produce una serie storica in cui parte del calo è dovuta all'uscita
di stati dal campione, non a un fenomeno reale. Nel notebook gli andamenti
temporali sono calcolati **solo sui 40 stati completi** (pannello bilanciato).
Chiunque rifaccia questa analisi deve fare lo stesso.

### 2. Tre colonne su otto sono calcolate dalle altre

Verificato su tutte le 626 righe, con scarto massimo pari a **zero**:

```
totalprod = numcol × yieldpercol
```

E, a meno di un arrotondamento al migliaio di dollari (scarto massimo 500 $,
pari allo 0,22 %):

```
prodvalue = totalprod × priceperlb
```

**Perché conta.** È l'osservazione con più conseguenze pratiche di tutta
l'analisi. Un modello di regressione che prevede `totalprod` ricevendo `numcol`
e `yieldpercol` fra le variabili di ingresso otterrebbe un R² pari a 1 senza
aver imparato nulla: starebbe eseguendo una moltiplicazione. È il caso da
manuale di **data leakage**, e sarebbe la prima cosa che un esaminatore nota.

**Conseguenza per il progetto.** Il target della regressione deve essere
`yieldpercol`, la resa per colonia, e `totalprod` e `prodvalue` non possono
comparire fra i predittori. La decisione formale è di M2-T3; qui è la prova
numerica che la rende obbligata.

### 3. La produzione crolla, ma gli alveari non diminuiscono

Sul pannello bilanciato, fra il 1998 e il 2012:

| Grandezza | 1998 | 2012 | Variazione |
|---|---|---|---|
| Colonie totali | 2 600 000 | 2 509 000 | **−3,5 %** |
| Produzione totale (lb) | 218 547 000 | 140 907 000 | **−35,5 %** |
| Resa media per colonia (lb) | 71,7 | 55,2 | **−23,0 %** |
| Prezzo medio (USD/lb) | 0,80 | 2,37 | **+197,6 %** |

**Perché conta.** Il calo della produzione non è spiegato da un calo del numero
di alveari: è spiegato da alveari **meno produttivi**. Il periodo coincide con
gli anni in cui è stato descritto il *Colony Collapse Disorder*; il dataset da
solo non permette di stabilire un nesso causale, ma la forma del fenomeno è
quella.

**Conseguenza per il progetto.** `year` è una variabile informativa e non
decorativa: la resa attesa nel 2012 è sistematicamente diversa da quella del
1998. Va inclusa fra i predittori, ma con cautela — un modello addestrato su
questa tendenza ed estrapolato al 2026 sta indovinando.

### 4. Il prezzo è l'unica variabile con una tendenza temporale netta

La correlazione fra `priceperlb` e `year` è **0,694**, di gran lunga la più alta
fra quelle con l'anno. Tutte le altre correlazioni elevate della matrice
(`numcol`–`totalprod` = 0,954, `totalprod`–`prodvalue` = 0,907) sono l'identità
algebrica dell'osservazione 2, non una relazione empirica.

Il prezzo è **nominale**: non è corretto per l'inflazione. Confronti diretti fra
il 1998 e il 2012 vanno letti tenendone conto.

### 5. Gli outlier non sono errori: sono i grandi produttori

La regola IQR (fattore 1,5) segnala molte righe:

| Colonna | Righe fuori intervallo | % |
|---|---|---|
| `prodvalue` | 76 | 12,1 % |
| `totalprod` | 75 | 12,0 % |
| `numcol` | 63 | 10,1 % |
| `stocks` | 54 | 8,6 % |
| `priceperlb` | 22 | 3,5 % |
| `yieldpercol` | 12 | 1,9 % |

Guardando **chi** sono, il quadro cambia: gli outlier di `totalprod` provengono
da North Dakota, California, South Dakota e Florida in **tutti e 15 gli anni**,
più Montana (8) e Minnesota (7).

**Perché conta.** Un valore estremo che si ripete per quindici anni consecutivi
non è un errore di misura: è una caratteristica strutturale. Eliminare quelle
righe cancellerebbe oltre la metà della produzione nazionale.

**Conseguenza per il progetto.** Nessuna rimozione di outlier su `totalprod`,
`numcol`, `stocks` e `prodvalue`. La regola di pulizia definitiva si scrive in
M2-T2, ma la direzione è già decisa da questi numeri.

### 6. La produzione è fortemente concentrata

I primi **5 stati** valgono il **57,2 %** della produzione dei quindici anni; il
solo North Dakota vale il **18,2 %**. Gli ultimi dieci stati messi insieme
arrivano all'**1,4 %**.

**Conseguenza per il progetto.** Una media nazionale non descrive nessuno stato
reale. Se il modello userà `state` come variabile, dovrà trattarla come
categoria, non come indice numerico.

### 7. La resa per colonia è l'unica variabile "biologica"

`yieldpercol` è l'unica colonna con una distribuzione ragionevolmente simmetrica
(media 62,0 lb, mediana 60,0 lb) e con la percentuale più bassa di outlier
(1,9 %). Tutte le altre grandezze sono asimmetriche a destra perché dipendono
dalla **dimensione** dello stato, non dal comportamento delle api.

**Conseguenza per il progetto.** Conferma dal lato statistico quello che
l'osservazione 2 imponeva dal lato logico: `yieldpercol` è il candidato naturale
come target.

### 8. Gli estremi di resa hanno una spiegazione geografica

| | Stato, anno | Resa (lb) |
|---|---|---|
| Massimo | Hawaii, 2002 | 136 |
| | Hawaii, 2005 | 131 |
| | North Dakota, 1998 | 128 |
| Minimo | New Jersey, 2003 | 19 |
| | Maine, 2001 | 20 |
| | Maine, 2000 | 21 |

Per medie sui quindici anni: in testa Hawaii (98), Louisiana (96), North Dakota
(88); in coda Maine (31), New Jersey (37), Virginia (40).

**Perché conta.** Alle Hawaii la fioritura è continua tutto l'anno, nel Maine la
stagione utile dura poche settimane. La differenza fra il primo e l'ultimo è di
**oltre tre volte**. Non sono dati da correggere: sono la prova che il clima
domina la resa, e che un modello che ignora la posizione geografica non può
funzionare.

### 9. Il dato è commerciale e aggregato, l'utente è amatoriale e italiano

Convertendo in unità comprensibili (1 lb = 0,45359237 kg):

| | Libbre | Chilogrammi |
|---|---|---|
| Resa media per colonia | 62,0 | **28,1** |
| Resa mediana | 60,0 | 27,2 |
| Minimo osservato | 19 | 8,6 |
| Massimo osservato | 136 | 61,7 |

**Perché conta.** L'ordine di grandezza è confrontabile con quello di un alveare
amatoriale italiano in una buona stagione, ma la somiglianza è ingannevole: qui
si tratta di **medie statali di apicoltura professionale**, con pratiche di
gestione, nomadismo e selezione genetica che un amatore non ha.

**Conseguenza per il progetto.** La previsione mostrata all'utente non può
essere un numero secco. Deve essere una stima indicativa con banda di
incertezza e un avviso esplicito sulla provenienza dei dati. È il punto che
M2-T3 formalizza e che la pagina Trasparenza (M6-T8) dovrà comunicare.

---

## Anomalie e valori sospetti

| # | Anomalia | Righe | Valutazione |
|---|---|---|---|
| A1 | Stati con meno di 15 anni di rilevazione (SC, MD, OK, NV) | 26 | **Reale.** Il NASS non rileva ogni stato ogni anno. Da gestire escludendoli dalle serie storiche, non dal dataset. |
| A2 | `stocks` maggiore di `totalprod`: Nebraska 2006 (3 843 000 contro 3 431 000) | 1 | **Plausibile.** Le scorte di fine anno includono l'invenduto degli anni precedenti. Da segnalare, non da correggere. |
| A3 | 75 righe fuori dall'intervallo IQR su `totalprod` | 75 | **Non sono errori** (osservazione 5). Nessuna rimozione. |
| A4 | Resa di 19 lb (New Jersey 2003) contro 136 lb (Hawaii 2002) | 2 | **Reali.** Differenza climatica documentata (osservazione 8). |
| A5 | `prodvalue` non corrisponde esattamente a `totalprod × priceperlb` | 626 | **Arrotondamento** al migliaio di dollari. Scarto massimo 0,22 %. Nessun intervento. |
| A6 | `priceperlb` non corretto per l'inflazione | 626 | **Caratteristica della fonte.** Da dichiarare, non da modificare. |

Nessuna anomalia richiede la rimozione di righe. È un risultato inatteso e va
detto: il lavoro di pulizia in M3-T4 sarà di **conversione e normalizzazione**,
non di scarto.

---

## Cosa comporta per il resto del progetto

| Osservazione | Ricade su |
|---|---|
| `totalprod` e `prodvalue` sono derivate (2) | **M2-T3** scelta del target · **M4** costruzione della pipeline |
| Pannello sbilanciato (1) | **M3-T4** ETL: la logica di aggregazione temporale |
| Nessun valore da rimuovere (5, A1–A6) | **M2-T2** regole di pulizia |
| `state` è categoria, non numero (6) | **M4-T2** codifica delle variabili |
| Scarto fra dato commerciale USA e apiario amatoriale (9) | **M2-T3** limiti · **M6-T8** pagina Trasparenza · **M7-T4** documento etico |
| Il dato è aggregato per stato-anno (fonte) | **M2-T4** schema relazionale: le tabelle USDA sono di *riferimento*, separate da quelle operative |

---

## Cosa non è stato deciso qui

Deliberatamente fuori dallo scopo di M2-T1, per non anticipare decisioni senza
averle documentate:

- il **dizionario delle colonne** con tipi, unità e range attesi → **M2-T2**;
- le **regole di pulizia** e la conversione libbre → chilogrammi → **M2-T2**;
- la **scelta formale del target** e i limiti di trasferibilità → **M2-T3**.
