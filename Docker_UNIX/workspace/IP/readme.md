# Specifiche

Realizzare un semplice sistema client/server mediante socket programming che, dato un indirizzo
`IP`, ritorni `classe` dell’indirizzo, `net ID` e indirizzo di `broadcast`.

## Elementi di valutazione:
1. Il codice si avvia
2. Il server si pone in ascolto
3. Il client si connette al server
4. Viene identificata la classe dell’indirizzo
5. Vengono ritornate correttamente `net ID` e `broadcast address`
6. Eventuali errori nell’input sono identificati correttamente
7. Qualità del codice
8. Tempo impiegato per completare la prova

### Informazioni aggiuntive:
- Il **server** non ha parametri da linea di comando e, quando invocato deve mettersi in ascolto sulla
porta `1025` e attendere connessioni
- Il **client** ha due parametri corrispondenti `(1)` all’indirizzo del server (in formato FQDN o IP) e `(2)`
a un indirizzo `IPv4` (es, `192.168.1.2`)
- Quando invocato il **client** apre una connessione `TCP` verso il **server** e invia una stringa
contenente l’indirizzo IP fornito al **client** da linea di comando
- Il **server**, quando riceve i dati dal **client** ritorna una stringa contenente `(1)` la classe dell’indirizzo
(A, B, C, D, E), nel caso di indirizzi di classe A, B o C, anche il `net ID` e l’indirizzo di `broadcast`.

Le informazioni devono essere separate da spazi. In caso di errore deve semplicemente essere
ritornato una stringa `ERROR`


## Esempi di funzionamento

| Input              | Output                              |
|--------------------|-------------------------------------|
| `10.0.0.1`         | `A 10.0.0.0 10.255.255.255`         |
| `155.185.10.1`     | `B 155.185.0.0 155.185.255.255`     |
| `192.168.1.1`      | `C 192.168.1.0 192.168.1.255`       |
| `192.168.`         | `ERROR`                             |
| `192.157.1.1`      | `ERROR`                             |
| `192.F0.1.1`       | `ERROR`                             |
| `Prova`            | `ERROR`                             |
