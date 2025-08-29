# Configurazione iniziale

Guardare [PDF](./Marionnet_01072020.pdf)

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
        address 192.168.10.1
        netmask 255.255.255.0
        gateway 192.168.10.254
        hostname H1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H1 network configuration added."

```

### H2

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.10.2
        netmask 255.255.255.0
        gateway 192.168.10.254
        hostname H2
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H2 network configuration added."
```

### H3

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.20.1
        netmask 255.255.255.0
        gateway 192.168.20.254
        hostname H3
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H3 network configuration added."

```

### H4

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.20.2
        netmask 255.255.255.0
        gateway 192.168.20.254
        hostname H4
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H4 network configuration added."
```

### GW

```bash
#!/bin/bash

interfaces="
auto eth0.10
iface eth0.10 inet static
        address 192.168.10.254
        netmask 255.255.255.0

auto eth0.20
iface eth0.20 inet static
        address 192.168.20.254
        netmask 255.255.255.0
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


## 🔹 Tabella di test

| Test                                 | Host di partenza | Comando                    | Risultato atteso                                     |
| ------------------------------------ | ---------------- | -------------------------- | ---------------------------------------------------- |
| Connettività H1 ↔ H2 (stessa VLAN)   | H1               | `ping -c 3 192.168.10.2`   | Risponde, RTT basso                                  |
| ARP check H1 ↔ H2                    | H1               | `arping -c 3 192.168.10.2` | Risposta diretta (MAC di H2)                         |
| Connettività H3 ↔ H4 (stessa VLAN)   | H3               | `ping -c 3 192.168.20.2`   | Risponde, RTT basso                                  |
| ARP check H3 ↔ H4                    | H3               | `arping -c 3 192.168.20.2` | Risposta diretta (MAC di H4)                         |
| Isolamento tra sottoreti (ARP)       | H1               | `arping -c 3 192.168.20.1` | **Nessuna risposta** (ARP bloccato da VLAN)          |
| Ping cross-subnet H1 ↔ H3 (via GW)   | H1               | `ping -c 3 192.168.20.1`   | Risponde tramite GW                                  |
| Verifica routing GW                  | GW               | `ip route`                 | Mostra route verso 192.168.10.0/24 e 192.168.20.0/24 |
