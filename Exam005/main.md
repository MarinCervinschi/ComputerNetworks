## Initial Configuration

Guarda il [readme.md](./readme.md)

## Configurazione VLAN

Dentro lo SWITCH S1

```bash
vlan/create 10
vlan/create 20
vlan/create 30

# access link
port/setvlan 1 30 # Client
port/setvlan 2 10 # WebSrv
port/setvlan 3 10 # MailSrv

# trunk link
vlan/addport 30 4 # GWC
vlan/addport 20 4 # GWC
vlan/addport 10 5 # GWS
vlan/addport 20 5 # GWS
```

## Configurazione ip

### Client

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname Client
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Client network configuration added."
```

### WebSrv

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.200.1
        netmask 255.255.255.0
        gateway 192.168.200.254
        hostname WebSrv
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> WebSrv network configuration added."
```

### MailSrv

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.200.2
        netmask 255.255.255.0
        gateway 192.168.200.254
        hostname MailSrv
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> MailSrv network configuration added."
```

### GWC

```bash
#!/bin/bash

interfaces="
auto eth0.30
iface eth0.30 inet static
        address 192.168.100.254
        netmask 255.255.255.0

auto eth0.20
iface eth0.20 inet static
        address 2.2.2.2
        netmask 255.255.255.255

post-up ip route add 1.1.1.1 dev eth0.20
post-up ip route add 192.168.200.0/24 via 1.1.1.1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> GW network configuration added."

dnsmasq="
no-resolv
expand-hosts
domain=local

interface=eth0.30
dhcp-option=3,192.168.100.254  #server DHCP - IP della sua VLAN
dhcp-option=6,192.168.100.254  #server DNS
dhcp-option=15,local

# syntax -> dhcp-range=<start_IP>,<end_IP>,<netmask>,<lease_time>
dhcp-range=192.168.100.1,192.168.100.253,255.255.255.0,12h
"

echo "$dnsmasq" >> /etc/dnsmasq.conf
echo "<M> dnsmasq configuration added."

echo "<M> Eseguo comandi di configurazione"
systemctl enable dnsmasq
if [ $? -eq 0 ]; then
    systemctl restart dnsmasq
    if [ $? -eq 0 ]; then
        echo "<M> dnsmasq restarted successfully."
    else
        echo "<M> Failed to restart dnsmasq."
        echo "<M> Check the dnsmasq logs for more information."
        echo "<M> Exec -> dnsmasq --test or journalctl -xe"
        exit 1
    fi
    echo "<M> Verifica la configurazione di dnsmasq:"
    dnsmasq --test
    if [ $? -eq 0 ]; then
        echo "<M> dnsmasq configuration is valid."
    else
        echo "<M> dnsmasq configuration is invalid."
        exit 1
    fi
else
    echo "<M> Failed to enable dnsmasq."
    exit 1
fi

echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "<M> Ip configurato correttamente."

sysctl -p /etc/sysctl.conf
if [ $? -eq 0 ]; then
    echo "<M> sysctl configuration reloaded successfully."
else
    echo "<M> Failed to reload sysctl configuration."
    exit 1
fi

```

> **⚠️🚨** Ricordiamo di tirare su tutte le interfacce con `ifup -a` (prima il `GW`)

## GWC SNAT

> ‼️ Configurazioni da lanciare in `GWC`

```bash
#!/bin/bash

# Prima di tutto faccio il flush
iptables -F # cancello tutte le regole esistenti
iptables -t nat -F # cancello tutte le regole NAT esistenti
iptables -X # cancello tutte le catene personalizzate

# Configuro il SNAT
# -t nat -> significa "table nat", ovvero la tabella NAT
# -A POSTROUTING -> aggiunge una regola nella catena POSTROUTING
# -o <INTERFACE> -> specifica l'interfaccia di uscita
# -j MASQUERADE -> applica la regola di masquerading

iptables -t nat -A POSTROUTING -o eth0.20 -j MASQUERADE

if [ $? -eq 0 ]; then
    echo "<M> SNAT configuration added."
else
    echo "<M> Failed to add SNAT configuration."
    exit 1
fi
```

### GWS

```bash
#!/bin/bash

interfaces="
auto eth0.10
iface eth0.10 inet static
        address 192.168.200.254
        netmask 255.255.255.0

auto eth0.20
iface eth0.20 inet static
        address 1.1.1.1
        netmask 255.255.255.255

post-up ip route add 2.2.2.2 dev eth0.20
post-up ip route add 192.168.100.0/24 via 2.2.2.2
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> GW network configuration added."

echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "<M> Ip configurato correttamente."

sysctl -p /etc/sysctl.conf
if [ $? -eq 0 ]; then
    echo "<M> sysctl configuration reloaded successfully."
else
    echo "<M> Failed to reload sysctl configuration."
    exit 1
fi

```

> **⚠️🚨** Ricordiamo di tirare su tutte le interfacce con `ifup -a` (prima il `GW`)

## GWS DNAT

> ‼️ Configurazioni da lanciare in `GWS`

```bash
#!/bin/bash

# Interfacce
PUB_IF=eth0.20   # lato client/GWC
SRV_IF=eth0.10   # lato server
WEBSRV=192.168.200.1
MAILSRV=192.168.200.2

# Flush
iptables -F
iptables -t nat -F
iptables -X

# Policy default
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT   # consigliato: lasciare GWS parlare col mondo

# ICMP ovunque
iptables -A INPUT   -p icmp -j ACCEPT
iptables -A OUTPUT  -p icmp -j ACCEPT
iptables -A FORWARD -p icmp -j ACCEPT

# Consenti traffico già stabilito/relativo
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# DNAT WebSrv (HTTP)
iptables -t nat -A PREROUTING -i $PUB_IF -p tcp --dport 80 -j DNAT --to-destination $WEBSRV:80
iptables -A FORWARD -i $PUB_IF -o $SRV_IF -d $WEBSRV -p tcp --dport 80 -j ACCEPT

# DNAT MailSrv (SMTP)
iptables -t nat -A PREROUTING -i $PUB_IF -p tcp --dport 25 -j DNAT --to-destination $MAILSRV:25
iptables -A FORWARD -i $PUB_IF -o $SRV_IF -d $MAILSRV -p tcp --dport 25 -j ACCEPT

echo "<M> DNAT + firewall configurato su GWS."
```

## 🔹 Tabella di test

| #  | Descrizione                                                     | Nodo di partenza | Comando                                    | Risultato atteso                              |
| -- | --------------------------------------------------------------- | ---------------- | ------------------------------------------ | --------------------------------------------- |
| 1  | Connettività Client → GWC                                       | Client           | `ping -c 3 192.168.100.1`                  | Risponde (ICMP OK)                            |
| 2  | Connettività Client → GWS (indirizzo sulla rete esterna di GWS) | Client           | `ping -c 3 <IP_pubblico_GWS>`              | Risponde (ICMP OK)                            |
| 3  | DHCP: il Client riceve IP                                       | Client           | `dhclient eth0` oppure `ip addr show eth0` | Ottiene IP in `192.168.100.0/24`, gateway GWC |
| 4  | SNAT da Client verso GWS                                        | Client           | `ping -c 3 <IP_pubblico_GWS>`              | Risponde, sorgente tradotta da GWC            |
| 5  | DNAT HTTP Client → WebSrv                                       | Client           | `nc -vz <IP_pubblico_GWS> 80`              | Connessione riuscita verso WebSrv             |
| 6  | DNAT SMTP Client → MailSrv                                      | Client           | `nc -vz <IP_pubblico_GWS> 25`              | Connessione riuscita verso MailSrv            |
| 7  | Firewall WebSrv (solo HTTP + ICMP)                              | Client           | `nc -vz <IP_privato_WebSrv> 22`            | Connessione **rifiutata** (blocco firewall)   |
| 8  | Firewall MailSrv (solo SMTP + ICMP)                             | Client           | `nc -vz <IP_privato_MailSrv> 80`           | Connessione **rifiutata** (blocco firewall)   |
| 9  | ICMP WebSrv                                                     | Client           | `ping -c 3 <IP_privato_WebSrv>`            | Risponde                                      |
| 10 | ICMP MailSrv                                                    | Client           | `ping -c 3 <IP_privato_MailSrv>`           | Risponde                                      |
| 11 | VLAN isolation tra reti diverse                                 | Client           | `arping -c 3 <IP_privato_WebSrv>`          | Nessuna risposta (ARP bloccato da VLAN)       |
| 12 | VLAN isolation tra reti diverse                                 | WebSrv           | `arping -c 3 <IP_privato_Client>`          | Nessuna risposta                              |
| 13 | Test UDP non consentito (es. su HTTP)                           | Client           | `nc -vu <IP_pubblico_GWS> 80`              | Nessuna risposta (blocco firewall UDP)        |
| 14 | Test UDP non consentito (SMTP)                                  | Client           | `nc -vu <IP_pubblico_GWS> 25`              | Nessuna risposta (blocco firewall UDP)        |

