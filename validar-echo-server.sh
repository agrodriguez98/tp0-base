#!/bin/bash
addr="server:12345"
sent="hola"
received=$(echo "$sent" | nc "$addr")
if [ "$received" = "$sent" ]; then
	echo "action: test_echo_server | result: success"
else
	echo "action: test_echo_server | result: fail"
fi
