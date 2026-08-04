# M2 - T5 · `schema.sql` e MySQL in Docker

> **Milestone** M2 · Dati e database
> **Stato** completata
> **Commit** `M2 - T5 : add database schema and MySQL container`
> **Progettazione** → [`M2-T4_schema.md`](M2-T4_schema.md)

## Obiettivo

Tradurre in SQL lo schema progettato in M2-T4 e mettere in piedi il database.
È la prima task di M2 che produce qualcosa di **eseguibile**: fino a ieri
avevamo un documento, da oggi c'è un database che si avvia con un comando.

## Cosa è stato fatto

### MySQL in un contenitore

`docker-compose.yml` definisce un solo servizio, MySQL 8.4, con le credenziali
lette dallo stesso `.env` che legge l'applicazione.

```bash
docker compose up -d          # avvia
docker compose logs -f mysql  # guarda cosa fa
docker compose down           # ferma, i dati restano
docker compose down -v        # ferma e cancella i dati
```

**MySQL non si installa sul computer.** Il contenitore lo rende identico per
tutti e tre, non lascia un servizio Windows acceso a ogni avvio, e si azzera in
trenta secondi quando serve ripartire da zero. È anche il requisito Docker che
il docente chiede in M7, ottenuto con quattro mesi di anticipo.

### Lo schema si crea da solo

`sql/` è montata dentro `/docker-entrypoint-initdb.d`: al **primo** avvio — cioè
quando il volume è vuoto — MySQL esegue da solo tutti gli `.sql` che trova, in
ordine alfabetico. Prima `schema.sql`, poi `seed.sql` (M2-T6).

Non serve nessun comando manuale, e soprattutto **la procedura è identica per
chiunque cloni il progetto**: `docker compose up -d` e il database è pronto.

Gli script non vengono rieseguiti agli avvii successivi. Per ripartire pulito:

```bash
docker compose down -v && docker compose up -d
```

### Il DDL

Quattordici tabelle, quindici chiavi esterne, quattordici vincoli `CHECK`, otto
indici unici, quattordici indici. Scritto a mano dal documento M2-T4, **non**
esportato da dbdiagram: l'export non genera i `CHECK`, la colonna generata,
`UNSIGNED` né la codifica dei caratteri — cioè quattro cose su cui si regge
metà della correttezza dello schema.

## File prodotti

| File | Contenuto |
|---|---|
| `docker-compose.yml` | servizio MySQL 8.4, volume persistente, healthcheck |
| `sql/schema.sql` | il DDL completo e commentato |
| `.env.example` | nuova variabile `DB_ROOT_PASSWORD` |
| `docs/diagrams/er_diagram.dbml` | aggiornato: `raccolti` per apiario |
| `docs/markdown/M2-dati/M2-T4_schema.md` | aggiornato: tabella, relazioni, indici, query Q1 e Q5 |

## Decisioni progettuali

**D1 · Il nome del database non è scritto in `schema.sql`.** Arriva da `DB_NAME`
nel `.env`, e il contenitore seleziona quel database prima di eseguire lo
script. Scriverlo anche nel DDL significherebbe averlo in due posti: se qualcuno
cambiasse `DB_NAME`, le tabelle nascerebbero in un database e l'applicazione ne
cercherebbe un altro. Per l'esecuzione manuale si passa `-D nome_database`.

**D2 · Lo script è idempotente.** Ogni oggetto usa `CREATE TABLE IF NOT EXISTS`:
rilanciarlo non produce errori e non tocca i dati. La Definition of Done lo
chiede esplicitamente, ed è ciò che rende sicuro rieseguirlo per sbaglio.

**D3 · `DB_ROOT_PASSWORD` non è nella configurazione dell'applicazione.**
La usa solo il contenitore per creare il database e l'utente. `beewatch/config.py`
non la legge e non la valida, perché **l'applicazione non si connette mai come
root**: se un giorno lo facesse, sarebbe un errore da bloccare, non una
funzionalità da configurare.

**D4 · Volume con nome, non una cartella del progetto.** I file di MySQL restano
gestiti da Docker: non finiscono per sbaglio in git e non danno i problemi di
permessi che nascono montando una cartella Windows dentro un contenitore Linux.

**D5 · C'è un `healthcheck`.** Senza, il contenitore risulta "avviato" prima che
MySQL accetti connessioni, e il primo tentativo dell'applicazione fallisce.
Servirà a `docker compose up --wait` e a qualunque servizio che in M7 dipenderà
da questo.

**D6 · La porta esposta arriva da `.env`.** Chi ha già un MySQL sulla 3306 cambia
`DB_PORT` e non tocca `docker-compose.yml`. La porta *interna* al contenitore
resta sempre 3306.

**D6-bis · La porta è pubblicata solo su `127.0.0.1`.** Scrivere
`"3306:3306"` invece di `"127.0.0.1:3306:3306"` fa sì che Docker esponga il
database su **tutte** le interfacce di rete: chiunque si trovi sulla stessa rete
— il wifi dell'università, per dire — potrebbe tentare di connettersi, e
troverebbe le credenziali di sviluppo. Con il prefisso, MySQL risponde solo a
chi sta su questo computer. È una riga che elimina un'intera categoria di
problemi, ed è il motivo per cui in sviluppo si può convivere con password
semplici.

**D7 · Ogni tabella e le colonne non ovvie hanno un `COMMENT`.** La
documentazione vive anche dentro il database: `SHOW FULL COLUMNS FROM ispezioni`
spiega a cosa serve `note` senza aprire un file. Costa una riga e sopravvive
alla documentazione, che invece si può dimenticare di aggiornare.

**D8 · La coerenza fra `apiario_id` e `alveare_id` nei raccolti è applicativa.**
Un `CHECK` non può leggere altre tabelle, quindi il database non può impedire di
indicare un alveare che appartiene a un altro apiario. La verifica vive in M3,
insieme alle altre regole di dominio. Un trigger farebbe lo stesso lavoro, ma
sarebbe codice che vive nel database, non compare in nessuna revisione di pull
request e che nessuno ricorda di avere finché non lo maledice.

## Definition of Done

Eseguita su Windows 11 con Docker Desktop, MySQL 8.4.11.

| Verifica | Comando | Esito |
|---|---|---|
| Il database si avvia | `docker compose up -d` | ✅ contenitore `beewatch-mysql` in esecuzione |
| Lo schema si crea da solo | `docker compose logs mysql` | ✅ `BeeWatch: schema creato in \`beewatch\`, 14 tabelle` |
| Le tabelle ci sono | `SHOW TABLES;` | ✅ 14 righe |
| I vincoli funzionano | `UPDATE utenti SET tema='fucsia'` | ✅ `ERROR 3819: Check constraint 'chk_utenti_tema' is violated` |
| I dati sopravvivono al riavvio | `docker compose restart` | ✅ la riga inserita è ancora lì |
| Il database si ricrea da zero | `docker compose down -v && docker compose up -d` | ✅ schema ricreato, zero righe |
| Rilanciarlo non rompe nulla | rieseguire `schema.sql` a mano | ✅ `CREATE TABLE IF NOT EXISTS`: nessun errore |
| Testato da tutti e tre | — | ⬜ da fare con B e C |

La verifica sui vincoli è la più importante delle sette: fino alla 8.0.16 MySQL
accettava i `CHECK` e li ignorava in silenzio. Vederne uno fallire davvero è la
sola prova che lo schema difende sé stesso invece di sperare che sia
l'applicazione a farlo.

## Verifiche fatte prima di eseguire

Il DDL è stato controllato staticamente prima di provarlo, su tre punti che in
MySQL producono errori difficili da leggere:

| Controllo | Esito |
|---|---|
| Sintassi MySQL (parser `sqlglot`) | 15 istruzioni, nessun errore |
| Tipi delle chiavi esterne identici alle colonne riferite | 15 su 15 allineate |
| Nomi di vincolo duplicati (in MySQL sono unici per database) | nessuno |
| Ordine di creazione rispetta le dipendenze | nessuna tabella fuori ordine |

Il secondo è il più insidioso: una chiave esterna `INT` che punta a un
`INT UNSIGNED` fallisce con l'errore `errno 150`, che non dice quale colonna sia
il problema.

## Miglioramenti futuri

- **Migrazioni.** Oggi lo schema si ricrea da zero. Quando esisteranno dati veri
  da conservare, servirà uno strumento di migrazione — o almeno una tabella
  `versione_schema` e degli script numerati. Introdurlo adesso sarebbe
  over-engineering: non c'è ancora niente da migrare.
- **Backup.** `docker compose exec mysql mysqldump` in uno script, da valutare
  in M7 insieme al resto della messa in produzione.
- **Utente di sola lettura** per il notebook e le analisi, così l'esplorazione
  non può modificare nulla per errore.
