# Laboratorio

 Si chiede di realizzare una rete come quella in figura, in cui R1 fornisce connettività a tre sottoreti:
 - `192.168.20.0/24` con Cli1 e Cli2 (configurati mediante DHCP)
 - `192.168.30.0/24` con SrvInt
 - `155.185.48.0/24` con SrvExt

 GW deve fornire connettività a tutte le reti avendo a disposizione una sola scheda di rete collegato allo switch SW (usare opportunamente le VLAN e le schede di rete virtuali)
 
 Si chiede inoltre di implementare sul nodo GW:
 - SNAT per ogni rete con indirizzi privati
 - DNAT per un server sulla porta 80 di SrvInt che deve apparire sulla porta 8000 di R1 e deve essere raggiungibile da tutti le reti

![image.png](/img/image_9.png)

**Elementi di valutazione:**
 1. C’è comunicazione La configurazione DHCP di Cli1 e Cli2 funziona
 2. C’è comunicazione di ogni nodo con R1 ma il dominio di collisione è separato (verificare con ping e arping)
 3. Per ogni sottorete, le interfacce di R1 devono avere il più alto hostID disponibile
 4. SrvExt, Cli1, Cli2 possono dialogare con SrvInt usando il DNAT (verificare con nc)
 5. Cli1 e Cli2 possono dialogare con SrvExt (verificare con ping e controllare con tcpdump il funzionamento del SNAT)

  ## Schema di rete

 ### Cli1 e Cli2

   - **NetID**: 192.168.20.0
   - **VLANID**: 20
   - **Interfaccia**: eth0
        - **Indirizzo IP**: DHCP
        - **Netmask**: 255.255.255.0

### SrvExt
   - **NetID**: 155.185.48.0
   - **VLANID**: 10
   - **Interfaccia**: eth0
        - **Indirizzo IP**: 155.185.54.1
        - **Netmask**: 255.255.255.0

### SrvInt
   - **NetID**: 192.168.30.0
   - **VLANID**: 30
   - **Interfaccia**: eth0
        - **Indirizzo IP**: 192.168.30.1
        - **Netmask**: 255.255.255.0

### R1
- **Interfaccia**: eth0.10
   - **Indirizzo IP**:
   - **Netmask**: 255.255.255.0
- **Interfaccia**: eth0.20
   - **Indirizzo IP**:
   - **Netmask**: 255.255.255.0
- **Interfaccia**: eth0.30
   - **Indirizzo IP**: 
   - **Netmask**: 255.255.255.0