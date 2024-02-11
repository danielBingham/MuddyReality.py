#!/usr/bin/python3

import time, random, argparse

from game.sockets.server import ServerSocket 

from game.store.store import Store 
from game.library.library import Library
from game.player import Player

from game.interpreters.command.interpreter import CommandInterpreter
from game.interpreters.state.interpreter import StateInterpreter

import game.account_menu.welcome as welcome 
import game.account_menu.creation as creation
import game.account_menu.password as password
import game.account_menu.menu as menu

import game.commands.communication as communication 
import game.commands.information as information 
import game.commands.movement as movement
import game.commands.manipulation as manipulation
import game.commands.crafting as crafting
import game.commands.reserves as reserves
import game.commands.system as system

from game.heartbeat import Heartbeat
from game.world_time import WorldTime 


def gameLoop(serverSocket, world_time, library, store, account_interpreter, game_interpreter):
    """
    The primary game loop.  This method loops indefinitely (until killed using
    a keyboard interrupt).  It handles new connections to the game and
    input/output for existing connections.  It also runs the game's heartbeat.

    Parameters
    ----------
    serverSocket: ServerSocket
        The primary server socket that player sockets will connect to.
    library:    Library
        The game library.
    store: Store
        The game store.
    account_interpreter:    StateInterpreter
        An interpreter to be used for players in the Account Menu.
    game_interpreter:   CommandInterpreter
        An interpreter to be used for players who are playing the game.

    Returns
    -------
    void
    """

    # The length of a single loop in milliseconds.
    loop_length = 1000/world_time.loops_a_second

    heartbeat = Heartbeat(store, library)

    # The Game Loop
    while serverSocket.isOpen:
        start_time = time.time()*1000

        world_time.tick() 

        # Poll for input and output ready clients and then handle the
        # communication.  Also accept new clients.
        serverSocket.poll()

        serverSocket.handleReadSet()
        serverSocket.handleWriteSet()
        serverSocket.handleErrorSet()

        # If we have a new connection, create a player for it and send it to
        # the account flow starting with the welcome screen.
        if serverSocket.hasNewConnection():
            newConnection = serverSocket.accept() 
            player = Player(newConnection, account_interpreter, game_interpreter)
            player.status = player.STATUS_ACCOUNT
            player.setAccountState("welcome-screen")
            store.players.append(player)

        serverSocket.resetPollSets()

        # Handle New Input
        for player in store.players:
            player.interpret()

        heartbeat.heartbeat(world_time)

        # Write prompts at the end of the loop if any reading or writing has
        # been done.
        for player in store.players:
            player.writePrompt()

        # Once we reach the end of the loop, calculate how long it took and
        # sleep the remainder of the time.  This makes sure we don't loop more
        # than we want to.  If we're going too slow, then we'll just have to
        # keep going and hope we catch up.
        end_time = time.time()*1000
        loop_time = end_time - start_time
        if loop_time < loop_length:
            sleep_time = loop_length - loop_time - overrun
            if sleep_time > 0:
                time.sleep(sleep_time/1000)
        elif loop_time > loop_length:
            overrun = loop_time - loop_length 

        # Reset overrun.
        if loop_time <= loop_length:
            overrun = 0




def main():
    parser = argparse.ArgumentParser(
                    prog='main',
                    description='Run the Muddy Reality Server.')

    parser.add_argument('-H', '--host', dest='host', default='', help="What hostname do we want to run the server on?")
    parser.add_argument('-p', '--port', dest='port', default=3000, help="What port should we run the server on?")

    parser.add_argument('--data', default='data/', help='The location of the data directory, relative to this file.')
    parser.add_argument('--world', default='base', help='The name of the world we want to run the server for.') 

    parser.add_argument('--loops-a-second', dest='loops_a_second', default=10, help='The number of loops to allow in a second.')

    arguments = parser.parse_args()

    random.seed()

    host = arguments.host
    port = int(arguments.port)

    data_directory = arguments.data

    world_time = WorldTime(arguments.loops_a_second)

    serverSocket = ServerSocket(host, port)

    store = Store(world_time, arguments.world, data_directory)
    store.load()

    library = Library(store)

    # Initialize the states for the Account flow state interpreter.
    states = {}
    states['welcome-screen'] = welcome.WelcomeScreen(world_time, library, store)
    states['get-account-password'] = welcome.GetAccountPassword(world_time, library, store)
    states['create-new-account'] = creation.CreateNewAccount(world_time, library, store)
    states['account-menu'] = menu.AccountMenu(world_time, library, store)
    states['get-new-account-password'] = password.GetNewAccountPassword(world_time, library, store)
    states['confirm-new-account-password'] = password.ConfirmNewAccountPassword(world_time, library, store)
    account_interpreter = StateInterpreter(states, library, store)

    # Initialize the command list for commands in the game.
    #
    # Order matters here.  Commands are tested using `startswith` and the first
    # match is executed.  Commands defined earlier in the list will be tested
    # first and matched with shorter strings.  For example, if `east` is
    # defined before `eat`, then both `e` and `ea` will match `east` and `eat`
    # will nee to be fully typed out to match.  
    #
    # Keep this in mind and try to order commands by frequency of player use.
    # List is also intentionally in alphabetic order (except where player
    # convenience dictates breaking it) to enable ease of use.
    commands = {}
    commands['close'] = manipulation.Close(world_time, library, store)
    commands['craft'] = crafting.Craft(world_time, library, store)

    commands['down'] = movement.Down(world_time, library, store)
    commands['drink'] = reserves.Drink(world_time, library, store)
    commands['drop'] = manipulation.Drop(world_time, library, store)

    commands['east'] = movement.East(world_time, library, store)
    commands['eat'] = reserves.Eat(world_time, library, store)
    commands['equipment'] = information.Equipment(world_time, library, store)
    commands['examine'] = information.Examine(world_time, library, store)

    commands['get'] = manipulation.Get(world_time, library, store)

    commands['harvest'] = crafting.Harvest(world_time, library, store)
    # Help needs a reference to the command list so that it
    # can walk the list to describe the commands.
    commands['help'] = system.Help(commands, world_time, library, store)

    commands['inventory'] = information.Inventory(world_time, library, store)

    commands['look'] = information.Look(world_time, library, store)

    commands['north'] = movement.North(world_time, library, store)

    commands['open'] = manipulation.Open(world_time, library, store)

    commands['rest'] = reserves.Rest(world_time, library, store)
    commands['run'] = movement.Run(world_time, library, store)

    commands['quit'] = system.Quit(world_time, library, store)

    commands['south'] = movement.South(world_time, library, store)
    commands['say'] = communication.Say(world_time, library, store)
    commands['sleep'] = reserves.Sleep(world_time, library, store)
    commands['sprint'] = movement.Sprint(world_time, library, store)
    commands['status'] = information.Status(world_time, library, store)

    commands['time'] = information.Time(world_time, library, store)

    commands['west'] = movement.West(world_time, library, store)
    commands['walk'] = movement.Walk(world_time, library, store)
    commands['wield'] = manipulation.Wield(world_time, library, store)
    commands['wake'] = reserves.Wake(world_time, library, store)

    commands['up'] = movement.Up(world_time, library, store)
    game_interpreter = CommandInterpreter(commands, library, store)

    print('Starting up the server on world "' + store.world.name + '" on port ' + repr(port))
    try:
        gameLoop(serverSocket, world_time, library, store, account_interpreter, game_interpreter)
    except KeyboardInterrupt:
        print("Shutting down.")
        serverSocket.shutdown()
    except Exception as ex:
        print("Shutting down due to error.")
        serverSocket.shutdown()
        raise ex 


if __name__ == '__main__':
    main()
