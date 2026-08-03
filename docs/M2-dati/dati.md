# I dati di BeeWatch AI

> **Task M2-T1** · analisi esplorativa → sezioni *Fonte*, *Struttura*, *Osservazioni*, *Anomalie*
> **Task M2-T2** · dizionario e pulizia → sezioni *Dizionario delle colonne*, *Regole di pulizia*, *Conversioni di unità*
> **Procedimento completo:** `notebooks/01_eda.ipynb` (eseguibile dall'inizio alla fine)
> **File analizzato:** `data/honeyproduction.csv` — 32 KB, ignorato da git
> **Stato:** manca la scelta motivata del target, che arriva con M2-T3.

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

## Dizionario delle colonne

Il **nome interno** è quello che useremo nel codice, nel database e
nell'interfaccia. Il nome originale resta solo nel modulo che legge il CSV.

| Colonna (fonte) | Nome interno | Significato | Tipo | Unità |
|---|---|---|---|---|
| `state` | `stato` | Codice dello stato USA in cui è stata rilevata la produzione | testo, 2 caratteri | — |
| `year` | `anno` | Anno di riferimento della rilevazione | intero | anno solare |
| `numcol` | `numero_colonie` | Numero di colonie produttive nello stato | intero | colonie |
| `yieldpercol` | `resa_per_colonia_kg` | Miele prodotto in media da una colonia | decimale | kg (da libbre) |
| `totalprod` | `produzione_totale_kg` | Produzione complessiva dello stato — **derivata** | decimale | kg (da libbre) |
| `stocks` | `scorte_kg` | Miele invenduto al 15 dicembre | decimale | kg (da libbre) |
| `priceperlb` | `prezzo_per_kg_usd` | Prezzo medio di vendita | decimale | USD/kg (da USD/lb) |
| `prodvalue` | `valore_produzione_usd` | Valore della produzione — **derivata** | decimale | USD |

### Range e qualità

| Colonna | Minimo osservato | Massimo osservato | Valori distinti | Mancanti | Range accettato dall'ETL |
|---|---|---|---|---|---|
| `state` | `AL` | `WY` | 44 | 0 % | uno dei 44 codici elencati sotto |
| `year` | 1998 | 2012 | 15 | 0 % | 1990 – anno corrente |
| `numcol` | 2 000 | 510 000 | 148 | 0 % | 1 – 1 000 000 |
| `yieldpercol` | 19 lb (8,6 kg) | 136 lb (61,7 kg) | 95 | 0 % | 1 – 200 lb |
| `totalprod` | 84 000 lb | 46 410 000 lb | 517 | 0 % | > 0 |
| `stocks` | 8 000 lb | 13 800 000 lb | 500 | 0 % | ≥ 0 |
| `priceperlb` | 0,49 USD | 4,15 USD | 210 | 0 % | 0,10 – 10,00 USD |
| `prodvalue` | 162 000 USD | 69 615 000 USD | 589 | 0 % | > 0 |

Il **range accettato** è volutamente più largo di quello osservato: serve a
validare i dati in ingresso senza rifiutare valori legittimi che il dataset
attuale non contiene. Un valore fuori da quell'intervallo è un errore di
formato, non un caso raro.

I 44 codici ammessi:

```
AL AR AZ CA CO FL GA HI IA ID IL IN KS KY LA MD ME MI MN MO MS MT
NC ND NE NJ NM NV NY OH OK OR PA SC SD TN TX UT VA VT WA WI WV WY
```

### Un dettaglio sulla precisione

`numcol`, `totalprod`, `stocks` e `prodvalue` sono **tutti multipli di 1000**
nella fonte: il NASS arrotonda al migliaio. `yieldpercol` è un intero in libbre,
`priceperlb` ha al massimo due decimali.

**Conseguenza.** Il dato di partenza ha una precisione grossolana. Una previsione
che uscisse con tre cifre decimali darebbe un'impressione di accuratezza che i
dati non giustificano: la UI dovrà arrotondare di conseguenza (M6).

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

## Regole di pulizia

Queste regole sono la specifica di `transform()` in **M3-T4**. Ogni riga scartata
dall'ETL dovrà essere contata insieme al motivo, e il motivo dovrà essere una di
queste regole.

### R1 · Nessuna riga viene scartata perché "outlier"

I valori estremi sono stati verificati uno per uno (osservazione 5, anomalie
A3 e A4): sono grandi produttori e differenze climatiche, non errori di misura.
Applicare una regola IQR automatica cancellerebbe oltre metà della produzione
nazionale.

*Motivazione: un valore estremo che si ripete per quindici anni consecutivi è una
caratteristica, non un errore.*

### R2 · I valori mancanti si scartano, ma qui non ce ne sono

La fonte non ne contiene. La regola serve comunque, perché l'ETL deve reggere un
file diverso da quello di oggi: se in una riga manca un valore obbligatorio, la
riga viene scartata e contata con motivo `campo_obbligatorio_mancante`.

*Motivazione: nessuna imputazione. Inventare un valore su un dataset di 626 righe
sposterebbe le statistiche in modo non tracciabile.*

### R3 · Le quantità si convertono in chilogrammi

Fattore esatto **1 lb = 0,45359237 kg**, applicato a `yieldpercol`, `totalprod` e
`stocks`. Il fattore vive in una sola costante del codice, mai scritto a mano due
volte.

*Motivazione: l'utente è italiano. Un'interfaccia che parla di libbre è
inutilizzabile, e la conversione fatta a valle in ogni schermata è il modo
migliore per sbagliarne una.*

### R4 · Il prezzo si converte in USD/kg, la valuta resta in dollari

`priceperlb` diventa `prezzo_per_kg_usd` dividendo per 0,45359237. **Non** si
converte in euro.

*Motivazione: passare da libbre a chili è una conversione di unità, esatta e
senza assunzioni. Passare da dollari a euro richiederebbe il tasso di cambio di
ciascuno dei quindici anni: un'assunzione arbitraria che sporcherebbe un dato
storico. Il prezzo, del resto, non entra nel modello.*

### R5 · Le colonne derivate si conservano ma si marcano

`totalprod` e `prodvalue` sono calcolate dalle altre (osservazione 2). Restano
nel database per fedeltà alla fonte, ma sono **escluse dai predittori** del
modello.

*Motivazione: rimuoverle renderebbe impossibile verificare i dati contro il file
originale. Usarle come variabili di ingresso sarebbe data leakage. La marcatura
risolve entrambi i problemi.*

### R6 · Nessun arrotondamento in fase di trasformazione

I valori convertiti si conservano con tutti i decimali che escono dalla
moltiplicazione. L'arrotondamento è una scelta di **presentazione** e appartiene
all'interfaccia.

*Motivazione: arrotondare due volte a stadi diversi produce differenze fra
schermate che si fatica poi a spiegare.*

### R7 · `state` normalizzato e validato contro una lista chiusa

Due lettere maiuscole, spazi rimossi. Un codice fuori dai 44 ammessi scarta la
riga con motivo `stato_non_valido`. Il nome esteso dello stato vive in una
tabella di riferimento, non in questa colonna.

*Motivazione: la lista è chiusa e non cambierà. Validare contro di essa
intercetta subito un file corrotto o della fonte sbagliata.*

### R8 · `year` intero, entro un intervallo plausibile

Fuori dall'intervallo 1990 – anno corrente, la riga viene scartata con motivo
`anno_non_plausibile`.

*Motivazione: un anno a 1900 o 3025 è un errore di parsing, non un dato storico.*

### R9 · La coppia (`stato`, `anno`) è la chiave naturale

Deve essere unica. Un duplicato scarta la riga con motivo `chiave_duplicata`, e
viene registrato a livello `WARNING`: significa che la fonte è cambiata.

*Motivazione: diventerà un vincolo `UNIQUE` nello schema (M2-T4). Meglio
scoprirlo nell'ETL che dal database.*

### R10 · Gli stati con copertura parziale restano

South Carolina, Maryland, Oklahoma e Nevada hanno meno di 15 anni (anomalia A1).
Le righe si conservano. Chi calcola serie storiche usa il **pannello bilanciato**
dei 40 stati completi.

*Motivazione: il dato è valido, è il confronto fra anni a non esserlo. Il
problema si risolve a valle, non buttando via righe buone.*

### R11 · `scorte_kg` maggiore di `produzione_totale_kg` si segnala, non si corregge

Un `WARNING` a log con stato e anno. La riga passa.

*Motivazione: è plausibile (anomalia A2) — le scorte includono l'invenduto degli
anni precedenti. Correggerla significherebbe inventare un dato.*

### R12 · Le quantità sono interi, non decimali

Nel CSV `numcol`, `totalprod`, `stocks` e `prodvalue` sono letti come `float64`
ma sono sempre valori interi. Si leggono come interi, tranne dove la conversione
in chilogrammi introduce dei decimali.

*Motivazione: tipi corretti fin dalla lettura significa errori intercettati
prima, e una colonna `INT` invece di `DOUBLE` nel database.*

---

## Conversioni di unità e verifica manuale

```
1 libbra (lb) = 0,45359237 kg      (definizione internazionale esatta)

resa_per_colonia_kg   = yieldpercol × 0,45359237
produzione_totale_kg  = totalprod   × 0,45359237
scorte_kg             = stocks      × 0,45359237
prezzo_per_kg_usd     = priceperlb  ÷ 0,45359237
```

Il prezzo si **divide**, non si moltiplica: se un chilo pesa più di una libbra,
un chilo costa più di una libbra. È l'errore più facile da fare, ed è il motivo
per cui la verifica sotto include un controllo di plausibilità.

### Verifica su tre righe, calcolata a mano

**Riga 1 — Alabama, 1998** (prima riga del file)

| Grandezza | Valore fonte | Calcolo | Risultato |
|---|---|---|---|
| Resa per colonia | 71 lb | 71 × 0,45359237 | **32,2051 kg** |
| Produzione totale | 1 136 000 lb | 1 136 000 × 0,45359237 | **515 280,93 kg** |
| Scorte | 159 000 lb | 159 000 × 0,45359237 | **72 121,19 kg** |
| Prezzo | 0,72 USD/lb | 0,72 ÷ 0,45359237 | **1,5873 USD/kg** |

Controllo di coerenza: 16 000 colonie × 71 lb = 1 136 000 lb ✓ (corrisponde a
`totalprod`)

**Riga 314 — Iowa, 2005** (circa a metà del file)

| Grandezza | Valore fonte | Calcolo | Risultato |
|---|---|---|---|
| Resa per colonia | 88 lb | 88 × 0,45359237 | **39,9161 kg** |
| Produzione totale | 2 464 000 lb | 2 464 000 × 0,45359237 | **1 117 651,60 kg** |
| Scorte | 1 232 000 lb | 1 232 000 × 0,45359237 | **558 825,80 kg** |
| Prezzo | 1,21 USD/lb | 1,21 ÷ 0,45359237 | **2,6676 USD/kg** |

Controllo di coerenza: 28 000 × 88 = 2 464 000 lb ✓

**Riga 626 — Wyoming, 2012** (ultima riga del file)

| Grandezza | Valore fonte | Calcolo | Risultato |
|---|---|---|---|
| Resa per colonia | 51 lb | 51 × 0,45359237 | **23,1332 kg** |
| Produzione totale | 2 550 000 lb | 2 550 000 × 0,45359237 | **1 156 660,54 kg** |
| Scorte | 459 000 lb | 459 000 × 0,45359237 | **208 198,90 kg** |
| Prezzo | 1,87 USD/lb | 1,87 ÷ 0,45359237 | **4,1226 USD/kg** |

Controllo di coerenza: 50 000 × 51 = 2 550 000 lb ✓

**Verifica di plausibilità.** Le tre rese convertite valgono 32, 40 e 23 kg per
colonia: valori credibili per un alveare in una stagione. Se la conversione fosse
stata invertita (dividendo invece di moltiplicare) si otterrebbero 157, 194 e
112 kg — impossibili. Il segno della conversione è quindi corretto.

Questi tre casi diventeranno altrettanti test in **M3-T4**: i numeri qui sopra
sono i valori attesi.

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

Deliberatamente fuori dallo scopo di M2-T1 e M2-T2:

- la **scelta formale del target** della regressione e i limiti di
  trasferibilità al caso italiano → **M2-T3**;
- quali variabili entrano nel modello e come vengono codificate → **M4-T2**;
- come le tre tabelle si legano fra loro → **M2-T4**.

## Registro delle decisioni

| Regola | Decisione | Motivo in una riga |
|---|---|---|
| R1 | Nessuno scarto per outlier | Sono grandi produttori, non errori |
| R2 | Scarto se manca un campo obbligatorio, nessuna imputazione | Inventare valori su 626 righe sposta le statistiche |
| R3 | Quantità convertite in kg (× 0,45359237) | L'utente è italiano |
| R4 | Prezzo in USD/kg, valuta non convertita | Il cambio storico sarebbe un'assunzione arbitraria |
| R5 | Colonne derivate conservate ma escluse dai predittori | Fedeltà alla fonte senza data leakage |
| R6 | Nessun arrotondamento nell'ETL | L'arrotondamento è presentazione |
| R7 | `stato` validato su lista chiusa di 44 codici | Intercetta subito un file sbagliato |
| R8 | `anno` fra 1990 e l'anno corrente | Fuori intervallo è errore di parsing |
| R9 | (`stato`, `anno`) chiave unica | Diventa un vincolo nello schema |
| R10 | Stati con copertura parziale conservati | Il dato è valido, è il confronto a non esserlo |
| R11 | Scorte > produzione: warning, non correzione | Plausibile, correggerla sarebbe inventare |
| R12 | Quantità lette come interi | Tipi corretti fin dalla lettura |
