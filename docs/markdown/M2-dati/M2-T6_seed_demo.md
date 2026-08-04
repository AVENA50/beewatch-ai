# M2 - T6 · `seed.sql` e apiario dimostrativo

> **Milestone** M2 · Dati e database
> **Stato** completata
> **Commit** `M2 - T6 : add seed data and demo apiary`
> **Dipende da** [M2-T5](M2-T5_schema_sql.md) · lo schema deve esistere

## Obiettivo

Riempire il database con due cose diverse: i **valori fissi** senza i quali non
si può inserire nemmeno un alveare, e un **apiario dimostrativo** su cui
sviluppare l'interfaccia.

Il secondo punto non è un vezzo. Un'interfaccia costruita su tabelle vuote
nasce sbagliata: le colonne sono larghe uguali perché non c'è testo dentro, i
grafici sembrano funzionare perché non hanno punti da disegnare, e nessuno si
accorge che una nota lunga manda a capo la riga finché non arriva una nota
lunga.

## Cosa contiene

### Valori fissi

| Tabella | Righe | Contenuto |
|---|---|---|
| `stati_alveare` | 5 | in salute, in osservazione, debole, sciamato, morto — ciascuno con il proprio colore |
| `livelli_rischio` | 4 | nessuno, basso, medio, alto |
| `tipi_miele` | 8 | acacia, millefiori, castagno, tiglio, melata, girasole, eucalipto, non specificato |
| `stati_usa` | 44 | i codici presenti nel dataset USDA, con il nome esteso |

### L'apiario dimostrativo

Un utente, un apiario e **quattro alveari che raccontano quattro situazioni
diverse**. Non è un dettaglio estetico: sono i quattro casi che l'interfaccia
deve saper mostrare.

| Alveare | Stato | Storia |
|---|---|---|
| **A1** | in salute | la famiglia di riferimento: pesi che crescono con le fioriture, due stagioni complete |
| **A2** | debole | regina del 2023, sviluppo lento, scorte che calano fino al candito di marzo |
| **A3** | in osservazione | nucleo giovane con **sospetta varroa** — è qui che sta la nota per l'assistente AI |
| **A4** | sciamato | sciamatura di maggio 2026, famiglia dimezzata e poi recuperata |

**14 ispezioni** distribuite su due stagioni, con pesi che salgono durante le
fioriture e calano dopo la smielatura. Una serie piatta non permetterebbe di
verificare i grafici dell'andamento in M6.

**4 raccolti**, registrati **in entrambi i modi** previsti dallo schema: tre
dell'apiario intero con `alveare_id` a `NULL`, uno di un singolo alveare tenuto
separato. Serve a verificare che l'interfaccia gestisca tutti e due i casi, che
è esattamente la decisione presa in M2-T4.

### La nota lunga

L'ispezione 12 su A3 contiene un testo di circa 1 300 caratteri scritto **come
lo scriverebbe davvero un apicoltore la sera**: senza punteggiatura ordinata,
con osservazioni mescolate a dubbi e promemoria.

Contiene, sepolti nel discorso, cinque elementi strutturati che l'assistente
dovrà saper estrarre: la regina è stata vista, la covata è su quattro telaini,
il conteggio della varroa è di circa trenta in tre giorni, ci sono api con ali
deformi, le scorte sono sufficienti. E una domanda aperta — *trattare adesso o
aspettare la fine dell'acacia?* — che è il tipo di richiesta a cui l'assistente
**non deve** rispondere con un consiglio operativo (M2-T3).

È il caso di prova di M5: se l'assistente funziona su questa nota, funziona.

## File prodotti

| File | Contenuto |
|---|---|
| `sql/seed.sql` | valori fissi, apiario dimostrativo, ispezioni, raccolti |

## Decisioni progettuali

**D1 · Il seed è idempotente.** Ogni riga ha una chiave esplicita e usa
`ON DUPLICATE KEY UPDATE`: rilanciarlo non duplica niente e non genera errori.
Permette anche di **correggere il seed e riapplicarlo** senza ricreare il
database, che durante lo sviluppo capita spesso.

La forma usata è `VALUES (...) AS nuovo ON DUPLICATE KEY UPDATE col = nuovo.col`,
disponibile da MySQL 8.0.19. La vecchia `VALUES(col)` è deprecata dalla 8.0.20:
usarla oggi significherebbe scrivere codice che si sa già che andrà riscritto.

**D2 · Non ci sono dati USDA nel seed.** Arrivano dall'ETL a partire dal CSV
(M3-T4). Inserirli qui significherebbe avere due strade per popolare la stessa
tabella, e prima o poi darebbero risultati diversi.

**D3 · Non ci sono modelli né previsioni.** Un modello nasce
dall'addestramento; inventare `mae_kg = 3.2` significherebbe mettere un numero
falso in un posto dove qualcuno andrebbe a leggerlo sul serio — e in una
presentazione quel numero finirebbe su una slide. Arrivano con M4.

**D4 · Non ci sono conversazioni con l'assistente.** Stessa ragione: una
risposta scritta a mano e salvata come se l'avesse prodotta un modello è una
bugia archiviata.

Ne consegue che le pagine Previsioni e Assistente andranno progettate **con lo
stato vuoto**. È un bene: lo stato vuoto è un requisito dell'interfaccia, non un
caso limite, ed è il motivo per cui in tante applicazioni la prima schermata che
si vede è una tabella con zero righe e nessuna spiegazione.

**D5 · L'utente dimostrativo ha una password vera, ma è dichiarata.**
L'hash è bcrypt a 12 giri di `beewatch-demo`, scritto nei commenti del file.
Non è un segreto ed è giusto che non lo sia: serve a chiunque cloni il progetto
per entrare e guardarsi intorno. **Va disattivato prima della consegna**, e la
cosa è annotata nel file stesso.

**D6 · Le coordinate dell'apiario sono approssimate.** Un apiario dimostrativo
non deve suggerire che sia normale registrare una posizione esatta: le
coordinate sono dati personali indiretti (M2-T4), e l'esempio che diamo conta.

## Definition of Done

Eseguita su Windows 11 con Docker Desktop, MySQL 8.4.11.

| Verifica | Comando | Esito |
|---|---|---|
| Il seed si applica da solo al primo avvio | `docker compose down -v && docker compose up -d` | ✅ `BeeWatch: dati iniziali caricati - 44 stati USA, 4 alveari, 14 ispezioni, 4 raccolti` |
| Rilanciarlo non duplica | rieseguire `seed.sql` a mano | ✅ stessi conteggi: 44, 4, 14, 4 |
| Tutti gli stati sono coperti | `SELECT COUNT(DISTINCT stato_alveare_id) FROM alveari;` | ✅ 4 stati diversi su 4 alveari |
| I raccolti coprono entrambi i modi | `SELECT COUNT(*) FROM raccolti WHERE alveare_id IS NULL;` | ✅ 3 su 4 |
| La nota lunga c'è | `SELECT MAX(CHAR_LENGTH(note)) FROM ispezioni;` | ✅ 1 032 caratteri |

La verifica sull'idempotenza è quella che dà il nome alla task: il seed è stato
rieseguito su un database già popolato e i conteggi non sono cambiati. Con dei
semplici `INSERT` avremmo avuto 8 alveari e 28 ispezioni.

## Miglioramenti futuri

- **Un secondo utente** con un apiario diverso, per verificare che l'isolamento
  fra utenti funzioni davvero. Utile quando in M6 arriverà l'autenticazione: è
  lì che si scopre se una query si è dimenticata il `WHERE utente_id`.
- **Più note lunghe** con casi diversi — nutrizione, sostituzione regina,
  invernamento — quando in M5 si vorrà misurare l'assistente su più di un
  esempio.
- **Un seed separato per i test automatici**, più piccolo e senza testo
  realistico: i test devono essere veloci e non dipendere dal contenuto della
  demo.
