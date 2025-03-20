#!/bin/bash
python3 validar-echo-server.py
ip=$(cat ip_file)
port=$(cat port_file)
sent="hola"
received=$(echo $sent | nc $ip $port -w 3)
if [[ $received == $sent ]]; then
	echo "action: test_echo_server | result: success"
else
	echo "action: test_echo_server | result: fail"
fi
