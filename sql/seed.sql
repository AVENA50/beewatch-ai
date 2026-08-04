-- =========================================================================== --
-- BeeWatch AI - dati iniziali
-- =========================================================================== --
--
-- Task M2-T6. Due cose diverse in un file solo:
--
--   1. VALORI FISSI      stati alveare, livelli di rischio, tipi di miele,
--                        i 44 stati USA del dataset. Servono sempre: senza,
--                        non si puo' inserire nemmeno un alveare.
--
--   2. APIARIO DIMOSTRATIVO  un utente con quattro alveari che raccontano
--                        situazioni diverse. Serve a sviluppare l'interfaccia
--                        (M6) su dati veri invece che su tabelle vuote, e a
--                        dare all'assistente AI (M5) del testo su cui lavorare.
--
-- Esecuzione
-- ----------
-- Automatica: il contenitore lo esegue dopo `schema.sql` al primo avvio,
-- perche' /docker-entrypoint-initdb.d li ordina alfabeticamente e
-- "schema" viene prima di "seed".
--
--     docker compose up -d
--
-- Manuale:
--
--     docker compose exec -T mysql mysql -u root -p -D beewatch < sql/seed.sql
--
-- Idempotenza
-- -----------
-- Ogni riga ha una chiave esplicita e usa ON DUPLICATE KEY UPDATE: rilanciare
-- questo file non duplica niente e non genera errori. E' la Definition of Done
-- della task, ed e' anche cio' che permette di correggere il seed e riapplicarlo
-- senza ricreare il database.
--
-- La forma usata e' `VALUES (...) AS nuovo ON DUPLICATE KEY UPDATE col =
-- nuovo.col`, disponibile da MySQL 8.0.19. La vecchia `VALUES(col)` e'
-- deprecata dalla 8.0.20 e verra' rimossa: usarla oggi significherebbe scrivere
-- codice che si sa gia' che andra' riscritto.
--
-- Cosa NON c'e', e perche'
-- ------------------------
--   produzione_usda   arriva dall'ETL a partire dal CSV (M3-T4)
--   modelli           nasce dall'addestramento (M4): inventare metriche
--                     significherebbe mettere numeri falsi in un posto dove
--                     qualcuno andrebbe a leggerli sul serio
--   previsioni        dipendono da un modello, quindi seguono M4
--   conversazioni     nascono parlando con l'assistente (M5)
--
-- Le pagine che mostrano queste cose andranno progettate con lo stato vuoto,
-- il che e' un bene: lo stato vuoto e' un requisito dell'interfaccia, non un
-- caso limite, e progettarlo per ultimo e' il motivo per cui in tante
-- applicazioni la prima schermata che vedi e' una tabella con zero righe e
-- nessuna spiegazione.
-- =========================================================================== --


-- --------------------------------------------------------------------------- --
-- 1. Valori fissi
-- --------------------------------------------------------------------------- --

INSERT INTO stati_alveare (id, codice, etichetta, colore, ordine) VALUES
    (1, 'in_salute',      'In salute',       '#3FB463', 1),
    (2, 'in_osservazione','In osservazione', '#E9A825', 2),
    (3, 'debole',         'Debole',          '#F0A310', 3),
    (4, 'sciamato',       'Sciamato',        '#5B96FF', 4),
    (5, 'morto',          'Morto',           '#EC5A5F', 5)
AS nuovo
ON DUPLICATE KEY UPDATE
    codice    = nuovo.codice,
    etichetta = nuovo.etichetta,
    colore    = nuovo.colore,
    ordine    = nuovo.ordine;


INSERT INTO livelli_rischio (id, codice, etichetta, gravita) VALUES
    (1, 'nessuno', 'Nessun rischio rilevato', 1),
    (2, 'basso',   'Rischio basso',           2),
    (3, 'medio',   'Rischio medio',           3),
    (4, 'alto',    'Rischio alto',            4)
AS nuovo
ON DUPLICATE KEY UPDATE
    codice    = nuovo.codice,
    etichetta = nuovo.etichetta,
    gravita   = nuovo.gravita;


INSERT INTO tipi_miele (id, codice, etichetta) VALUES
    (1, 'acacia',      'Acacia'),
    (2, 'millefiori',  'Millefiori'),
    (3, 'castagno',    'Castagno'),
    (4, 'tiglio',      'Tiglio'),
    (5, 'melata',      'Melata'),
    (6, 'girasole',    'Girasole'),
    (7, 'eucalipto',   'Eucalipto'),
    (8, 'non_definito','Non specificato')
AS nuovo
ON DUPLICATE KEY UPDATE
    codice    = nuovo.codice,
    etichetta = nuovo.etichetta;


-- I 44 stati presenti nel dataset USDA (M2-T2). Non sono tutti gli stati
-- americani: il NASS non rileva la produzione ovunque.
INSERT INTO stati_usa (codice, nome) VALUES
    ('AL', 'Alabama'),        ('AR', 'Arkansas'),       ('AZ', 'Arizona'),
    ('CA', 'California'),     ('CO', 'Colorado'),       ('FL', 'Florida'),
    ('GA', 'Georgia'),        ('HI', 'Hawaii'),         ('IA', 'Iowa'),
    ('ID', 'Idaho'),          ('IL', 'Illinois'),       ('IN', 'Indiana'),
    ('KS', 'Kansas'),         ('KY', 'Kentucky'),       ('LA', 'Louisiana'),
    ('MD', 'Maryland'),       ('ME', 'Maine'),          ('MI', 'Michigan'),
    ('MN', 'Minnesota'),      ('MO', 'Missouri'),       ('MS', 'Mississippi'),
    ('MT', 'Montana'),        ('NC', 'North Carolina'), ('ND', 'North Dakota'),
    ('NE', 'Nebraska'),       ('NJ', 'New Jersey'),     ('NM', 'New Mexico'),
    ('NV', 'Nevada'),         ('NY', 'New York'),       ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),       ('OR', 'Oregon'),         ('PA', 'Pennsylvania'),
    ('SC', 'South Carolina'), ('SD', 'South Dakota'),   ('TN', 'Tennessee'),
    ('TX', 'Texas'),          ('UT', 'Utah'),           ('VA', 'Virginia'),
    ('VT', 'Vermont'),        ('WA', 'Washington'),     ('WI', 'Wisconsin'),
    ('WV', 'West Virginia'),  ('WY', 'Wyoming')
AS nuovo
ON DUPLICATE KEY UPDATE nome = nuovo.nome;


-- --------------------------------------------------------------------------- --
-- 2. Apiario dimostrativo
-- --------------------------------------------------------------------------- --
-- Utente di prova. La password e' `beewatch-demo`, l'hash e' bcrypt a 12 giri.
-- E' un account dimostrativo: va disabilitato o cancellato prima di qualsiasi
-- uso reale, e non deve esistere nell'ambiente di consegna con questa password.

INSERT INTO utenti (id, email, nome_completo, hash_password, tema, attivo) VALUES
    (1, 'demo@beewatch.local', 'Apicoltore Dimostrativo',
     '$2b$12$3UhRtFKUUOgVutfM3VnYbOeOjj5lL5asOvtgOVv/79WDjLjx3NX1W', 'auto', TRUE)
AS nuovo
ON DUPLICATE KEY UPDATE
    nome_completo = nuovo.nome_completo,
    hash_password = nuovo.hash_password;


-- Coordinate volutamente approssimate: un apiario dimostrativo non deve
-- suggerire che sia normale registrare una posizione esatta.
INSERT INTO apiari (id, utente_id, nome, localita, latitudine, longitudine, note) VALUES
    (1, 1, 'Apiario del Noce', 'Colline sopra Bergamo', 45.7100, 9.6700,
     'Esposizione a sud-est, riparato dal vento. Fioriture principali: acacia a maggio, castagno a giugno, millefiori estivo.')
AS nuovo
ON DUPLICATE KEY UPDATE
    nome     = nuovo.nome,
    localita = nuovo.localita,
    note     = nuovo.note;


-- Quattro alveari, quattro situazioni diverse. Servono a verificare che
-- l'interfaccia regga tutti i casi, non solo quello felice.
INSERT INTO alveari
    (id, apiario_id, stato_alveare_id, codice, data_installazione, anno_regina, note, attivo)
VALUES
    (1, 1, 1, 'A1', '2024-04-12', 2024,
     'Famiglia forte, regina del 2024. E'' l''alveare di riferimento dell''apiario.', TRUE),

    (2, 1, 3, 'A2', '2024-04-12', 2023,
     'Regina vecchia, da sostituire. Sviluppo lento in primavera.', TRUE),

    (3, 1, 2, 'A3', '2025-03-30', 2025,
     'Nucleo formato a marzo. Da tenere d''occhio per la varroa.', TRUE),

    (4, 1, 4, 'A4', '2024-05-20', 2024,
     'Sciamato a maggio 2026, recuperato con regina nuova.', TRUE)
AS nuovo
ON DUPLICATE KEY UPDATE
    stato_alveare_id = nuovo.stato_alveare_id,
    codice           = nuovo.codice,
    note             = nuovo.note,
    attivo           = nuovo.attivo;


-- --------------------------------------------------------------------------- --
-- 3. Ispezioni su due stagioni
-- --------------------------------------------------------------------------- --
-- I pesi crescono con le fioriture e calano dopo la smielatura: una serie
-- piatta non permetterebbe di verificare i grafici dell'andamento (M6).

INSERT INTO ispezioni
    (id, alveare_id, livello_rischio_id, data_ispezione,
     peso_kg, telaini_covata, telaini_scorte, regina_vista, sciamatura, note)
VALUES
    -- A1, stagione 2025
    (1, 1, 1, '2025-04-05', 22.40, 4, 3, TRUE,  FALSE,
     'Ripresa regolare. Covata compatta su quattro telaini.'),
    (2, 1, 1, '2025-05-10', 31.80, 6, 5, TRUE,  FALSE,
     'Acacia in piena fioritura, melario aggiunto.'),
    (3, 1, 1, '2025-06-14', 44.20, 7, 8, FALSE, FALSE,
     'Melario quasi pieno. Regina non vista ma covata fresca presente.'),
    (4, 1, 2, '2025-09-06', 26.10, 3, 6, TRUE,  FALSE,
     'Post smielatura. Trattamento antivarroa eseguito il 2 settembre.'),

    -- A1, stagione 2026
    (5, 1, 1, '2026-03-28', 24.90, 3, 4, TRUE,  FALSE,
     'Invernamento riuscito, consumo scorte nella norma.'),
    (6, 1, 1, '2026-05-16', 35.60, 7, 6, TRUE,  FALSE,
     'Famiglia in forma. Aggiunto secondo melario.'),

    -- A2: la famiglia debole, scorte in calo
    (7, 2, 2, '2025-04-05', 18.20, 2, 3, TRUE,  FALSE,
     'Sviluppo lento rispetto ad A1. Regina del 2023, da valutare la sostituzione.'),
    (8, 2, 3, '2025-06-14', 21.50, 3, 2, FALSE, FALSE,
     'Covata a macchie. Scorte scarse nonostante la stagione buona.'),
    (9, 2, 3, '2026-03-28', 14.80, 2, 1, TRUE,  FALSE,
     'Scorte quasi esaurite, somministrato candito. Famiglia ridotta ma viva.'),
    (10, 2, 3, '2026-05-16', 19.30, 3, 2, TRUE, FALSE,
     'Leggera ripresa ma resta indietro. Sostituzione regina programmata.'),

    -- A3: sospetta varroa. Qui c'e' la nota lunga per l'assistente AI.
    (11, 3, 2, '2025-06-14', 16.40, 3, 2, TRUE, FALSE,
     'Nucleo in crescita regolare. Nessun segno di malattia.'),
    (12, 3, 4, '2026-05-16', 23.70, 4, 3, TRUE, FALSE,
     'Aperto verso le 9.30, giornata coperta e fresca, forse 16 gradi, le api erano nervose piu'' del solito. Ho trovato la regina sul terzo telaino, depone bene, covata compatta su quattro telaini ma su due di questi ho visto celle opercolate affossate e qualche cella aperta con la larva che non sembrava a posto, colore piu'' scuro del normale. Sul fondo dell''arnia, dal cassetto diagnostico, ho contato piu'' o meno una trentina di varroe cadute in tre giorni, che mi sembrano parecchie per maggio. Ho visto anche due o tre api giovani con le ali deformi che camminavano davanti alla porticina senza riuscire a volare. Le scorte ci sono, tre telaini pieni, quindi da mangiare non manca. Ho richiuso senza fare altro perche'' non avevo dietro niente per trattare. Devo assolutamente decidere cosa fare entro questa settimana, se aspettare la fine del raccolto di acacia o intervenire subito, e nel caso capire cosa posso usare che non mi rovini il miele nel melario. Segnare anche di ricontrollare A1 e A2 che sono a due metri di distanza.'),

    -- A4: lo sciame
    (13, 4, 1, '2025-05-10', 28.30, 5, 4, TRUE, FALSE,
     'Situazione normale, nessun segno di sciamatura.'),
    (14, 4, 3, '2026-05-16',  9.60, 1, 2, FALSE, TRUE,
     'Sciamato. Trovate celle reali opercolate, famiglia dimezzata. Recuperato lo sciame sul noce e reinserito con regina nuova.')
AS nuovo
ON DUPLICATE KEY UPDATE
    livello_rischio_id = nuovo.livello_rischio_id,
    peso_kg            = nuovo.peso_kg,
    telaini_covata     = nuovo.telaini_covata,
    telaini_scorte     = nuovo.telaini_scorte,
    regina_vista       = nuovo.regina_vista,
    sciamatura         = nuovo.sciamatura,
    note               = nuovo.note;


-- --------------------------------------------------------------------------- --
-- 4. Raccolti
-- --------------------------------------------------------------------------- --
-- Registrati in entrambi i modi previsti dallo schema (M2-T4): quelli
-- dell'apiario intero hanno `alveare_id` a NULL, quello tenuto separato lo
-- valorizza. Serve a verificare che l'interfaccia gestisca tutti e due i casi.

INSERT INTO raccolti
    (id, apiario_id, alveare_id, tipo_miele_id, data_raccolto, quantita_kg, note)
VALUES
    (1, 1, NULL, 1, '2025-05-28', 34.50,
     'Acacia, smielatura di tutto l''apiario. Annata buona.'),
    (2, 1, NULL, 3, '2025-07-02', 21.00,
     'Castagno, resa inferiore per il caldo di giugno.'),
    (3, 1, 1,    2, '2025-08-30', 12.80,
     'Millefiori estivo, melario di A1 tenuto separato per confronto.'),
    (4, 1, NULL, 1, '2026-05-30', 29.20,
     'Acacia 2026. Fioritura piu'' breve dell''anno scorso.')
AS nuovo
ON DUPLICATE KEY UPDATE
    tipo_miele_id = nuovo.tipo_miele_id,
    quantita_kg   = nuovo.quantita_kg,
    note          = nuovo.note;


-- --------------------------------------------------------------------------- --
-- Fine
-- --------------------------------------------------------------------------- --

SELECT CONCAT(
    'BeeWatch: dati iniziali caricati - ',
    (SELECT COUNT(*) FROM stati_usa),       ' stati USA, ',
    (SELECT COUNT(*) FROM alveari),         ' alveari, ',
    (SELECT COUNT(*) FROM ispezioni),       ' ispezioni, ',
    (SELECT COUNT(*) FROM raccolti),        ' raccolti'
) AS esito;
