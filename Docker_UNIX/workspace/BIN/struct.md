# Spiegazione della libreria `struct` in Python

La libreria `struct` in Python è essenziale per lavorare con dati binari, specialmente in contesti di networking dove è necessario convertire tra tipi di dati Python e rappresentazioni binarie.

## Concetti fondamentali della libreria `struct`

### 1. Formattazione dei dati
La libreria `struct` usa stringhe di formato per specificare come i dati devono essere impacchettati o spacchettati:

- `!` - Network order (big-endian) - usato per il networking
- `I` - Unsigned int (4 byte)
- `H` - Unsigned short (2 byte)
- `B` - Unsigned char (1 byte)

### 2. Funzioni principali

- `pack(fmt, v1, v2, ...)` - Converte valori Python in bytes secondo il formato
- `unpack(fmt, buffer)` - Converte bytes nei valori Python secondo il formato
- `calcsize(fmt)` - Calcola la dimensione in bytes della struttura

## Errori comuni e come evitarli

### 1. Ordine dei byte (Endianness)
**Errore:** Dimenticare di specificare l'endianness corretta
**Soluzione:** Usare sempre `!` per il network order

```python
# SBAGLIATO - usa l'endianness nativa del sistema
packed_data = struct.pack('I', value)

# CORRETTO - usa network order (big-endian)
packed_data = struct.pack('!I', value)
```

### 2. Dimensioni dei dati
**Errore:** Usare il tipo di dato sbagliato per la dimensione
**Soluzione:** Conoscere le dimensioni esatte dei tipi

```python
# IP: 4 byte -> unsigned int (I)
# Porta: 2 byte -> unsigned short (H)
```

## Esempi pratici dal codice

### Client side
```python
# Converti IP in network order
ip_packed = socket.inet_aton(ip_str)  # già in network order

# Converti porta in network order
port_packed = struct.pack('!H', port)  # usa '!' per network order

# Prepara il messaggio con byte nulli
message = ip_packed + b'\x00' + port_packed + b'\x00'
```

### Server side
```python
# Estrai i componenti dal buffer
ip_packed = data[:4]          # primi 4 byte: IP
port_packed = data[5:7]       # byte 5-6: porta (salta il nullo a posizione 4)

# Converti i dati
ip_uint32 = struct.unpack('!I', ip_packed)[0]  # unpack restituisce una tupla
port_uint16 = struct.unpack('!H', port_packed)[0]
```

## Best practices

1. **Usare sempre network order** (`!`) per i dati di rete
2. **Verificare le dimensioni** dei dati ricevuti
3. **Documentare il formato** dei messaggi binari
4. **Testare con valori noti** per verificare la correttezza delle conversioni
5. **Usare strumenti di debug** come Wireshark o tcpdump per verificare i dati sulla rete

## Debug del traffico di rete in container Docker Debian

### Opzione 1: Debug con tcpdump

**Vantaggi:** Leggero, funziona in terminale, ideale per container

```bash
# Cattura traffico su localhost (loopback)
tcpdump -i lo -X -s 0 port [PORTA_SERVER]

# Esempio con porta 8080
tcpdump -i lo -X -s 0 port 8080

# Per salvare in un file
tcpdump -i lo -X -s 0 port 8080 -w capture.pcap

# Per vedere solo i dati payload in esadecimale
tcpdump -i lo -X -s 0 'port 8080 and tcp[tcpflags] & tcp-push != 0'
```

**Interpretazione dell'output tcpdump:**
- Cercare i byte in formato esadecimale
- Verificare la sequenza: IP (4 byte) + 0x00 + Porta (2 byte) + 0x00

### Opzione 2: Debug con tshark (Wireshark CLI)

**Vantaggi:** Parsing più avanzato, filtri potenti

```bash
# Cattura e mostra i dati payload
tshark -i lo -f "port 8080" -T fields -e data.data

# Con decodifica esadecimale più leggibile
tshark -i lo -f "port 8080" -x

# Salva in formato pcap per analisi successiva
tshark -i lo -f "port 8080" -w capture.pcap
```

### Esempio pratico di verifica

1. **Avvia tcpdump in un terminale:**
```bash
tcpdump -i lo -X -s 0 port 8080
```

2. **In un altro terminale, esegui client e server**

3. **Verifica nell'output di tcpdump:**
```
15:30:45.123456 IP 127.0.0.1.54321 > 127.0.0.1.8080: Flags [P.], seq 1:9, ack 1, win 65535
    0x0000:  4500 003d 0000 4000 4006 3c73 7f00 0001  E..=..@.@.<s....
    0x0010:  7f00 0001 d431 1f90 1234 5678 9abc def0  .....1...4Vx....
    0x0020:  8018 ffff 1234 0000 c0a8 0101 0000 1f90  .....4..........
    0x0030:  00                                        .
```

In questo output, cercare:
- `c0a8 0101` = IP 192.168.1.1 (4 byte)
- `00` = byte nullo
- `1f90` = porta 8080 (2 byte in network order)
- `00` = byte nullo finale

La libreria `struct` è potente ma richiede attenzione ai dettagli, specialmente quando si lavora con dati binari in contesti di rete dove l'ordine dei byte e le dimensioni dei dati sono critici.