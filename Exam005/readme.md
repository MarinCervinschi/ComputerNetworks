# Specifiche

Si chiede di realizzare una rete come quella in figura, con due sottoreti ciascuna dotata di gateway che
effettua NAT. Tutto deve essere realizzato usando un unico switch configurando opportunamente le VLAN

**GWC deve fornire:**
- SNAT per i nodi appartenenti alla rete `192.168.100.0/24`
- Servizio DHCP per il nodo client

**GWS deve fornire:**
- DNAT per il protocollo HTTP sul nodo WebSrv
- DNAT per il protocollo SMTP sul nodo MailSrv
Si chiede inoltre di configurare le opportune regole di firewalling in modo che i server accettino
esclusivamente:
    - Traffico necessario al servizio rilevante per ciascun server (HTTP per WebSrv e SMTP per MailSrv)
    - Traffico ICMP

![image.png](/img/image_5.png)

**Elementi di valutazione:**
1. Il client può raggiungere GWC (verificare con ping)
2. Il client può raggiungere GWS (verificare con ping)
3. Il client può raggiungere il server sulla porte del servizio HTTP (verificare con nc)
4. Il client riceve il suo indirizzo mediante DHCP (se il server DHCP parte automaticamente è meglio)
5. Le VLAN separano le reti (verificare con arping)
6. Le politiche di firewalling sono correttamente implementate (verificare con nc e nc -u su porta
HTTP/SMTP e altra porta da tutti i nodi della rete, incluso l'altro server)

## Schema di rete

### Client 

- Interfaccia: eth0.30
- IP: 192.168.100.X (DHCP)
- Netmask: 255.255.255.0

### GWC

- Interfaccia: eth0.30
- IP: 192.168.100.254
- Netmask: 255.255.255.0

- Interfaccia: eth0.20
- IP: 2.2.2.2
- Netmask: 255.255.255.255

### WebSrv

- Interfaccia: eth0.10
- IP: 192.168.200.1
- Netmask: 255.255.255.0

### MailSrv

- Interfaccia: eth0.10
- IP: 192.168.200.2
- Netmask: 255.255.255.0

### GWS

- Interfaccia: eth0.10
- IP: 192.168.200.254
- Netmask: 255.255.255.0

- Interfaccia: eth0.20
- IP: 1.1.1.1
- Netmask: 255.255.255.255