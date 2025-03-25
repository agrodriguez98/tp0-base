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
        self.pending_connections = []

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
            # verify all clients sent data
            if len(self.pending_connections) == 5:
                logging.info(f'action: sorteo | result: success')
                self.send_results()
                self.pending_connections.clear()

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

    def process_batch(self, batch):
        data = list(map(lambda x: x.split('|'), batch.split('||')))
        bets = list(map(lambda x: Bet(x[0], x[1], x[2], x[3], x[4], x[5]), data))
        store_bets(bets)
        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')

    def process_winners(self, agency_id, bets):
        winning_bets = list(filter(lambda x: x.agency == agency_id and has_won(x), bets))
        winners = list(map(lambda x: x.document, winning_bets))
        return '|'.join(winners) + '\n'

    def send_results(self):
        bets = load_bets()
        for client_sock in self.pending_connections:
            client_sock.send("ID\n".encode('utf-8'))
            id_data = client_sock.recv(1024).decode('utf-8')
            id = int(id_data)
            winners_data = self.process_winners(id, bets)
            client_sock.send(winners_data.encode('utf-8'))
            client_sock.close()

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
                    self.process_batch(batch)
                    client_sock.send("ACK\n".encode('utf-8'))
                elif header == 'd':
                    break
                else:
                    logging.info('received unknown header')
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            # add connection to waiting list
            self.pending_connections.append(client_sock)

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
