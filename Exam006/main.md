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
        gateway 2.2.2.2
        hostname EXT
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> EXT network configuration added."
```

### GWC

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
        address 2.2.2.2
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
dhcp-option=3,10.42.0.0  #server DHCP - IP della sua VLAN
dhcp-option=6,10.42.0.0  #server DNS

#devo assegnare a H1 e H2 sempre lo stesso indirizzo (ip addr show eth0 - MAC)
dhcp-host=02:04:06:11:11:11,H1,10.42.0.1
dhcp-host=02:04:06:22:22:22,H2,10.42.0.2
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

> **⚠️🚨** Ricordiamo di tirare su tutte le interfacce con `ifup -a` (prima il `GW`)

## GWS DNAT

> ‼️ Configurazioni da lanciare in `GWS`

```bash
#!/bin/bash

# Interfacce
PUB_IF=eth0  # lato VLAN
DHCP_LAN=eth0.42
LAN_SRV=eth0.43
EXT_IF=eth1   # lato EXT
EXT=2.20.20.20
SRV_IP=10.42.0.129
VLAN_1_IP=10.42.0.0/25
H1_IP=10.42.0.1
H2_IP=10.42.0.2

# Flush
iptables -F
iptables -t nat -F
iptables -X

# Policy default
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# ICMP ovunque
iptables -A INPUT   -p icmp -j ACCEPT
iptables -A OUTPUT  -p icmp -j ACCEPT
iptables -A FORWARD -p icmp -j ACCEPT


# Configuro il SNAT
# -t nat -> significa "table nat", ovvero la tabella NAT
# -A POSTROUTING -> aggiunge una regola nella catena POSTROUTING
# -o <INTERFACE> -> specifica l'interfaccia di uscita
# -j MASQUERADE -> applica la regola di masquerading

iptables -t nat -A POSTROUTING -o $EXT_IF -j MASQUERADE

iptables -A INPUT -i $DHCP_LAN -p udp --sport 67 --dport 68 -j ACCEPT
iptables -A OUTPUT -o $DHCP_LAN -p udp --sport 68 --dport 67 -j ACCEPT


iptables -t filter -A FORWARD -i $DHCP_LAN -o $LAN_SRV -s $VLAN_1_IP -d $SRV_IP -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A FORWARD -i $LAN_SRV -o $DHCP_LAN -s $SRV_IP -d $VLAN_1_IP -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT

# SSH
# Consentire connessioni SSH in ingresso dalla LAN
iptables -A INPUT -i $DHCP_LAN -p tcp -s $H1_IP --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT

# Consentire risposte SSH in uscita verso il client
iptables -A OUTPUT -o $DHCP_LAN -p tcp -d $H1_IP --sport 22 -m state --state ESTABLISHED -j ACCEPT


# Lan to EXT
iptables -t filter -A FORWARD -i $DHCP_LAN -o $EXT_IF -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A FORWARD -i $EXT_IF -o $DHCP_LAN -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT

# From EXT to SRV
# DNAT
iptables -t nat -A PREROUTING -i $EXT_IF -p tcp --dport 80 -j DNAT --to-destination $SRV_IP:80

iptables -t filter -A FORWARD -i $EXT_IF -o $LAN_SRV -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A FORWARD -o $EXT_IF -i $LAN_SRV -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT


echo "<M> DNAT + firewall configurato su GWS."
```
