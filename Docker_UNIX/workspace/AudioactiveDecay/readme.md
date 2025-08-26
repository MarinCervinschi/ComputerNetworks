# Specifiche

Scrivere un server di rete che implementi il processo di decadimento audioattivo
di Conway (DAC) come descritto in:

https://en.wikipedia.org/wiki/Look-and-say_sequence

Il *server* deve gestire richieste concorrenti mediante uso di `systemcall fork()` e
porsi in ascolto sulla porta `8080`. Il protocollo prevede che l’input sia come segue:
```bash
<seed>,<niterations>\r\n
```
Il parametro `seed` deve essere una sola cifra, mentre il `numero di iterazioni` deve
essere un numero intero. Se la validazione dell’input è corretta viene ritornato un
output del tipo:
```bash
+OK <niterations> iterations on seed <seed>
```
Mentre le righe successive implementano il decadimento audioattivo partendo
dalla riga precedente (o dal `seed` per la prima iterazione). In caso di errore viene
ritornato semplicemente un messaggio del tipo:
```bash
- ERR
```
Esempi di interazione tra client e server sono delineati di seguito:

```bash
C: 1,5\r\n
S: + OK 5 iterations on seed 1\r\n
S: 11\r\n
S: 21\r\n
S: 1211\r\n
S: 111221\r\n
S: 312211\r\n
C: 1, 5\r\n
S: - ERR\r\n
```

Elementi di valutazione
- Gli input sono stati validati (presenza di caratteri non permessi, assenza di parametri, etc. . . )
- L’output del server è consistente con le specifiche
- La logica del decadimento audioattivo è corretta


Informazioni aggiuntive:
- Per validare velocemente il funzionamento si può usare un one liner come segue:
```bash
echo '1,5' | nc -q1 -C localhost 8080
```