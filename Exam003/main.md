# Configurazione iniziale

Guardare [readme.md](readme.md)

## Configurazione VLAN

Dentro lo SWITCH S1

```bash
vlan/create 10
vlan/create 20

# access link
port/setvlan 1 10
port/setvlan 2 10
port/setvlan 3 20
port/setvlan 4 20

# trunk link
vlan/addport 10 5
vlan/addport 20 5
```

## Configurazione IP

### H1

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.1.2
        netmask 255.255.255.0
        gateway 192.168.1.254
        hostname H1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H1 network configuration added."

```

### Srv1

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.1.1
        netmask 255.255.255.0
        gateway 192.168.1.254
        hostname Srv1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Srv1 network configuration added."
```

### H2

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.2.2
        netmask 255.255.255.0
        gateway 192.168.2.254
        hostname H2
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H2 network configuration added."

```

### Srv2

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.2.1
        netmask 255.255.255.0
        gateway 192.168.2.254
        hostname Srv2
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Srv2 network configuration added."
```

### Ext

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 2.2.2.2
        netmask 255.255.255.255
        gateway 1.1.1.1
        hostname Ext
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Ext network configuration added."
```

### GW

```bash
#!/bin/bash

interfaces="
auto eth0.10
iface eth0.10 inet static
        address 192.168.1.254
        netmask 255.255.255.0

auto eth0.20
iface eth0.20 inet static
        address 192.168.2.254
        netmask 255.255.255.0

auto eth1
iface eth1 inet static
        address 1.1.1.1
        netmask 255.255.255.255

post-up ip route add 2.2.2.2 dev eth1
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

> **⚠️🚨** Ricordiamo di tirare su tutte le interfacce con `ifup -a` (prima in `GW`)

## SNAT e DNAT

> ‼️ Configurazioni da lanciare in `GW`

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

iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
if [ $? -eq 0 ]; then
    echo "<M> SNAT configuration added."
else
    echo "<M> Failed to add SNAT configuration."
    exit 1
fi


# DNAT
# -t nat -> significa "table nat", ovvero la tabella NAT
# -A PREROUTING -> aggiunge una regola nella catena PREROUTING
# -i <INTERFACE> -> specifica l'interfaccia di ingresso
# -p <PROTOCOL> -> specifica il protocollo (tcp, udp, ecc.)
# --dport <PORT> -> specifica la porta di destinazione
# -s <SOURCE_IP> -> specifica l'indirizzo IP sorgente
# -d <DESTINATION_IP> -> specifica l'indirizzo IP di destinazione
# -j DNAT -> applica la regola di DNAT
# --to-destination <IP>:<PORT> -> specifica l'indirizzo IP e la porta di destinazione

iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j DNAT --to-destination 192.168.1.1:80
iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 8000 -j DNAT --to-destination 192.168.2.1:80

if [ $? -eq 0 ]; then
    echo "<M> DNAT configuration added."
else
    echo "<M> Failed to add DNAT configuration."
    exit 1
fi
```
