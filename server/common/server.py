import socket
import logging
import signal
import sys

from common.utils import *

class SignalHandler:
    def __init__(self, server):
        self.server = server
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signal, frame):
        self.server.shutdown()

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.signal_handler = SignalHandler(self)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After communucation with client
        finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def shutdown(self):
        fd = self._server_socket.fileno()
        self._server_socket.close()
        logging.info(f'action: shutdown | result: success | socket fd: {fd}')
        sys.exit(0)

    def recv(self, client_sock, size):
        data = client_sock.recv(size)
        while (len(data) < size):
            data = client_sock.recv(size)
        return data

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                packet = client_sock.recv(1024).decode('utf-8')
                msg = packet.split('|')
                header = msg[0]
                if header == 's':
                    client_sock.send("ACK\n".encode('utf-8'))
                    size = int(msg[1])
                    batch = client_sock.recv(size).decode('utf-8')
                    logging.info(batch)
                    client_sock.send("ACK\n".encode('utf-8'))
                    # process batch
                elif header == 'd':
                    client_sock.send("ACK\n".encode('utf-8'))
                    logging.info('client done')
                    break
                else:
                    logging.info('received unknown header')
            '''data = msg.split('|')
            bet = Bet(data[0], data[1], data[2], data[3], data[4], data[5])
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')

            client_sock.send("ACK\n".encode('utf-8'))'''
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
