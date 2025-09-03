
#!/bin/bash
# debug_struct.sh

if [ -z "$1" ]; then
    echo "Errore: specificare la porta come parametro."
    exit 1
fi

echo "Avvio cattura traffico..."
tcpdump -i lo -X -s 0 port $1 &
TCPDUMP_PID=$!

echo "Premi ENTER dopo aver testato client/server"
read

kill $TCPDUMP_PID
echo "Cattura terminata"