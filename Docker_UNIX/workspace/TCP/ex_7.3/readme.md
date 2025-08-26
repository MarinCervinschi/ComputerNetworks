# 7.3.1 Specifiche

Si vuole realizzare un’applicazione client/server che consente a un *client* di scaricare
un file dal *server*.
Il server dovra porsi in attesa di richieste da parte del client sulla porta TCP `8080`.

Una richiesta e costituita da una stringa `JSON` (una notazione che può essere usata per
rappresentare dictionary). La richiesta deve essere strutturata come di seguito: se si
vuole scaricare il file `file.txt` la richiesta sara strutturata come:

```JSON
{
    "filename": "file.txt"
}
```

A questa richiesta il server dovra rispondere con una struttura `JSON` seguita dal
contenuto del file. La risposta dovra contenere le seguenti informazioni:

```JSON
{
    "filename": "file.txt",
    "filesize": "853"
}
<853 bytes of file content>
```

A fronte di questa risposta il client dovra **creare un file** con il nome indicato e
riempirlo con i dati trasferiti dal server, quindi chiudere la connessione con il server.

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
