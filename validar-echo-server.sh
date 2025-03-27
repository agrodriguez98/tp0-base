#!/bin/bash
addr="server:12345"
sent="hola"
received=$(echo "$sent" | nc "$addr" -w 3)
if [ "$received" = "$sent" ]; then
	echo "action: test_echo_server | result: success"
else
	echo "action: test_echo_server | result: fail"
fi
