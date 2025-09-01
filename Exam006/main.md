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
        hostname EXT
        post-up ip route add 2.2.2.42/32 dev eth0
        post-up ip route add default via 2.2.2.42 dev eth0
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

## Regole di NAT e politiche di filtraggio sul firewall

1. Utilizzare una **policy di negazione implicita** per tutti i pacchetti in transito, ingresso e uscita da GW
2. Consentire flussi di comunicazione UDP per il corretto funzionamento del protocollo DHCP tra gli host della **VLAN 42** e **GW**
3. Consentire a tutte le **macchine della rete interna** di accedere a macchine in **Internet** condividendo l’IP pubblico associato all’interfaccia eth1 di GW
4. Consentire **connessioni HTTP** generate dalla **sottorete 10.42.0.0/25** verso il server web in esecuzione su **SRV** (testare con nc)
5. Consentire **connessioni SSH** generate dalla macchina **H1** verso **GW**
6. Consentire alle macchine della **rete LAN** di contattare un **server Web** in esecuzione su **EXT** (testare con nc)
7. **EXT** possa contattare un **server Web** in esecuzione su **SRV** utilizzando l’IP pubblico associato all’interfaccia eth1 di GW (testare con nc)
8. Consentire il **passaggio di traffico ICMP** tra tutti i nodi.

### Firewall e NAT

> ‼️ Configurazioni da lanciare in `GW`

```bash
#!/bin/bash

DHCP_IF="eth0.42"
GW_PUB_IF="eth1"
SRV_IF="eth0.43"
SRV_IP="10.42.0.129"
H1_IP="10.42.0.1"
DHCP_LAN_NET="10.42.0.0/25"
SRV_LAN_NET="10.42.0.128/25"
EXT_IP="2.20.20.20"
GW_IP="2.2.2.42"

#------------------------------------------------
# 1. Policy di default (blocco totale)
#------------------------------------------------
iptables -t filter -P INPUT DROP
iptables -t filter -P OUTPUT DROP
iptables -t filter -P FORWARD DROP

#------------------------------------------------
# 2. DHCP LAN
#------------------------------------------------
iptables -A INPUT  -i $DHCP_IF -p udp --sport 68 --dport 67 -j ACCEPT
iptables -A OUTPUT -o $DHCP_IF -p udp --sport 67 --dport 68 -j ACCEPT

#-------------------------------------------
# 3. NAT: Masquerading per traffico in uscita (TUTTE le reti interne)
#-------------------------------------------
iptables -t nat -A POSTROUTING -o $GW_PUB_IF -s $DHCP_LAN_NET -j MASQUERADE
iptables -t nat -A POSTROUTING -o $GW_PUB_IF -s $SRV_LAN_NET -j MASQUERADE

#---------------------------------------------
# 4. H1, H2 (sottorete 10.42.0.0/25) -> SRV
#---------------------------------------------
iptables -A FORWARD -p tcp --dport 80 -i $DHCP_IF -o $SRV_IF -s $DHCP_LAN_NET -d $SRV_IP -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -p tcp --sport 80 -i $SRV_IF -o $DHCP_IF -s $SRV_IP -d $DHCP_LAN_NET -m state --state ESTABLISHED -j ACCEPT

#------------------------------------------------
# 5. SSH da H1 → GW
#------------------------------------------------
iptables -A INPUT  -p tcp --dport 22 -i $DHCP_IF -s $H1_IP  -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -p tcp --sport 22 -o $DHCP_IF -d $H1_IP  -m state --state ESTABLISHED -j ACCEPT

#------------------------------------------------
# 6. Reti LAN (DHCP+SRV) -> EXT HTTP (porta 80)
#------------------------------------------------
iptables -A FORWARD -p tcp --dport 80 -i $DHCP_IF -o $GW_PUB_IF -s $DHCP_LAN_NET -d $EXT_IP -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -p tcp --sport 80 -i $GW_PUB_IF -o $DHCP_IF -s $EXT_IP -d $DHCP_LAN_NET -m state --state ESTABLISHED -j ACCEPT

iptables -A FORWARD -p tcp --dport 80 -i $SRV_IF -o $GW_PUB_IF -s $SRV_LAN_NET -d $EXT_IP -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -p tcp --sport 80 -i $GW_PUB_IF -o $SRV_IF -s $EXT_IP -d $SRV_LAN_NET -m state --state ESTABLISHED -j ACCEPT

#------------------------------------------------
# 7. EXT -> SRV (via IP pubblico di GW)
#------------------------------------------------
iptables -t nat -A PREROUTING -p tcp --dport 80 -i $GW_PUB_IF -s $EXT_IP -d $GW_IP -j DNAT --to-destination $SRV_IP
iptables -A FORWARD -p tcp --dport 80 -i $GW_PUB_IF -o $SRV_IF -s $EXT_IP -d $SRV_IP -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A FORWARD -p tcp --sport 80 -i $SRV_IF -o $GW_PUB_IF -s $SRV_IP -d $EXT_IP -m state --state ESTABLISHED -j ACCEPT

#------------------------------------------------
# 8. ICMP
#------------------------------------------------
iptables -A INPUT   -p icmp -j ACCEPT
iptables -A FORWARD -p icmp -j ACCEPT
iptables -A OUTPUT  -p icmp -j ACCEPT

echo "<M> DNAT + firewall configurato su GW."
```
