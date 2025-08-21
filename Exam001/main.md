## Initial Configuration

Dati dal testo

### LAN

- `NET id`: `10.0.1.0/25`
- `VLAN id`: `10`
- `H1`: `10.0.1.1` -> DHCP (calcola pure il MAC)
- `H2`: DHCP

*per calcolare il MAC
```bash
ip addr show eth0
```

### DMZ

- `NET id`: `10.0.1.128/25`
- `VLAN id`: `20`
- `Srv`: `10.0.1.129`

GW ha due interfacce di rete:

- eth0, connessa a sw1, su cui insistono le interfacce di rete virtuali attestate su LAN e DMZ. Queste
  sono configurate staticamente con **l’ultimo** indirizzo IP della rispettiva rete.
- eth1, connessa a sw2, con indirizzo IP 5.4.3.2/32

### GW

Steps per l'ultimo:

```bash
ipcalc 10.0.1.0/25
```

Prendiamo `HostMax` -> `10.0.1.126`

- `eth0.10`: `10.0.1.126`

```bash
ipcalc 10.0.1.128/25
```

Prendiamo `HostMax` -> `10.0.1.254`.

- `eth0.20`: `10.0.1.254`

ETH1 fornita dal testo:

- `eth1`: `5.4.3.2/32`

### Ext

Fornito dal testo:

- `eth0`: `2.3.4.5/32`

## Configurazione VLAN
Dentro lo SWITCH S1

```test
vlan/create 10
vlan/create 20

port/setvlan 1 10
port/setvlan 2 10
port/setvlan 3 20

vlan/addport 10 4
vlan/addport 20 4
```

## Configurazione ip

### H1

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname H1
"

echo "$interfaces" >> /etc/network/interfaces

if [ $? -eq 0 ]; then
    echo "H1 network configuration added."
else
    echo "Failed to add H1 network configuration."
fi
```

### H2

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname H2
"

echo "$interfaces" >> /etc/network/interfaces

if [ $? -eq 0 ]; then
    echo "H2 network configuration added."
else
    echo "Failed to add H2 network configuration."
fi
```

### Srv

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 10.0.1.129
        netmask 255.255.255.128
        gateway 10.0.1.254
"

echo "$interfaces" >> /etc/network/interfaces

if [ $? -eq 0 ]; then
    echo "Srv network configuration added."
else
    echo "Failed to add Srv network configuration."
fi
```

### Ext

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 2.3.4.5
        netmask 255.255.255.255
        gateway 5.4.3.2/32
"

echo "$interfaces" >> /etc/network/interfaces

if [ $? -eq 0 ]; then
    echo "Ext network configuration added."
else
    echo "Failed to add Ext network configuration."
fi
```

### GW

```bash
#!/bin/bash

interfaces="
auto eth0.10
iface eth0.10 inet static
        address 10.0.1.126
        netmask 255.255.255.128

auto eth0.20
iface eth0.20 inet static
        address 10.0.1.254
        netmask 255.255.255.128

auto eth1
iface eth1 inet static
        address 5.4.3.2
        netmask 255.255.255.255

post-up ip route add 2.3.4.5/32 via 5.4.3.2/32 dev eth1
"

echo "$interfaces" >> /etc/network/interfaces

if [ $? -eq 0 ]; then
    echo "GW network configuration added."
else
    echo "Failed to add GW network configuration."
fi

dnsmasq="
no-resolv
expand-hosts
domain=local

interface=eth0.10
dhcp-option=3,10.0.1.126  #server DHCP - IP della sua VLAN
dhcp-option=6,10.0.1.126  #server DNS
dhcp-option=15,local

#devo assegnare a H1 sempre lo stesso indirizzo (ip addr show eth0 - MAC)
dhcp-host=02:04:06:11:11:11,H1,10.0.1.1

#Trovo il min/max con ipcalc
dhcp-range=10.0.1.2,10.0.1.125,255.255.255.128,12h
"

echo "$dnsmasq" >> /etc/dnsmasq.conf

if [ $? -eq 0 ]; then
    echo "dnsmasq configuration added."
else
    echo "Failed to add dnsmasq configuration."
fi

echo "Eseguo comandi di configurazione"
systemctl enable dnsmasq
systemctl restart dnsmasq

if [ $? -eq 0 ]; then
    echo "dnsmasq restarted successfully."
else
    echo "Failed to restart dnsmasq."
    echo "Verifica la configurazione di dnsmasq:"
    dnsmasq --test
fi

echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "Ip configurato correttamente."

sysctl -p /etc/sysctl.conf

```

>**⚠️🚨** Ricordiamo di tirare su tutte le interfacce con `ifup -a`

### Testare FLOW

| Test | Comando | Result |
| --- | --- | --- |
| `H1 → H2` ping | `ping H2` | Successo |
| `H2 → H1` ping | `ping H1` | Successo |
| `H1 → Srv` ping (passa da GW) | `ping 10.0.1.129` | Successo |
| `H1 → Srv` arping  | `arping 10.0.1.129` | Fallimento, non sono nella stessa VLAN |
| `H1 → GW` ping | `ping 10.0.1.126` | Successo |
| `H1 → GW` ping | `ping 10.0.1.254` | Successo |
| `H1 → Ext` ping | `ping 2.3.4.5` | Successo |