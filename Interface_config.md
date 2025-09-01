# LAN Configuration

Dentro lo SWITCH SX

```bash
# Creazione VLAN
# syntax: vlan/create <VLAN_ID>
vlan/create X1
vlan/create X2

# access link
# syntax: port/setvlan <port_id> <vlan_id>
port/setvlan 1 X1 # HOSTNAME 1
port/setvlan 2 X2 # HOSTNAME 2

# trunk link
# syntax: vlan/addport <vlan_id> <port_id>
vlan/addport X1 4 # GWC
vlan/addport X2 4 # GWC
vlan/addport X1 5 # GWS
vlan/addport X2 5 # GWS
```

>**⚠️🚨** Assicurati di collegare i CAVI alle PORTE giuste in fase di configurazione.

# Interface Configuration

## NETMASKS

| CIDR | Hosts per Subnet | Netmask         |
| ---- | ---------------- | --------------- |
| /24  | 256              | 255.255.255.0   |
| /25  | 128              | 255.255.255.128 |
| /32  | 1                | 255.255.255.255 |

### DHCP_INTERFACE

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname DHCP_INTERFACE
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> DHCP_INTERFACE network configuration added."
```

### STATIC_INTERFACE

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address X.X.X.X
        netmask 255.255.255.X
        gateway X.X.X.X
        hostname STATIC_INTERFACE
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> STATIC_INTERFACE network configuration added."
```

### DNSMASQ CONFIG -> on GW

```bash
dnsmasq="
no-resolv
expand-hosts
domain=local

interface=ETH0.X
dhcp-option=3,X.X.X.X  #server DHCP - IP della sua VLAN
dhcp-option=6,X.X.X.X  #server DNS

# Assegna indirizzi statici anche con DHCP
# syntax -> dhcp-host=<MAC_address>,<hostname>,<IP_address>
dhcp-host=MAC,YOUR_HOST,X.X.X.X

# Definisci il range DHCP
# syntax -> dhcp-range=<start_IP>,<end_IP>,<netmask>,<lease_time>
dhcp-range=X.X.X.X,X.X.X.X,255.255.255.X,12h
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
```

### IP_FORWARD + ENABLE ROUTING

```bash
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
