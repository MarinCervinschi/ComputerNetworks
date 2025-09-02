## Initial Configuration

Guarda il [readme.md](./readme.md)

# LAN Configuration

Dentro lo SWITCH S1

```bash
# Creazione VLAN
# syntax: vlan/create <VLAN_ID>
vlan/create 10
vlan/create 20
vlan/create 30

# access link
# syntax: port/setvlan <port_id> <vlan_id>
port/setvlan 1 20 # Cli1
port/setvlan 2 20 # Cli2
port/setvlan 3 30 # SrvInt
port/setvlan 4 10 # SrvExt


# trunk link
# syntax: vlan/addport <vlan_id> <port_id>
vlan/addport 10 5 # GWC
vlan/addport 20 5 # GWC
vlan/addport 30 5 # GWC
```

> **⚠️🚨** Assicurati di collegare i CAVI alle PORTE giuste in fase di configurazione.

# Interface Configuration

## LAN 20

### Cli1 -> PORT 1

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname Cli1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Cli1 network configuration added."
```

### Cli2 -> PORT 2

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname Cli2
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Cli2 network configuration added."
```

## LAN 30

### SrvInt -> PORT 3

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 192.168.30.1
        netmask 255.255.255.0
        gateway 192.168.30.254
        hostname SrvInt
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> SrvInt network configuration added."
```

## LAN 10

### SrvExt -> PORT 4

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 155.185.48.1
        netmask 255.255.255.0
        gateway 155.185.48.254
        hostname SrvExt
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> SrvExt network configuration added."
```

## R1 (GW) -> PORT 5

```bash
#!/bin/bash

interfaces="
auto eth0.20
iface eth0.20 inet static
        address 192.168.20.254
        netmask 255.255.255.0

auto eth0.30
iface eth0.30 inet static
        address 192.168.30.254
        netmask 255.255.255.0

auto eth0.10
iface eth0.10 inet static
        address 155.185.48.254
        netmask 255.255.255.0
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> R1 network configuration added."

dnsmasq="
no-resolv
expand-hosts
domain=local

interface=eth0.20
dhcp-option=3,192.168.20.254  #server DHCP - IP della sua VLAN
dhcp-option=6,192.168.20.254  #server DNS

# Definisci il range DHCP
# syntax -> dhcp-range=<start_IP>,<end_IP>,<netmask>,<lease_time>
dhcp-range=192.168.20.1,192.168.20.253,255.255.255.0,12h
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

### Firewall e NAT

> ‼️ Configurazioni da lanciare in `GW`

```bash
#!/bin/bash

LAN_10_IF="eth0.10"
LAN_20_IF="eth0.20"

LAN_20_NET="192.168.20.0/24"
LAN_30_NET="192.168.30.0/24"

SRV_INT_IP="192.168.30.1"

#-------------------------------------------
# SNAT per ogni rete con indirizzi privati
#-------------------------------------------
iptables -t nat -A POSTROUTING -o $LAN_10_IF -s $LAN_20_NET -j MASQUERADE
iptables -t nat -A POSTROUTING -o $LAN_10_IF -s $LAN_30_NET -j MASQUERADE

#------------------------------------------------
# DNAT da tutte le reti verso SrvInt
#------------------------------------------------
iptables -t nat -A PREROUTING -p tcp --dport 8000 -i $LAN_10_IF -j DNAT --to-destination $SRV_INT_IP:80
iptables -t nat -A PREROUTING -p tcp --dport 8000 -i $LAN_20_IF -j DNAT --to-destination $SRV_INT_IP:80

echo "<M> SNAT + DNAT configurato su R1."
```
