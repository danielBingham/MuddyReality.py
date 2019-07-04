import sys, traceback, time

from sockets.server import ServerSocket 
from library import Library
from player import Player
from interpreter.state import StateInterpreter
from account.welcome import WelcomeScreen 

HOST = ''
PORT = 3000 

def gameLoop(serverSocket, library):

    # Number of loops we've run.  Reset once it hits a certain value.  Used to determine how often
    # to perform certain tasks.
    loop_counter = 0

    # Max value to allow the counter to reach before resetting it
    max_counter = 100000000

    # Number of loops we want to perform each second. 
    loops_a_second = 10
    loop_length = 1000/loops_a_second

    # The Game Loop
    while serverSocket.isOpen:
        start_time = time.time()*1000

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

        if loop_counter % (5 * loops_a_second) == 0:
            library.save()

        loop_counter = loop_counter + 1
        if loop_counter == max_counter:
            loop_counter = 0

        # Once we reach the end of the loop, calculate how long it took and sleep the remainder of
        # the time.  This makes sure we don't loop more than we want to.  If we're going too slow,
        # then we'll just have to keep going and hope we catch up.
        end_time = time.time()*1000
        if end_time - start_time < loop_length:
            sleep_time = loop_length - (end_time - start_time)
            time.sleep(sleep_time/1000)


def main():
    serverSocket = ServerSocket(HOST, PORT)
    library = Library()
    library.load()

    print('Starting up the server on port ' + repr(PORT))
    try:
        gameLoop(serverSocket, library)
    except KeyboardInterrupt:
        print("Shutting down.")
        serverSocket.shutdown()


if __name__ == '__main__':
    main()
