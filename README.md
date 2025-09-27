# **Table of Contents**

- [**Table of Contents**](#table-of-contents)
  - [WelbyBot](#welbybot)
  - [1. Comandi disponibili](#1-comandi-disponibili)
    - [`/start`](#start)
    - [`/schedule`](#schedule)
  - [2. Trigger](#2-trigger)
  - [3. Messaggi automatici](#3-messaggi-automatici)
  - [4. Errori o Richieste](#4-errori-o-richieste)
  - [5. Comportamento](#5-comportamento)
  - [6. Contatti](#6-contatti)
    - [6bis. Contestazioni](#6bis-contestazioni)
  - [7. Versione](#7-versione)

## WelbyBot  

**WelbyBot** è un bot Telegram, di nome *ANoDoRea*, installato e gestito dall'**Autismo Centrale**.  

Questo documento fornisce le istruzioni per utilizzare i comandi disponibili e interagire con il bot.  
Qualsiasi richiesta di modifica o segnalazione di errore va inviata tramite **GitHub** (vedi sezione finale).

---

## 1. Comandi disponibili

### `/start`

Mostra un messaggio di presentazione del bot.  

**Sintassi:**

```plain
/start
```

### `/schedule`

Programma l’invio di un messaggio nel gruppo dopo un intervallo specificato.

**Sintassi:**

```plain
/schedule <unità> <valore> <messaggio>
```

| Parametro     | Tipo                  | Descrizione                                  |
| ------------- | --------------------- | -------------------------------------------- |
| `<unità>`     | `s` / `m` / `h` / `d` | Unità di tempo: secondi, minuti, ore, giorni |
| `<valore>`    | numero                | Valore da attendere (intero o decimale)      |
| `<messaggio>` | testo                 | Messaggio che il bot invierà nel gruppo      |

**Esempi:**

```plain
/schedule s 30 Uè sfigato
/schedule m 10 Assaggia sto liquido
/schedule h 1.5 Il periodo refrattario è terminato
```

Il messaggio pianificato includerà la data e l’ora in cui è stato schedulato.

---

## 2. Trigger

*ANoDoRea* risponde automaticamente a determinati termini presenti nei messaggi.  
Le risposte sono predefinite e non richiedono comandi.

| Parola chiave | Azione                           |
| ------------- | -------------------------------- |
| `negr`        | Risposta automatica preimpostata |
| `palle`       | Risposta automatica preimpostata |
| `sindaco`     | Risposta automatica preimpostata |

Le risposte vengono inviate solo se una delle parole chiave è contenuta nel testo.  
Se presenti più parole chiave, le risposte verranno concatenate ed enumerate in un solo messaggio.  

---

## 3. Messaggi automatici

*ANoDoRea* invia messaggi informativi nel gruppo in corrispondenza di:

- **Avvio del servizio**: il bot segnala di essere online
- **Spegnimento del servizio**: il bot segnala la chiusura o l’interruzione

---

## 4. Errori o Richieste

Per segnalare un malfunzionamento o proporre una nuova funzione:

1. Accedere alla **[pagina](https://github.com/m-contini/WelbyBot)** GitHub del progetto:

2. Cliccare su **[Issues](https://github.com/m-contini/WelbyBot/issues)** > **New Issue**

3. Compilare il titolo e la descrizione:

   - **Titolo:** breve descrizione del problema o della richiesta
   - **Descrizione:** includere, se possibile:
     - Data e ora dell’evento
     - Comando usato o messaggio inviato
     - Eventuale messaggio di errore
     - Comportamento atteso

4. Cliccare su **Submit new issue**  

---

## 5. Comportamento

- Il bot è attivo solo all’interno del gruppo per cui è stato configurato.  
- I comandi devono essere inviati direttamente nel gruppo, **non in chat privata**.  
- I messaggi programmati vengono inviati nel gruppo e includono data e ora della pianificazione.  
- I messaggi non conformi alla sintassi verranno ignorati o genereranno un messaggio di errore.

---

## 6. Contatti  

Il bot è gestito e mantenuto da **[@kengo14](http://telegram.me/kengo14)**.  
Gli utenti non possono modificarne il comportamento o le impostazioni.  
Ogni aggiornamento o nuova funzione verrà comunicato (forse).

### 6bis. Contestazioni  

Contattare il Potere dell'Autismo Centrale.

---

## 7. Versione

**Versione:** 1.1  
**Data rilascio:** 2025-09-28

---

© 2025 — Tutti i diritti riservati.  
WelbyBot è uno strumento interno non destinato a uso pubblico.
Nessuno si assume la responsabilità delle volgarità eventuali prodotte da *ANoDoRea*.
