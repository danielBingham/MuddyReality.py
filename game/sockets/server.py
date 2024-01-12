import socket, select
from game.sockets.client import ClientSocket


class ServerSocket:
    'A socket server class, wrapping our select and polling logic.'

    def __init__(self, host, port):
        # Create our server socket that will be used to accept new connections
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.bind((host, port))
        self.server.listen(5)

        self.isOpen = True

        # Initialize the list of connected sockets, which is used for select polling.
        self.clients = []

        # Reset the lists we use for polling our clients and determining which clients are in
        # various ready states. 
        self.resetPollSets()

    def resetPollSets(self):
        # Poll lists, populated by select and read by the input handling methods.
        self.readable = []
        self.writeable = []
        self.erroring = []
        self.newConnections = False

    def poll(self):
        readSet = list(self.clients)
        readSet.append(self.server)

        writeSet = list(self.clients)
        errorSet = list(self.clients)

        self.readable, self.writeable, self.erroring = select.select(readSet, writeSet, errorSet)

    def handleReadSet(self):
        while self.readable:
            client = self.readable.pop()
            if client is not self.server:
                client.read()
            elif client is self.server:
                self.newConnections = True

    def handleWriteSet(self):
        while self.writeable:
            client = self.writeable.pop()
            if client.hasOutput():
                client.write()

    def handleErrorSet(self): 
        while self.erroring:
            client = self.erroring.pop()
            client.handleError()

    def hasNewConnection(self):
        return self.newConnections

    def accept(self):
        try:
            client = ClientSocket(self.server.accept(), self)
        except socket.error: 
            return None

        self.clients.append(client)
        return client

    # Remove a socket from the client list
    def remove(self, client):
        self.clients.remove(client)

    def shutdown(self):
        for client in self.clients:
            client.close()
        self.server.close()
        self.isOpen = False

# End ServerSocket
