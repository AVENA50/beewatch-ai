# Diagrammi

Qui vivono i **sorgenti** dei diagrammi, accanto alla loro esportazione.

Un `.png` non si modifica: senza il sorgente, il primo che deve correggere una
freccia ridisegna tutto da capo. Tenerli insieme, con lo stesso nome, rende
evidente quando l'immagine non è più aggiornata rispetto al sorgente.

## Contenuto

| Sorgente | Esportazione | Strumento | Stato |
|---|---|---|---|
| `er_diagram.dbml` | `er_diagram.png` | [dbdiagram.io](https://dbdiagram.io/d) | ✅ M2-T4 |
| `architecture.drawio` | `architecture.png` | [draw.io](https://app.diagrams.net) | ⬜ da fare in M3-T1 |
| `workflow.drawio` | `workflow.png` | [draw.io](https://app.diagrams.net) | ⬜ da fare in M3-T4 |

I due file `.drawio` esistono già come tele vuote con una nota dentro che
descrive cosa dovranno contenere: si aprono e si disegna, senza dover ricordare
dove andavano messi.

## Come si modifica un diagramma

### `er_diagram.dbml` — schema del database

1. apri [dbdiagram.io/d](https://dbdiagram.io/d)
2. incolla il contenuto di `er_diagram.dbml` nel pannello di sinistra
3. modifica il testo, non il disegno
4. *Export → PNG*, sovrascrivi `er_diagram.png`
5. committa **entrambi** i file

### `architecture.drawio` e `workflow.drawio`

1. apri [app.diagrams.net](https://app.diagrams.net) e carica il file, oppure
   usa l'estensione *Draw.io Integration* di VS Code e aprilo direttamente
2. disegna
3. *File → Export as → PNG*, con sfondo trasparente disattivato
4. salva l'esportazione qui accanto, con lo stesso nome del sorgente
5. committa **entrambi** i file

## Regole

- **Il sorgente e l'esportazione hanno lo stesso nome.** Cambia solo
  l'estensione.
- **Si modifica il sorgente, mai l'immagine.** Ritoccare un PNG con un editor
  grafico rende impossibile la modifica successiva.
- **Si esporta in PNG**, non in JPEG: il testo dei diagrammi in JPEG diventa
  sfocato.
- **Si committano insieme.** Un'esportazione senza il suo sorgente aggiornato è
  una bugia che qualcuno scoprirà fra due mesi.

I diagrammi vengono richiamati dai documenti in `docs/markdown/` con un
percorso relativo, per esempio:

```markdown
![Diagramma ER](../../diagrams/er_diagram.png)
```

## Cosa non va qui

Screenshot dell'interfaccia e grafici prodotti dal codice vanno in
[`../images/`](../images/): non hanno un sorgente da versionare, si rifanno
eseguendo l'applicazione o il notebook.
