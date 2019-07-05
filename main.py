import sys, traceback, time

from sockets.server import ServerSocket 
from library import Library
from player import Player
from interpreter.state import StateInterpreter
from account.welcome import WelcomeScreen 

HOST = ''
PORT = 3001 

# A method called on every loop that can be used for actions that need to take place every so many
# loops.  Used to control autonomous timing in the game world.
def heartbeat(library, loop_counter, loops_a_second):
    pass

def gameLoop(serverSocket, library):

    # Number of loops we've run.  Reset once it hits a certain value.  Used to determine how often
    # to perform certain tasks.
    loop_counter = 0

    # Number of loops we want to perform each second. 
    loops_a_second = 10

    # The lenght of a single loop in milliseconds.
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
            player.interpreter = StateInterpreter(player, library, WelcomeScreen(player, library))
            library.players.append(player)

        serverSocket.resetPollSets()

        # Handle New Input
        for player in library.players:
            if player.hasInput():
                player.interpret()

        # Reset the loop counter at a value well below max int.  We only need it to continue to
        # increment, it doesn't matter what the value is.
        loop_counter = loop_counter + 1
        if loop_counter == 100000*loops_a_second:
            loop_counter = 0

        heartbeat(library, loop_counter, loops_a_second)

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
    except Exception as ex:
        print("Shutting down due to error.")
        serverSocket.shutdown()
        raise ex 



if __name__ == '__main__':
    main()
