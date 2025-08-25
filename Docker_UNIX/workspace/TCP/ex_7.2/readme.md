# 7.2.1 Specifiche
Si vuole realizzare un’applicazione client/server in cui il client comunica al server il
proprio hostname. Il server non deve prevedere parametri dai linea di comando. Il
server si pone in ascolto sulla porta `2525` mediante il protocollo TCP. Il client prevede
come unica parametro il nome del server a cui connettersi (la porta anche in questo
caso e hardcoded e corrisponde alla porta `2525`).

Quando il client si connette, trasmette immediatamente al server trasmette il seguente messaggio di presentazione: `Connection from <hostname>`, dove hostname e il nome del client e chiudere la connessione. Il server dovrà mostrare quanto ricevuto dal client sul suo standard output.
Si chiede di realizzare:
- programma server scritto in Python
- programma client scritto in Python
- versione con server che supporta richieste multiple in parallelo mediante fork()

## 7.2.2 Elementi di verifica
La correttezza di quanto fatto si puo valutare sulla base delle osservazioni già discusse nel caso precedente, con le seguenti modifiche per tenere conto della peculiarità dell’applicazione:
- Il client manda l’hostname quando un generico client si connette (verificare con
`nc -l -p 2525` al posto del server)
- Il server riceve e mostra la stringa mandata dal client (verificare con `hostname | nc -q1 <server> 2525` al posto del client)

## Verifica del Funzionamento

### 1. Verifica con netcat come server

```bash
# Terminale 1: Avvia netcat in ascolto
nc -l -p 2525

# Terminale 2: Esegui il client
python client.py localhost
```

Dovresti vedere nel terminale 1 il messaggio "Connection from [hostname-del-client]".

### 2. Verifica con netcat come client

```bash
# Terminale 1: Avvia il server
python server.py

# Terminale 2: Usa netcat come client
hostname | nc -q1 localhost 2525
```

Dovresti vedere nel terminale 1 il messaggio "[hostname]".

### 3. Verifica del server con fork

```bash
# Terminale 1: Avvia il server con fork
python server_fork.py

# Terminale 2: Esegui multiple client
for i in {1..5}; do python client.py localhost & done
```

Dovresti vedere nel terminale 1 i messaggi ricevuti da tutti i client.
