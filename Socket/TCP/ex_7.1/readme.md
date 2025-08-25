# 7.1.1 Specifiche
Si vuole realizzare un’applicazione **client/server** in cui il server comunica al client il
proprio *hostname*. Il server non deve prevedere parametri dai linea di comando. Il
server si pone in ascolto sulla porta `2525` mediante il protocollo **TCP**. Il client prevede
come **unico parametro** il `nome` del server a cui connettersi (la porta anche in questo
caso e hardcoded e corrisponde alla porta `2525`).

Quando il client si connette, il server trasmette il seguente messaggio di benvenuto:
`Welcome from <hostname>`, dove hostname è il nome del server. Il client dovrà
mostrare quanto ricevuto dal server sul suo standard output e chiudere la connessione
In Python la funzione che si può usare a tale scopo è `socket.gethostname()`
che ritorna una stringa.
Si chiede di realizzare:
- programma server scritto in Python
- programma client scritto in Python
- versione con server che supporta richieste multiple in parallelo mediante fork()

## 7.1.2 Elementi di verifica
La correttezza i quanto fatto si puo valutare con le seguenti osservazioni:
- Esecuzione senza eccezioni del software in Python
- Il server quando lanciato si mette in ascolto sulla porta indicata (verificare con `netstat -ntlp`)
- Il server manda l’hostname quando un generico client si connette (verificare con `nc <server> 2525` al posto del client)
- Il client riceve e mostra la stringa mandata dal server (verificare con `hostname | nc -l -p 2525 -q 1` al posto del server)
- Il client si comporta correttamente quando si interfaccia con il server
- Corretta interoperabilita tra le versioni Python e C del software (server Python e client C)
- Corretto funzionamento della versione che supporta richieste multiple

Ecco l'implementazione dei programmi client e server secondo le specifiche richieste:

### Istruzioni per l'uso:

1. **Avvio del server**:
   ```bash
   python server.py
   ```
   o per la versione con fork:
   ```bash
   python server_fork.py
   ```

2. **Avvio del client**:
   ```bash
   python client.py localhost
   ```
### Come compilare e usare il client in C

1. **Salva il codice** in un file chiamato `client.c`

2. **Compila il client** con il compilatore GCC:
   ```bash
   gcc -o client client.c
   ```

3. **Esegui il client**:
   ```bash
   ./client localhost
   ```
   oppure
   ```bash
   ./client nome_server
   ```

4. **Verifica il funzionamento**:
   - Assicurati che il server Python sia in esecuzione
   - Esegui il client C specificando l'indirizzo del server
   - Dovresti vedere il messaggio "Welcome from [hostname]"
