import socket
import logging
import signal
import sys
from multiprocessing import Process, Manager, Lock

from common.utils import *


class SignalHandler:
    def __init__(self, server):
        self.server = server
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signal, frame):
        self.server.shutdown()


class Server:
    def __init__(self, port, listen_backlog, number_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.signal_handler = SignalHandler(self)
        self.number_clients = number_clients
        self.manager = Manager()
        self.shared_data = self.manager.dict({
            'clients_finished': 0
        })
        self.locks = {
            'clients_finished': Lock()
        }

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After communucation with client
        finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            p = Process(target=self.__handle_client_connection,
                        args=(client_sock, self.locks))
            p.start()

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
        bets = list(
            map(lambda x: Bet(x[0], x[1], x[2], x[3], x[4], x[5]), data))
        store_bets(bets)
        logging.info(
            f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')

    def process_winners(self):
        winners = {id: [] for id in range(1, self.number_clients + 1)}
        for bet in load_bets():
            if has_won(bet):
                (winners[bet.agency]).append(bet)

        for (k, v) in winners.items():
            winners[k] = '|'.join(list(map(lambda x: x.document, v))) + '\n'

        return winners

    def send_results(self):
        winners = self.process_winners()
        for client_sock in self.pending_connections:
            client_sock.send("ID\n".encode('utf-8'))
            id_data = client_sock.recv(1024).decode('utf-8')
            id = int(id_data)
            winners_data = winners[id]
            client_sock.send(winners_data.encode('utf-8'))
            client_sock.close()

    def __handle_client_connection(self, client_sock, locks):
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
                    logging.info('client done sending batchs')
                    with self.locks['clients_finished']:
                        self.shared_data['clients_finished'] += 1
                    break
                elif header == 'r':
                    logging.info('results requested')
                    if self.is_finished():
                        client_sock.send("Done\n".encode('utf-8'))
                    else:
                        client_sock.send('Not yet\n'.encode('utf-8'))
                else:
                    logging.info(f'received unknown header: {header}')
                    logging.info(f'packet: {packet}')
                    break
        except OSError as e:
            logging.error(
                "action: receive_message | result: fail | error: {e}")
        finally:
            # add connection to waiting list
            client_sock.close()

    def is_finished(self):
        with self.locks['clients_finished']:
            return self.shared_data['clients_finished'] == self.number_clients

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
