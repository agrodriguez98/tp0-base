FROM ubuntu:20.04
COPY validar-echo-server.sh .
COPY validar-echo-server.py .
COPY server/config.ini .
RUN chmod +x validar-echo-server.sh
RUN apt-get update && apt-get install -y netcat && apt-get install python3 -y
ENTRYPOINT ["/bin/sh"]
