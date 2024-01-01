#!/usr/bin/python3

import sys, traceback, time, random, argparse

from game.sockets.server import ServerSocket 
from game.store.store import Store 
from game.store.player import Player
from game.interpreters.state import StateInterpreter
from game.account_menu.welcome import WelcomeScreen 

# A method called on every loop that can be used for actions that need to take
# place every so many loops.  Used to control autonomous timing in the game
# world.
def heartbeat(store, loop_counter, loops_a_second):
    loops_a_game_minute = loops_a_second
    loops_a_game_hour = loops_a_game_minute * 60

    # Advance any actions or action timers.
    if loop_counter % loops_a_game_minute == 0:
        for player in store.players:
            if not player.character:
                continue
            if not player.character.action:
                continue

            player.character.action_time -= 1
            if player.character.action_time > 0:
                player.prompt_off = True
                player.write(".", wrap=False)
                player.character.action.step(player)
            else:
                player.character.action.finish(player)
                player.character.action = None
                player.character.action_data = {}
                player.character.action_time = 0
                player.prompt_off = False

    # Do hunger calculations once a game minute.
    if loop_counter % loops_a_game_minute == 0:
        for player in store.players:
            if not player.character:
                continue
            player.character.reserves.calories -= 2

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
        for player in store.players:
            if not player.character:
                continue

            character = player.character

            # If they're awake, then get more tired.
            if character.position != character.POSITION_SLEEPING:
                character.reserves.sleep -= 1

            # If they're asleep they recover.
            elif character.position == character.POSITION_SLEEPING:
                character.reserves.sleep += 2

                if character.reserves.sleep >= 16:
                    character.position = character.POSITION_STANDING
                    player.write("You awaken, fully rested.")


            # If they're tired, they have an increasing chance of falling
            # asleep.
            if character.reserves.sleep < 0:
                chance = random.randint(0,248)
                if abs(character.reserves.sleep) < chance:
                    character.position = character.POSITION_SLEEPING
                    character.player.write("You can't stay awake anymore.  You fall asleep.")

    # Update player prompts
    if loop_counter % loops_a_game_minute == 0:
        for player in store.players:
            if player.character:
                prompt = ""
                prompt += player.character.reserves.hungerString(True)
                if len(prompt) > 0:
                    prompt += ":"
                prompt += player.character.reserves.sleepString(True)
                prompt += "> "
                player.setPrompt(prompt)
 

def gameLoop(serverSocket, store):

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
            player.interpreter = StateInterpreter(player, store, WelcomeScreen(player, store))
            store.players.append(player)

        serverSocket.resetPollSets()

        # Handle New Input
        for player in store.players:
            if player.hasInput():
                player.interpret()

        # Reset the loop counter at a value well below max int.  We only need it to continue to
        # increment, it doesn't matter what the value is.
        loop_counter = loop_counter + 1
        if loop_counter == 100000*loops_a_second:
            loop_counter = 0

        heartbeat(store, loop_counter, loops_a_second)

        # Write prompts at the loop if any reading or writing has been done.
        for player in store.players:
            if player.need_prompt and not player.prompt_off:
                player.write(player.getPrompt(), wrap=False)
                player.setPromptInBuffer(True)
                player.need_prompt = False

        # Once we reach the end of the loop, calculate how long it took and sleep the remainder of
        # the time.  This makes sure we don't loop more than we want to.  If we're going too slow,
        # then we'll just have to keep going and hope we catch up.
        end_time = time.time()*1000
        if end_time - start_time < loop_length:
            sleep_time = loop_length - (end_time - start_time)
            time.sleep(sleep_time/1000)


def main():
    parser = argparse.ArgumentParser(
                    prog='main',
                    description='Run the Muddy Reality Server.')

    parser.add_argument('-H', '--host', dest='host', default='', help="What hostname do we want to run the server on?")
    parser.add_argument('-p', '--port', dest='port', default=3000, help="What port should we run the server on?")

    parser.add_argument('--world', default='base', help='The name of the world we want to run the server for.') 

    arguments = parser.parse_args()

    random.seed()

    host = arguments.host
    port = int(arguments.port)

    serverSocket = ServerSocket(host, port)
    store = Store(arguments.world)
    store.load()

    print('Starting up the server on port ' + repr(port))
    try:
        gameLoop(serverSocket, store)
    except KeyboardInterrupt:
        print("Shutting down.")
        serverSocket.shutdown()
    except Exception as ex:
        print("Shutting down due to error.")
        serverSocket.shutdown()
        raise ex 



if __name__ == '__main__':
    main()
