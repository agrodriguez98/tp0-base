#!/bin/bash
sent="hola"
received=$(echo $sent | nc $1 $2 -w 3)
if [[ $received == $sent ]]; then
	echo "action: test_echo_server | result: success"
else
	echo "action: test_echo_server | result: fail"
fi
