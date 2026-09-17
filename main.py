#!/usr/bin/python3

###############################################################################
# MuddyReality.py
#
# The single entry point for the project.  Parses the command line and
# dispatches to either the game server (`server.py`) or the world generator
# (`generate.py`).
#
#   python3 main.py server [server arguments]
#   python3 main.py generator [name] [generator arguments]
#
# Use `python3 main.py <command> --help` to see the arguments for a command.
###############################################################################

import argparse


def addServerArguments(parser):
    """
    Define the command line arguments for the `server` command.

    Parameters
    ----------
    parser: argparse.ArgumentParser
        The subparser for the `server` command.

    Returns
    -------
    void
    """

    parser.add_argument('-H', '--host', dest='host', default='',
                        help="What hostname do we want to run the server on?")
    parser.add_argument('-p', '--port', dest='port', default=3000,
                        help="What port should we run the server on?")

    parser.add_argument('--data', default='data/', help='The location of the data directory, relative to this file.')
    parser.add_argument('--world', default='base', help='The name of the world we want to run the server for.')

    parser.add_argument('--loops-a-second', dest='loops_a_second', default=10, help='The number of loops to allow in a second.')
    parser.add_argument('--loop-sample-rate', dest='loop_sample_rate', default=10, help='Sample the loop time every `x` seconds.')


def addGeneratorArguments(parser):
    """
    Define the command line arguments for the `generator` command.

    Parameters
    ----------
    parser: argparse.ArgumentParser
        The subparser for the `generator` command.

    Returns
    -------
    void
    """

    parser.add_argument('name', help='A name for the world that heights are being generated for.  This will be used as the output directory under `data/worlds/`.')

    # World shape parameters.
    parser.add_argument('--width', default=100, help='Width of the world in rooms.  World will be square with width^2 total rooms..')
    parser.add_argument('--room-width', dest='room_width', default=100, help='Width of an individual room in meters.  World will be (room-width*width)^2 total area.')

    # Parameters for controlling which parts of the generating we're doing.
    parser.add_argument('--generate-heights', dest='generate_heights', action='store_true', help='Only generate the height map.  Will generate the worlds.json file if it does not exist.')
    parser.add_argument('--generate-water', dest='generate_water', action='store_true', help='Only generate the worlds water.')
    parser.add_argument('--generate-biomes', dest='generate_biomes', action='store_true', help='Only generate the biomes. world.json matching `name` must have heights already generated.')
    parser.add_argument('--generate-rooms', dest='generate_rooms', action='store_true', help='Only generate the rooms. world.json matching `name` must have heights and biomes already generated.')

    # Parmeters for controlling what, if anything, we should regenerate.  If
    # none of these are true, then anything previously generated will be reused
    # as is.  That stage of generation will be skipped.
    parser.add_argument('--regenerate-all', dest='regenerate_all', action='store_true', help='Regenerate the world, overriding any previously generated world.')
    parser.add_argument('--rengerate-heights', dest='regenerate_heights', action='store_true', help="Regenerate the world's heightmap, overriding any previously generated terrain.")
    parser.add_argument('--regenerate-water', dest='regenerate_water', action='store_true', help="Regenerate the world's water, overriding any previously generated water.")
    parser.add_argument('--regenerate-biomes', dest='regenerate_biomes', action='store_true', help="Regenerate the world's biomes, overriding any previously generated biomes.")
    parser.add_argument('--regenerate-rooms', dest='regenerate_rooms', action='store_true', help="Regenerate the world's rooms, overriding any previously generated rooms.")

    # Water generation parameters
    parser.add_argument('--water-initial-amount', default=30, dest='water__initial_amount', help="The initial water that will be dumped on the world and allowed to flow to the low areas in depth (meters) per world point.")
    parser.add_argument('--water-algorithm', default='inria', dest='water__algorithm', help='Choose the algorithm that will be used to generate water.')
    parser.add_argument('--water-debug', dest="water__debug", action="store_true", help="Turn on debugging output for the water algorith.")
    parser.add_argument("--water-snapshot", dest="water__snapshot", action="store_true", help="Turn on snapshotting for the water algorithm.  This will take an image snapshot of the water at the end of each iteration and then construct an animation of them showing the full water flow for the duration of the simulation at the end.  Images will be stored in the `snaps/` directory.")
    parser.add_argument("--water-flat-terrain", dest="water__flat_terrain", action="store_true", help="Run the water simulation on a flat terrain instead of the terrain generated in the previous step.")


def buildParser():
    """
    Build the top level argument parser, with a subcommand for each of the
    project's programs.

    Returns
    -------
    argparse.ArgumentParser
    """

    parser = argparse.ArgumentParser(
                    prog='main',
                    description='Run the Muddy Reality server, or generate a world for it.')

    subparsers = parser.add_subparsers(dest='command', metavar='{server,generator}', required=True)

    server_parser = subparsers.add_parser(
                    'server',
                    help='Run the game server.',
                    description='Run the Muddy Reality Server.')
    addServerArguments(server_parser)

    generator_parser = subparsers.add_parser(
                    'generator',
                    help='Generate a world for the game.',
                    description='Generate a world for Muddy Reality.')
    addGeneratorArguments(generator_parser)

    return parser


def main():
    arguments = buildParser().parse_args()

    # Only import the module for the command we're running.  The generator
    # depends on imaging libraries (matplotlib, Pillow, imageio) that the
    # server has no use for, so the server shouldn't need them installed.
    if arguments.command == 'server':
        import server
        server.run(arguments)
    elif arguments.command == 'generator':
        import generate
        generate.run(arguments)


if __name__ == '__main__':
    main()
