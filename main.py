#!/usr/bin/python3

import sys, traceback, time, random, argparse

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
 
def gameLoop(serverSocket, library, store, account_interpreter, game_interpreter):
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

        # Reset the loop counter at a value well below max int.  We only need
        # it to continue to increment, it doesn't matter what the value is.
        loop_counter = loop_counter + 1
        if loop_counter == 100000*loops_a_second:
            loop_counter = 0

        heartbeat.heartbeat(loop_counter)

        # Write prompts at the end of the loop if any reading or writing has
        # been done.
        for player in store.players:
            player.writePrompt()

        # Once we reach the end of the loop, calculate how long it took and
        # sleep the remainder of the time.  This makes sure we don't loop more
        # than we want to.  If we're going too slow, then we'll just have to
        # keep going and hope we catch up.
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

    parser.add_argument('--data', default='data/', help='The location of the data directory, relative to this file.')
    parser.add_argument('--world', default='base', help='The name of the world we want to run the server for.') 

    arguments = parser.parse_args()

    random.seed()

    host = arguments.host
    port = int(arguments.port)

    data_directory = arguments.data

    serverSocket = ServerSocket(host, port)

    store = Store(arguments.world, data_directory)
    store.load()

    library = Library(store)

    # Initialize the states for the Account flow state interpreter.
    states = {}
    states['welcome-screen'] = welcome.WelcomeScreen(library, store)
    states['get-account-password'] = welcome.GetAccountPassword(library, store)
    states['create-new-account'] = creation.CreateNewAccount(library, store)
    states['account-menu'] = menu.AccountMenu(library, store)
    states['get-new-account-password'] = password.GetNewAccountPassword(library, store)
    states['confirm-new-account-password'] = password.ConfirmNewAccountPassword(library, store)
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
    commands['close'] = manipulation.Close(library, store)
    commands['craft'] = crafting.Craft(library, store)

    commands['down'] = movement.Down(library, store)
    commands['drink'] = reserves.Drink(library, store)
    commands['drop'] = manipulation.Drop(library, store)

    commands['east'] = movement.East(library, store)
    commands['eat'] = reserves.Eat(library, store)
    commands['equipment'] = information.Equipment(library, store)
    commands['examine'] = information.Examine(library, store)

    commands['get'] = manipulation.Get(library, store)

    commands['harvest'] = crafting.Harvest(library, store)
    # Help needs a reference to the command list so that it
    # can walk the list to describe the commands.
    commands['help'] = system.Help(commands, library, store)

    commands['inventory'] = information.Inventory(library, store)

    commands['look'] = information.Look(library, store)

    commands['north'] = movement.North(library, store)

    commands['open'] = manipulation.Open( library, store)

    commands['rest'] = reserves.Rest(library, store)
    commands['run'] = movement.Run( library, store)

    commands['quit'] = system.Quit( library, store)

    commands['south'] = movement.South( library, store)
    commands['say'] = communication.Say( library, store)
    commands['sleep'] = reserves.Sleep( library, store)
    commands['sprint'] = movement.Sprint( library, store)
    commands['status'] = information.Status( library, store)

    commands['west'] = movement.West( library, store)
    commands['walk'] = movement.Walk( library, store)
    commands['wield'] = manipulation.Wield( library, store)
    commands['wake'] = reserves.Wake( library, store)

    commands['up'] = movement.Up(library, store)
    game_interpreter = CommandInterpreter(commands, library, store)

    print('Starting up the server on world "' + store.world.name + '" on port ' + repr(port))
    try:
        gameLoop(serverSocket, library, store, account_interpreter, game_interpreter)
    except KeyboardInterrupt:
        print("Shutting down.")
        serverSocket.shutdown()
    except Exception as ex:
        print("Shutting down due to error.")
        serverSocket.shutdown()
        raise ex 



if __name__ == '__main__':
    main()
