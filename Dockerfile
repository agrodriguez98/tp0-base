FROM ubuntu:20.04
COPY validar-echo-server.sh .
RUN chmod +x validar-echo-server.sh
RUN apt-get update && apt-get install -y netcat
ENTRYPOINT ["/bin/sh"]
