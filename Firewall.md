## Firewall

Quando si lavora con i firewall, è buona pratica seguire un approccio graduale: pulizia delle regole esistenti, definizione di policy di default, e apertura selettiva del traffico necessario.

### Scenario di riferimento

Per coerenza, tutti gli esempi utilizzano questo schema di rete:

- **Firewall (gateway)**
    - `eth0` → `10.0.1.1`
    - `eth1` → `192.168.0.1`
    - `eth2` → `5.4.3.2`
- LAN `10.0.1.0/25`
    - H1: `10.0.1.10`
    - H2: `10.0.1.11`
- DMZ `192.168.0.0/24`
    - Web server: `192.168.0.100`
    - FTP server: `192.168.0.101`
    - DNS server: `192.168.0.102`
- Internet
    - EXT `2.3.4.5`

### Pulizia delle regole esistenti

```bash
#!/bin/bash

# Svuota tutte le regole esistenti
iptables -F
iptables -t nat -F
iptables -t mangle -F

# Elimina tutte le catene personalizzate
iptables -X
iptables -t nat -X
iptables -t mangle -X

# Ripristina le policy di default (tutto ACCETTATO)
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT

echo "Firewall reset: tutte le regole rimosse, traffico consentito."

```

### Policy di blocco totale

Per implementare la negazione implicita del traffico, si possono impostare le policy di default a DROP:

```bash
# Policy di default (blocco totale)
iptables -t filter -P INPUT DROP
iptables -t filter -P OUTPUT DROP
iptables -t filter -P FORWARD DROP
```
> ⚠️ Con queste regole, tutto il traffico è bloccato se non esistono eccezioni specifiche.

### DHCP

Quando blocchiamo esplicitamente tutto il traffico per permettere l'assegnamento degli IP in modo dinamico agli host della LAN dobbiamo consentire il traffico DHCP

**DHCP utilizza UDP sulle porte:**
- `67` → server DHCP
- `68` → client DHCP

🔹 **Primo caso: server DHCP sul firewall (GW)**

- Consentire le *richieste DHCP* dalla **DMZ** verso il **firewall** (client → server): 
    
    ```bash
    iptables -A INPUT -i $DMZ_IF -p udp --sport 68 --dport 67 -j ACCEPT
    ```
    - **Catena:** `INPUT` → pacchetti diretti al firewall.
    - **Interfaccia:** `-i $DMZ_IF` → solo pacchetti in arrivo sull'interfaccia della DMZ.
    - **Protocollo:** `-p udp` (DHCP usa UDP).
    - **Porte:**  `--sport 68 --dport 67` → dal client (68) al server DHCP (67).
    - **Azione:** `ACCEPT` → lascia passare queste risposte verso lo stack locale.

- Consentire le *risposte DHCP* dal **firewall** verso la **DMZ** (porta 67 → 68)
    ```bash
    iptables -A OUTPUT -o $DMZ_IF -p udp --sport 67 --dport 68 -j ACCEPT
    ```
    * **Catena:** `OUTPUT` → pacchetti originati dal firewall.
    * **Interfaccia:** `-o $DMZ_IF` → inviati sull'interfaccia della DMZ
    * **Porte:** `--sport 67 --dport 68` → **dal server (67) al client (68)**.
    - **Azione:** `ACCEPT` → lascia passare queste risposte verso lo stack locale.

🔹 **Secondo caso: server DHCP su un’altra LAN (relay DHCP sul firewall)**

In questo scenario il firewall agisce come DHCP relay, inoltrando richieste/riposte tra gli host della DMZ e il server DHCP esterno.
- Consentire l’invio delle *richieste DHCP* dal **firewall** verso il **server DHCP** sulla LAN:
    ```bash
    iptables -A OUTPUT -o $LAN_IF -p udp -s $IP_DMZ_HOST --sport 67 -d $IP_DHCP_SERVER --dport 67 -m state --state NEW,ESTABLISHED -j ACCEPT
    ```
    - **Catena:** `OUTPUT`
    - **Interfaccia:** `$LAN_IF` ovvero quella della LAN dove sta il server DHCP
    - **Origine:** `$IP_DMZ_HOST` indirizzo IP dell'host della DMZ che effettua la richiesta
    - **Destinazione** `$IP_DHCP_SERVER` indirizzo IP del server DHCP che si trova su LAN
    - **Porte:** `67 → 67` perché il relay genera nuovi pacchetti per il server DHCP
 - Consentire le *risposte DHCP* del **server DHCP** sulla LAN verso il **firewall**
    ```bash
    iptables -A INPUT -i $LAN_IF -p udp -s $IP_DHCP_SERVER --sport 67 -d $IP_DMZ_HOST --dport 67 -m state --state ESTABLISHED -j ACCEPT
    ```
    - **Catena:** `INPUT`
    - **Interfaccia:** `$LAN_IF`
    - **Origine:** `$IP_DHCP_SERVER`
    - **Destinazione:** `$IP_DMZ_HOST`
    - **Porte:** `67 → 67`
> ⚠️ **Nota:** nello scenario relay, i pacchetti DHCP non mantengono le porte client/server originali. Il firewall agisce in prima persona nei confronti del server DHCP esterno.

***Verifica del funzionamento***:
```bash
ifdown -a   # Su un host che utilizza DHCP
ifup -a     # Su un host che utilizza il DHCP
```
Gli host dovranno ricevere correttamente un indirizzo IP dalla rete prevista.

### DNS
Il DNS è il servizio che permette di risolvere nomi di dominio in indirizzi IP. Per garantire la connettività tra client e server DNS, è necessario configurare correttamente il firewall, consentendo sia le richieste dei client sia le risposte del server.
| Catena      | Quando si usa                                             | Esempio DNS                                                                           |
| ----------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **INPUT**   | Pacchetti destinati al firewall stesso                    | Richieste DNS che il firewall deve processare localmente (server DNS sul firewall)    |
| **OUTPUT**  | Pacchetti generati dal firewall                           | Risposte DNS generate dal firewall verso i client                                     |
| **FORWARD** | Pacchetti che **attraversano il firewall** tra due subnet | Richieste DNS dai client della DMZ verso un server DNS nella LAN, e relative risposte |
> 🗝️ il FORWARD si usa solo se il traffico non è destinato al firewall, ma deve passare da una rete all’altra.

1. **Traffico DNS verso il firewall (INPUT/OUTPUT):**

    Per consentire ai client della LAN o DMZ di interrogare il server DNS sul firewall:
    ```bash
    NET_ID_LAN=10.0.1.0/25
    # Richieste in ingresso al firewall (porta destinazione 53)
    iptables -A INPUT -i $LAN_IF -p udp -s $NET_ID_LAN --dport 53 -m state --state NEW,ESTABLISHED -j ACCEPT

    # Risposte generate dal firewall verso i client
    iptables -A OUTPUT -o $LAN_IF -p udp -d $NET_ID_LAN --sport 53 -m state --state ESTABLISHED -j ACCEPT
    ```
    Spiegazione porte:

    * Le richieste DNS dei client partono generalmente da porte alte casuali verso porta 53 del server.
    * Le risposte del server DNS vengono inviate dalla porta 53 verso la porta alta del client.
    * Questo schema spiega perché in INPUT si usa `--dport 53` e in OUTPUT `--sport 53`.

2. **Regole DNS per traffico tra subnet (FORWARD)**
    Se il firewall deve inoltrare le richieste DNS dalla DMZ verso un server DNS nella LAN:
    ```bash
    NET_ID_DMZ=155.185.1.0/29
    IP_DNS_SERVER=192.168.1.253

    # Richieste DNS DMZ -> LAN
    iptables -t filter -A FORWARD -i $DMZ_IF -o $LAN_IF -p udp --dport 53 -s $NET_ID_DMZ -d $IP_DNS_SERVER -m state --state NEW,ESTABLISHED -j ACCEPT

    # Risposte DNS LAN -> DMZ
    iptables -t filter -A FORWARD -i $LAN_IF -o $DMZ_IF -p udp --sport 53 -s $IP_DNS_SERVER -d $NET_ID_DMZ -m state --state ESTABLISHED -j ACCEPT
    ```

    Spiegazione:

    - **Il traffico DNS attraversa il firewall:** i pacchetti non sono destinati al firewall stesso, ma devono essere inoltrati tra subnet diverse.
    - `--dport 53` per le richieste (arrivano alla porta 53 del server)
    - `--sport 53` per le risposte (partono dalla porta 53 del server verso la porta alta del client)
    - La connessione viene tracciata con state `NEW,ESTABLISHED` per le richieste e `ESTABLISHED` per le risposte.

***Verifica del funzionamento***:
```bash
dig google.com
```
Se ricevi una risposta corretta, significa che le regole INPUT, OUTPUT e FORWARD consentono correttamente le richieste e le risposte DNS

### SSH

Il servizio SSH permette di gestire in modo sicuro i dispositivi della rete tramite accesso remoto. Per consentire connessioni SSH verso il firewall o server dalla LAN, è necessario configurare correttamente le regole del firewall.

```bash
LAN_HOST=192.168.1.2
# Consentire connessioni SSH da un host della LAN al Firewall
iptables -A INPUT -i $LAN_IF -p tcp -s $LAN_HOST --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT

# Consentire risposte SSH dal Firewall all'host della LAN
iptables -A OUTPUT -o $LAN_IF -p tcp -d $LAN_HOST --sport 22 -m state --state ESTABLISHED -j ACCEPT
```

**Spiegazione delle regole:**

- **INPUT**
    - `-i $LAN_IF` → pacchetti in arrivo sull’interfaccia della LAN.
    - `-p tcp` → SSH utilizza TCP.
    - `--dport 22` → porta standard SSH.
    - `-s <subnet>` → solo il client autorizzato può connettersi.
    - `--state NEW,ESTABLISHED` → permette nuove connessioni e pacchetti di sessioni già stabilite.
    - `-j ACCEPT` → accetta i pacchetti corrispondenti.

- **OUTPUT**
   - `-o $LAN_IF` → pacchetti in uscita sull’interfaccia LAN.
   - `--sport 22` → pacchetti generati dal firewall/host SSH.
   - `-d <subnet>` → verso il client autorizzato.
   - `--state ESTABLISHED` → solo pacchetti di sessioni già aperte.
   - `-j ACCEPT` → accetta i pacchetti di risposta.

***Verifica del funzionamento***:
```bash
ssh <ip> #DALLA LAN
```

### HTTP
Il servizio HTTP utilizza il protocollo TCP sulla porta 80. Per permettere l’accesso a un server web da Internet o dalla LAN, è necessario configurare correttamente le regole FORWARD del firewall.

1. **Connessioni da Internet verso il server web su DMZ**

    Consentire a qualunque host esterno su Internet di connettersi al server web pubblico su DMZ:

    ```bash
    IP_SRV=155.185.1.1

    iptables -A FORWARD -p tcp --dport 80 -i $EXT_IF -o $DMZ_IF -d $IP_SRV -m state --state NEW,ESTABLISHED -j ACCEPT

    iptables -A FORWARD -p tcp --sport 80 -i $DMZ_IF -o $EXT_IF -s $IP_SRV -m state --state ESTABLISHED -j ACCEPT

    ```
    Spiegazione:
    - `$EXT_IF → $DMZ_IF`: traffico proveniente da Internet verso la DMZ.
    - `--dport 80`: pacchetti destinati al server web.
    - `--state NEW,ESTABLISHED`: consente sia nuove connessioni sia pacchetti di sessioni già aperte.
    - Regola inversa (`--sport 80`): consente le risposte del server verso l’host esterno.

     > ⚠️ se il server ha un indirizzo privato, devi anche configurare la regola di PREROUTING per il NAT, in modo che il traffico in ingresso venga inoltrato correttamente al server privato.


2. **Connessioni dalla LAN verso il server web su DMZ**
    Consentire agli host della LAN di raggiungere il server web sulla DMZ:
    ```bash
    IP_SRV=155.185.1.1

    iptables -A FORWARD -p tcp --dport 80 -i $LAN_IF -o $DMZ_IF -d $IP_SRV -m state --state NEW,ESTABLISHED -j ACCEPT
    
    iptables -A FORWARD -p tcp --sport 80 -i $DMZ_IF -o $LAN_IF -s $IP_SRV -m state --state ESTABLISHED -j ACCEPT
    ```
    Spiegazione:
    - `-i $LAN_IF -o $DMZ_IF` → traffico originato dalla LAN verso la DMZ.
    - `--dport 80` → porta di destinazione HTTP.
    - Risposte tracciate con `--sport 80` e stato ESTABLISHED.

3. **Connessioni dalla LAN verso un server Web in esecuzione su EXT**
    Se il server web è pubblico (es. EXT) per permettere alla LAN di contattarlo:

    ```bash
    NET_ID_LAN=10.42.0.0/25
    IP_EXT=2.20.20.20

    iptables -A FORWARD -i $LAN_IF -o $EXT_IF -p tcp -s $NET_ID_LAN -d $IP_EXT --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
    
    iptables -A FORWARD -i $EXT_IF -o $LAN_IF -p tcp -s $IP_EXT -d $NET_ID_LAN --sport 80 -m state --state ESTABLISHED -j ACCEPT

    ```   

**Spiegazione**

- Le richieste partono da porte alte casuali dei client verso la porta 80 del server web (`--dport 80`).

- Le risposte del server partono dalla porta 80 verso le porte alte dei client (`--sport 80`).

- Il modulo state (`NEW,ESTABLISHED`) traccia lo stato delle connessioni TCP, consentendo solo pacchetti validi.

***Verifica del funzionamento***: <!-- Probabilmente non va bene, va usato nc -->
```bash
nc -l -p 80         # Server
nc -vz <IP> 80      # Client
```
- `-l -p 80` → ascolta sulla porta 80 del server
- `-vz` → connessione di test dal client (verbose + scan della porta)

Se la connessione viene stabilita, significa che le regole FORWARD permettono correttamente il traffico HTTP tra client e server.

### ICMP

Il protocollo ICMP viene utilizzato per scopi diagnostici e di controllo, ad esempio:
- **Ping** (echo request/echo reply) per verificare la raggiungibilità di un host.
- **Messaggi di errore** (es. destination unreachable, time exceeded) necessari al corretto funzionamento della rete.

Per questo motivo, solitamente si consente il traffico ICMP sia in ingresso, che in uscita, che in inoltro.

```bash
iptables -t filter -A INPUT   -p icmp -j ACCEPT
iptables -t filter -A OUTPUT  -p icmp -j ACCEPT
iptables -t filter -A FORWARD -p icmp -j ACCEPT
```
Spiegazione:

- **INPUT**: consente che l’host firewall possa ricevere richieste ICMP (es. venga “pingato”).

- **OUTPUT**: consente che il firewall possa generare richieste ICMP (es. fare ping a un altro host).

- **FORWARD**: permette che i pacchetti ICMP possano attraversare il firewall (utile se i client della LAN devono pingare host su Internet o viceversa).

***Verifica del funzionamento***
```bash
ping <IP_destinazione>
```

Se ricevi risposta, significa che le regole ICMP permettono correttamente la comunicazione.

### NAT
Il NAT (Network Address Translation) viene utilizzato per tradurre indirizzi IP (sorgente o destinazione) nei pacchetti che attraversano il firewall/router.

**La logica generale:**

- **Da Internet → Rete privata**

    Si utilizza **PREROUTING** → DNAT per tradurre l’IP di destinazione pubblico in un IP privato (es. port forwarding).

    Il **DNAT** (Destination NAT) permette di pubblicare un servizio interno rendendolo raggiungibile da Internet tramite l’IP pubblico del firewall.

    ```bash
    IP_SRV_HTTP=155.185.1.1

    # EXT -> SRV: HTTP -> 80
    iptables -t nat -A PREROUTING -p tcp --dport 8080 -i $EXT_IF -j DNAT --to-destination $IP_SRV_HTTP:80
    ```

    > ⚠️ Dopo un DNAT, serve anche permettere il forwarding verso il server interno (**vedi sezione HTTP**)

    ***Verifica del funzionamento***
    ```bash
    nc -l -p 80  #su SRV
    nc -vz <IP_pubblico_firewall> 8080
    
    ```

- **Da Rete privata → Internet**

    Si utilizza **POSTROUTING** → SNAT o MASQUERADE per sostituire l’IP sorgente privato con l’IP pubblico del gateway.

    Il **MASQUERADE** è una forma speciale di SNAT usata quando l’IP pubblico è dinamico (tipico negli accessi domestici o tramite PPPoE).

    ```bash
    NET_ID_LAN=10.0.1.0/25
    
    iptables -t nat -A POSTROUTING -o $EXT_IF -s $NET_ID_LAN  -j MASQUERADE
    ```
    > ⚠️ Se non specificassimo `-s <subnet>` tutto il traffico che esce da $EXT_IF (non solo quello proveniente dalla rete 10.0.1.0/25) verrebbe mascherato. Questo potrebbe includere anche pacchetti provenienti da altre interfacce/reti interne (es. DMZ).


    ***Verifica del funzionamento***
    ```bash
    tcpdump -i $EXT_IF
    # Controllare che i pacchetti in uscita abbiano come IP sorgente quello pubblico del firewall
    ```

### FTP

L’FTP utilizza due connessioni TCP:

- **Porta 21 (control connection):** usata dal client per inviare comandi al server.

- **Porta 20 (ftp-data) o porte dinamiche (>1023)**: usate per il trasferimento dati, a seconda della modalità.

Esistono due modalità operative:

- **Active mode**: il server apre la connessione dati da porta 20 verso una porta effimera del client.

- **Passive mode**: il server comunica al client una porta >1023 su cui aprire la connessione dati, ed è il client ad avviarla.

> Consentire connessioni *TCP* sulla porta 21 da Internet verso il server *FTP ftp.fake.com* e consentire le risposte
```bash
IP_SRV_FTP=155.185.1.2
# Connessione control (porta 21)
iptables -t filter -A FORWARD -i $EXT_IF -o $DMZ_IF -d $IP_SRV_FTP -p tcp --dport 21 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A FORWARD -i $DMZ_IF -o $EXT_IF -s $IP_SRV_FTP -p tcp --sport 21 -m state --state ESTABLISHED -j ACCEPT

```
> Per il trasferimento dati il server apre una nuova connessione TCP da porta 20 (ftp-data) verso una porta sul client
```bash
# Trasferimento dati (porta 20)
iptables -t filter -A FORWARD -p tcp --sport 20 -i $EXT_IF -o $DMZ_IF -s $IP_SRV_FTP -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -t filter -A FORWARD -p tcp --dport 20 -i $DMZ_IF -o $EXT_IF -d $IP_SRV_FTP -m state --state ESTABLISHED -j ACCEPT
```

***Verifica del funzionamento***:
```bash
ftp 5.4.3.2    # Da host esterno
# Controllare che login e trasferimento dati funzionino correttamente
```