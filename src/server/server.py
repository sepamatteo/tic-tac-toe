'''
code author : Matteo Sepa
contact : sepamatteo@protonmail.me
website : sepamatteo.github.io

Software released under GNU GPLv3 license
'''

import socket
import threading
import sys


class SocketConnection:
    """Classe che gestisce la connessione attraverso socket"""

    # Server IP and port
    IP = "127.0.0.1"
    PORT = 12345

    turn = "x"

    # Socket type and options
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((IP, PORT))
    server_socket.listen()

    # dictionary of client sockets and their nicknames
    clients = {}

    print(f"Listening for connections on {IP}:{PORT}...")


    # Sending Messages To All Connected Clients
    def broadcast(self, message, client_socket):
        """Metodo che invia un messaggio in broadcast a gli host connessi"""
        # Send messages to all clients except to the original sender
        for client in self.clients.keys():
            if client is not client_socket:
                client.send(message.encode("utf-8"))


    # Function to be called per client
    def handle(self, client_socket):
        """Metodo che gestisce la connessione"""
        while True:
            message = client_socket.recv(1024).decode("utf-8")
            print(message)
            self.broadcast(message, client_socket)
            if "!exit" in message:
                client_socket.close()
                broadcast("{} left!".format(clients[client_socket]), client_socket)
                clients.pop(client_socket)
                print(clients)
                sys.exit()


    # Receiving / Listening Function
    def receive(self):
        """Metodo che gestisce le connessioni e fa partire il thread"""
        global turn
        while True:
            # Accept Connection
            client_socket, address = self.server_socket.accept()
            print("Connected with {}".format(str(address)))
            client_socket.send(self.turn.encode('utf-8'))
            nickname = f'player {self.turn}'
            if self.turn == "x":
                self.turn = "o"
            elif self.turn == "o":
                self.turn = "x"
            self.clients.update({client_socket: nickname})

            # Start Handling Thread For Client
            
            thread = threading.Thread(target=self.handle, args=(client_socket,))
            thread.start()


def main():
    """Main"""
    sock = SocketConnection()
    sock.receive()


if __name__ == '__main__':
    main()