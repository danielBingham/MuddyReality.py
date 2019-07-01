import sys, traceback

from sockets.server_socket import ServerSocket 
from library import Library
from player import Player
from interpreter.state import StateInterpreter
from account_states.get_account_name import GetAccountName

HOST = ''
PORT = 3000 

def gameLoop(serverSocket, library):
    # The Game Loop
    while serverSocket.isOpen:

        # Poll for input and output ready clients and then handle the communication.  Also accept
        # new clients.
        serverSocket.poll()

        serverSocket.handleReadSet()
        serverSocket.handleWriteSet()
        serverSocket.handleErrorSet()

        if serverSocket.hasNewConnection():
            newConnection = serverSocket.accept() 
            player = Player(newConnection)
            player.interpreter = StateInterpreter(player, library, GetAccountName(player, library))
            library.players.append(player)

        serverSocket.resetPollSets()

        # Handle New Input
        for player in library.players:
            if player.hasInput():
                player.interpret()

def main():
    serverSocket = ServerSocket(HOST, PORT)
    library = Library()

    print('Starting up the server on port ' + repr(PORT))
    try:
        gameLoop(serverSocket, library)
    except KeyboardInterrupt:
        print("Shutting down.")
        serverSocket.shutdown()


if __name__ == '__main__':
    main()
