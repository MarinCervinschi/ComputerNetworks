# Laboratorio

 Si chiede di realizzare una rete come quella in figura, in cui GW fornisce connettività a due sottoreti:
- `192.168.1.0/24` con Srv1 e H1
- `192.168.2.0/24` con Srv2 e H2

GW deve fornire connettività a entrambe le reti avendo a disposizione una sola scheda di rete collegato allo 
switch SW (usare opportunamente le VLAN e le schede di rete virtuali)

 Si chiede inoltre di implementare sul nodo GW:
 - SNAT per ogni nodo delle reti considerate
 - DNAT per un server sulla porta 80 di Srv1 che deve apparire sulla porta 80 di GW
 - DNAT per un server sulla porta 80 di Srv2 che deve apparire sulla porta 8000 di GW

 ![image.png](/img/image_10.png)

**Elementi di valutazione:**
 1. C’è comunicazione all’interno di ogni sottorete (Srv2 con H2, Srv1 con H1 – verificare con ping)
 2. C’è comunicazione di ogni nodo con GW (incluso Ext – verificare con ping) ma il dominio di 
collisione è separato (verificare con arping e tcpdump)
 3. C’è comunicazione tra elementi di sottoreti diverse (Srv2 con H1, Srv1 con H2 – verificare con 
ping)
 4. Il SNAT su GW consente a ciascun nodo in una sottorete di contattare Ext  (verificare con ping)
 5. Il DNAT su GW consente a Ext di contattare Srv1 e Srv2 (verificare con nc)

## Schema di rete

### H1

   - **NetID**: 192.168.1.0
   - **VLANID**: 10
   - **Interfaccia**: eth0
        - **Indirizzo IP**: 192.168.1.2
        - **Netmask**: 255.255.255.0

### Srv1

   - **NetID**: 192.168.1.0
   - **VLANID**: 10
   - **Interfaccia**: eth0
        - **Indirizzo IP**: 192.168.1.1
        - **Netmask**: 255.255.255.0

### H2

   - **NetID**: 192.168.2.0
   - **VLANID**: 20
   - **Interfaccia**: eth0
        - **Indirizzo IP**: 192.168.2.2
        - **Netmask**: 255.255.255.0

### Srv2

   - **NetID**: 192.168.2.0
   - **VLANID**: 20
   - **Interfaccia**: eth0
        - **Indirizzo IP**: 192.168.2.1
        - **Netmask**: 255.255.255.0

### GW
- **Interfaccia**: eth0.10
   - **Indirizzo IP**: 192.168.1.254
   - **Netmask**: 255.255.255.0
- **Interfaccia**: eth0.20
   - **Indirizzo IP**: 192.168.2.254
   - **Netmask**: 255.255.255.0
- **Interfaccia**: eth1
   - **Indirizzo IP**: 1.1.1.1
   - **Netmask**: 255.255.255.255

### EXT
- **Interfaccia**: eth0
   - **Indirizzo IP**: 2.2.2.2
   - **Netmask**: 255.255.255.255