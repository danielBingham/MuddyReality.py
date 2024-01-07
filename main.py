#!/usr/bin/python3

import sys, traceback, time, random, argparse

from game.sockets.server import ServerSocket 

from game.store.store import Store 
from game.store.player import Player

from game.interpreters.state import StateInterpreter
from game.account_menu.welcome import WelcomeScreen 

from game.heartbeat import Heartbeat
 
def gameLoop(serverSocket, store):

    # Number of loops we've run.  Reset once it hits a certain value.  Used to
    # determine how often to perform certain tasks.
    loop_counter = 0

    # Number of loops we want to perform each second. 
    loops_a_second = 10

    # The length of a single loop in milliseconds.
    loop_length = 1000/loops_a_second

    heartbeat = Heartbeat(store, loops_a_second)

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
