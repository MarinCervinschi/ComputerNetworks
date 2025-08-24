## Initial Configuration

Guarda il [PDF](./Marionnet_12012020.pdf)

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

### H3

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet dhcp
        hostname H3
        hwaddress 02:04:06:11:22:33
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> H3 network configuration added."
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
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> Ext network configuration added."
```

### GW

```bash
#!/bin/bash

interfaces="
auto eth0
iface eth0 inet static
        address 10.0.1.254
        netmask 255.255.255.0

auto eth1
iface eth1 inet static
        address 1.1.1.1
        netmask 255.255.255.255

post-up ip route add 2.2.2.2 via 1.1.1.1 dev eth1
"

echo "$interfaces" >> /etc/network/interfaces
echo "<M> GW network configuration added."

dnsmasq="
no-resolv
expand-hosts
domain=local

interface=eth0
dhcp-option=3,10.0.1.254  #server DHCP - IP della sua VLAN
dhcp-option=6,10.0.1.254  #server DNS
dhcp-option=15,local

#devo assegnare a H3 sempre lo stesso indirizzo (ip addr show eth0 - MAC)
# syntax -> dhcp-host=<MAC>,<hostname>,<IP>
dhcp-host=02:04:06:11:22:33,H3,10.0.1.21

# in questo caso Range dato dal testo
# syntax -> dhcp-range=<start_IP>,<end_IP>,<netmask>,<lease_time>
dhcp-range=10.0.1.10,10.0.1.20,255.255.255.0,12h
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

iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 8080 -s 2.2.2.2 -d 1.1.1.1 -j DNAT --to-destination 10.0.1.21:8080

if [ $? -eq 0 ]; then
    echo "<M> DNAT configuration added."
else
    echo "<M> Failed to add DNAT configuration."
    exit 1
fi
```

### Testare FLOW

Elementi di valutazione:

1. Il sistema DHCP fornisce parametri corretti di configurazione della rete per i nodi H1, H2
   - Verificare che i nodi H1 e H2 ricevano un indirizzo IP nella gamma 10.0.1.10 - 10.0.1.20
     - command -> `ip addr show eth0`
2. Il sistema DHCP fornisce parametri corretti di configurazione della rete per il nodo H3
   - Verificare che il nodo H3 riceva un indirizzo IP statico 10.0.1.21
     - command -> `ip addr show eth0`
3. I nodi GW e Ext sono configurati correttamente
   - Verificare che il nodo GW abbia l'indirizzo IP 10.0.1.254
     - command -> `ip addr show eth0`
   - Verificare che il nodo Ext abbia l'indirizzo IP 2.2.2.2
     - command -> `ip addr show eth0`
   - Pinga il nodo Ext da GW
     - command -> `ping 2.2.2.2`
   - Pinga il nodo GW da Ext
     - command -> `ping 10.0.1.254`
4. il servizio di SNAT è configurato correttamente
   - Prima PINGO (vedi punto 5)
   - Testo con `tcpdump -i eth0`
   - Controllo l'indirizzo IP sorgente che deve 1.1.1.1 (quello pubblico del GW, non quello privato)
5. I nodi H1, H2, H3 comunicano correttamente con Ext (verificare con ping)
   - Pinga il nodo Ext da H1
     - command -> `ping 2.2.2.2`
   - Pinga il nodo Ext da H2
     - command -> `ping 2.2.2.2`
   - Pinga il nodo Ext da H3
     - command -> `ping 2.2.2.2`
6. Il DNAT funziona correttamente (verificare con nc)
   - Eseguire il comando `nc -l -p 8080` su H3
     - (Attivi il listener)
   - Eseguire il comando `nc 1.1.1.1 8080` su Ext
     - (Invia un pacchetto)
   - Verificare che i pacchetti vengano ricevuti su H3
     - Provo a scrivere qualcosa nella connessione su `Ext` e verifico che arrivi su `H3`
