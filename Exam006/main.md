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

# Interfacce
GW_LAN_42_IF=eth0.42
GW_LAN_43_IF=eth0.43
GW_GW_EXT_IF=eth1

# IP
SRV_IP=10.42.0.129
VLAN_42_IP=10.42.0.0/25
H1_IP=10.42.0.1

# Flush delle regole esistenti
iptables -F
iptables -t nat -F
iptables -X

# Policy di default (negazione implicita)
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# 8. Consentire traffico ICMP ovunque
iptables -A INPUT -p icmp -j ACCEPT
iptables -A OUTPUT -p icmp -j ACCEPT
iptables -A FORWARD -p icmp -j ACCEPT

# 2. DHCP per VLAN 42 (corretto sport/dport)
iptables -A INPUT -i $GW_LAN_42_IF -p udp --dport 67 -j ACCEPT
iptables -A OUTPUT -o $GW_LAN_42_IF -p udp --sport 67 -j ACCEPT

# 3. NAT per l'accesso a Internet
iptables -t nat -A POSTROUTING -o $GW_EXT_IF -j MASQUERADE

# 4. HTTP dalla sottorete 10.42.0.0/25 verso SRV
iptables -A FORWARD -s $VLAN_42_IP -d $SRV_IP -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -d $VLAN_42_IP -s $SRV_IP -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT

# 5. SSH da H1 verso GW
iptables -A INPUT -i $GW_LAN_42_IF -s $H1_IP -p tcp --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -o $GW_LAN_42_IF -d $H1_IP -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT

# 6. Accesso a server Web esterno dalla LAN
iptables -A FORWARD -i $GW_LAN_42_IF -o $GW_EXT_IF -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $GW_EXT_IF -o $GW_LAN_42_IF -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT

# 7. Accesso da EXT al server Web su SRV (DNAT)
iptables -t nat -A PREROUTING -i $GW_EXT_IF -p tcp --dport 80 -j DNAT --to $SRV_IP
iptables -A FORWARD -i $GW_EXT_IF -o $GW_LAN_43_IF -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $GW_LAN_43_IF -o $GW_EXT_IF -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT

# Regole aggiuntive per traffico generico
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

echo "<M> DNAT + firewall configurato su GW."
```
