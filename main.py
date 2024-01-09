#!/usr/bin/python3

import sys, traceback, time, random, argparse

from game.sockets.server import ServerSocket 

from game.store.store import Store 
from game.library.library import Library
from game.player import Player

from game.interpreters.command.interpreter import CommandInterpreter
from game.interpreters.state.interpreter import StateInterpreter
from game.account_menu.welcome import WelcomeScreen 

from game.heartbeat import Heartbeat
 
def gameLoop(serverSocket, library, store):

    # Number of loops we've run.  Reset once it hits a certain value.  Used to
    # determine how often to perform certain tasks.
    loop_counter = 0

    # Number of loops we want to perform each second. 
    loops_a_second = 10

    # The length of a single loop in milliseconds.
    loop_length = 1000/loops_a_second

    heartbeat = Heartbeat(store, loops_a_second)

    state_interpreter = StateInterpreter()
    command_interpreter = CommandInterpreter(library, store)

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
            player.status = player.STATUS_ACCOUNT
            player.account_state = WelcomeScreen(player, library, store)
            store.players.append(player)

        serverSocket.resetPollSets()

        # Handle New Input
        for player in store.players:
            if player.hasInput():

                input = player.read().strip()

                if player.character:
                    if player.character.action:
                        player.character.action.cancel(player)
                        player.character.action = None
                        player.character.action_data = {}
                        player.character.action_time = 0
                        player.prompt_off = False

                # If we don't have input at this point, it means the player just sent
                # white space.  So we'll skip interpreting it and just send a new
                # prompt.
                if input:
                    if player.status == player.STATUS_ACCOUNT:
                        state_interpreter.interpret(player, input)
                    else:
                        command_interpreter.interpret(player, input)

        # Reset the loop counter at a value well below max int.  We only need it to continue to
        # increment, it doesn't matter what the value is.
        loop_counter = loop_counter + 1
        if loop_counter == 100000*loops_a_second:
            loop_counter = 0

        heartbeat.heartbeat(loop_counter)

        # Write prompts at the end of the loop if any reading or writing has
        # been done.
        for player in store.players:
            if player.character and player.character.action:
                player.prompt_off = True
            if player.need_prompt and not player.prompt_off:
                if player.character:
                    prompt = ""

                    hunger = player.character.reserves.hungerString(True)
                    if hunger:
                        if len(prompt) > 0:
                            prompt += ":"
                        prompt += hunger

                    thirst = player.character.reserves.thirstString(True)
                    if thirst:
                        if len(prompt) > 0:
                            prompt += ":"
                        prompt += thirst

                    sleep = player.character.reserves.sleepString(True)
                    if sleep:
                        if len(prompt) > 0:
                            prompt += ":"
                        prompt += sleep

                    wind = player.character.reserves.windString(True)
                    if wind:
                        if len(prompt) > 0:
                            prompt += ":"
                        prompt += wind

                    energy = player.character.reserves.energyString(True)
                    if energy:
                        if len(prompt) > 0:
                            prompt += ":"
                        prompt += energy

                    prompt += "> "
                    player.setPrompt(prompt)
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

    library = Library(store)

    print('Starting up the server on world "' + store.world.name + '" on port ' + repr(port))
    try:
        gameLoop(serverSocket, library, store)
    except KeyboardInterrupt:
        print("Shutting down.")
        serverSocket.shutdown()
    except Exception as ex:
        print("Shutting down due to error.")
        serverSocket.shutdown()
        raise ex 



if __name__ == '__main__':
    main()
