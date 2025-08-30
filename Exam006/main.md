## Initial Configuration

Guarda il [PDF](./esame_mar_20250616.pdf)

## Configurazione VLAN

Dentro lo SWITCH S1

```bash
vlan/create 42
vlan/create 43

# access link
port/setvlan 1 42 # H1
port/setvlan 2 42 # H2
port/setvlan 3 43 # SRV

# trunk link
vlan/addport 42 4 # GW
vlan/addport 43 4 # GW
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
echo "<M> H1 network configuration added."
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
echo "<M> H2 network configuration added."
```

### SRV

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 10.42.0.129
        netmask 255.255.255.128
        gateway 10.42.0.254
        hostname SRV
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> SRV network configuration added."
```

### EXT

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 2.20.20.20
        netmask 255.255.255.255
        gateway 2.2.2.42
        hostname EXT
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> EXT network configuration added."
```

### GW

```bash
#!/bin/bash

interfaces="
auto eth0.42
iface eth0.42 inet static
        address 10.42.0.126
        netmask 255.255.255.128

auto eth0.43
iface eth0.43 inet static
        address 10.42.0.254
        netmask 255.255.255.128

auto eth1
iface eth1 inet static
        address 2.2.2.42
        netmask 255.255.255.255

post-up ip route add 2.20.20.20/32 dev eth1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> GW network configuration added."

dnsmasq="
no-resolv
expand-hosts
domain=local

interface=eth0.42
dhcp-option=3,10.42.0.126  #server DHCP - IP della sua VLAN
dhcp-option=6,10.42.0.126  #server DNS

#devo assegnare a H1 e H2 sempre lo stesso indirizzo (ip addr show eth0 - MAC)
dhcp-host=02:04:06:11:11:11,H1,10.42.0.1
dhcp-host=02:04:06:22:22:22,H2,10.42.0.2

# syntax -> dhcp-range=<start_IP>,<end_IP>,<netmask>,<lease_time>
dhcp-range=10.42.0.3,10.42.0.125,255.255.255.128,12h
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

> **⚠️🚨** RICORDA DI SOSTITUIRE I MAC GIUSTI  
> **⚠️🚨** Ricordiamo di tirare su tutte le interfacce con `ifup -a` (prima il `GW`)

## Firewall e NAT

> ‼️ Configurazioni da lanciare in `GW`

```bash
#!/bin/bash

# Pulizia regole esistenti
iptables -F
iptables -t nat -F
iptables -X

# Policy di default (blocco totale)
iptables -t filter -P INPUT DROP
iptables -t filter -P OUTPUT DROP
iptables -t filter -P FORWARD DROP

#------------------------------------------------
# DHCP LAN
#------------------------------------------------
iptables -A INPUT  -i eth0.42 -p udp --sport 67 --dport 68 -j ACCEPT
iptables -A OUTPUT -o eth0.42 -p udp --sport 68 --dport 67 -j ACCEPT
#------------------------------------------------
# DNS LAN
#------------------------------------------------
iptables -A INPUT  -i eth0.42 -p udp -s 10.42.0.0/25 --dport 53 -j ACCEPT
iptables -A OUTPUT -o eth0.42 -p udp -d 10.42.0.0/25 --sport 53 -j ACCEPT
#-------------------------------------------
# NAT: Masquerading per traffico in uscita
#-------------------------------------------
iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
#---------------------------------------------
# H1, H2 -> SRV
#---------------------------------------------
iptables -A FORWARD -i eth0.42 -o eth0.43 -p tcp -s 10.42.0.0/25 -d 10.42.0.129 --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0.43 -o eth0.42 -p tcp -s 10.42.0.129 -d 10.42.0.0/25 --sport 80 -m state --state ESTABLISHED -j ACCEPT
#------------------------------------------------
# H1, H2 -> EXT HTTP (porta 80)
#------------------------------------------------
iptables -A FORWARD -i eth0.42 -o eth1 -p tcp -s 10.42.0.0/25 -d 2.20.20.20 --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0.42 -p tcp -s 2.20.20.20 -d 10.42.0.0/25 --sport 80 -m state --state ESTABLISHED -j ACCEPT
#------------------------------------------------
# SRV -> EXT HTTP (porta 80)
#------------------------------------------------
iptables -A FORWARD -i eth0.43 -o eth1 -p tcp -s 10.42.0.129 -d 2.20.20.20 --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0.43 -p tcp -s 2.20.20.20 -d 10.42.0.129 --sport 80 -m state --state ESTABLISHED -j ACCEPT
#------------------------------------------------
# EXT -> SRV (porta 80)
#------------------------------------------------
iptables -t nat -A PREROUTING -p tcp --dport 80 -i eth1 -s 2.20.20.20 -d 2.2.2.42 -j DNAT --to-destination 10.42.0.129
iptables -A FORWARD -i eth1 -o eth0.43 -p tcp -s 2.20.20.20 -d 10.42.0.129 --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0.43 -o eth1 -p tcp -s 10.42.0.129 -d 2.20.20.20 --sport 80 -m state --state ESTABLISHED -j ACCEPT
#------------------------------------------------
#ICMP
#------------------------------------------------
iptables -t filter -A INPUT -p icmp -j ACCEPT
iptables -t filter -A FORWARD -p icmp -j ACCEPT
iptables -t filter -A OUTPUT -p icmp -j ACCEPT
#------------------------------------------------
# SSH da H1 → GW
#------------------------------------------------
iptables -A INPUT  -i eth0.42 -p tcp -s 10.42.0.1 --dport 22 -m state --state NEW -j ACCEPT
iptables -A OUTPUT -o eth0.42 -p tcp -d 10.42.0.1 --sport 22 -m state --state ESTABLISHED -j ACCEPT

echo "<M> DNAT + firewall configurato su GW."
```
