import sys, traceback, time, random

from sockets.server import ServerSocket 
from library import Library
from player import Player
from interpreter.state import StateInterpreter
from account.welcome import WelcomeScreen 

HOST = ''
PORT = 3000 


# A method called on every loop that can be used for actions that need to take
# place every so many loops.  Used to control autonomous timing in the game
# world.
def heartbeat(library, loop_counter, loops_a_second):
    loops_a_game_minute = loops_a_second
    loops_a_game_hour = loops_a_game_minute * 60

    # Do hunger calculations once a game minute.
    if loop_counter % loops_a_game_minute == 0:
        for name in library.characters.repo:
            character = library.characters.getById(name)

            # Only do calculations for characters actively in the game.
            if not character.player:
                continue

            character.reserves.calories -= 2

    # Do tired calculations once a game hour. 
    #
    # The player's tiredness is stored as a 'sleep reserve' under
    # `character.reserves.sleep`.  It's stored as an integer representing the
    # number of hours they can stay awake without suffering any kind of
    # tiredness penalty.  The reserve is reduced by `1` for each hour the
    # character stays awake and increases by `2` for each hour spent sleeping,
    # roughly matching a schedule with 8 hours of sleep and 16 hours awake.
    #
    # Once the sleep reserve is drained below zero the player starts to suffer
    # tiredness penalties.  The primary penalty is a risk of falling asleep
    # that increases steadily up to 248 hours spent awake past the 16 hours
    # rested (16+248 = 264), the record number of hours any human has remained
    # awake.
    if loop_counter % loops_a_game_hour == 0:
        for name in library.characters.repo:
            character = library.characters.getById(name)
            
            # Only do tiredness calculations for characters actively being
            # played.
            if not character.player:
                continue

            # If they're awake, then get more tired.
            if character.position != character.POSITION_SLEEPING:
                character.reserves.sleep -= 1

            # If they're asleep they recover.
            elif character.position == character.POSITION_SLEEPING:
                character.reserves.sleep += 2

            # If they're tired, they have an increasing chance of falling
            # asleep.
            if character.reserves.sleep < 0:
                chance = random.randint(0,248)
                if abs(character.reserves.sleep) < chance:
                    character.position = character.POSITION_SLEEPING
                    if character.player:
                        character.player.write("You can't stay awake anymore.  You fall asleep.")
 

def gameLoop(serverSocket, library):

    # Number of loops we've run.  Reset once it hits a certain value.  Used to
    # determine how often to perform certain tasks.
    loop_counter = 0

    # Number of loops we want to perform each second. 
    loops_a_second = 10

    # The length of a single loop in milliseconds.
    loop_length = 1000/loops_a_second

    # The Game Loop
    while serverSocket.isOpen:
        start_time = time.time()*1000

        # Poll for input and output ready clients and then handle the
        # communication.  Also accept new clients.
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
    random.seed()

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
