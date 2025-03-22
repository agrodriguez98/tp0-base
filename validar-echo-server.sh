#!/bin/bash
ip="server"
port="12345"
sent="hola"
received=$(echo $sent | nc $ip $port -w 3)
if [[ $received == $sent ]]; then
	echo "action: test_echo_server | result: success"
else
	echo "action: test_echo_server | result: fail"
fi
