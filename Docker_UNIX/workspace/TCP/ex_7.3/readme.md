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