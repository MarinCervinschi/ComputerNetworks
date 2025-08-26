# 7.4.1 Specifiche

Su vuole realizzare un’applicazione client/server che consente a un _client_ di scaricare
un file dal _server_.
Il server dovra porsi in attesa di richieste da parte del client sulla porta TCP `8080`.

Una richiesta e costituita da una stringa `JSON` e dal `contenuto` del file che si vuole
caricare. La richiesta deve essere strutturata come di seguito:
se si vuole scaricare il file `file.txt` la richiesta sara strutturata come:

```JSON
{
    "filename": "file.txt",
    "filesize": "853"
}
<853 bytes of file content>
```

A questa richiesta il server dovra recuperare il file e salvarlo all’interno della cartella `uploads`. Mandera inoltre una risposta al client del tipo:

```JSON
{
    "statuscode": 200
}
```

A fronte di questa risposta il client chiudere la connessione.
