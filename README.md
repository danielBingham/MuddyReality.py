# MuddyReality.py

A multi-user dungeon written in python with a focus on realism.  Best used to
create open world, survival, crafting MUDs.

Includes two main pieces: the game itself and world generators.   The game is
stored in `game` and `server.py`.  The generators are stored in `generator` and
`generate.py`.  Both are run through `main.py`, and they both work with data
stored in `data`.

The world generators will generate worlds by first generating a base terrain
with fbm noise, then eroding that terrain using a water flow and sediment
simulation, then place water in that world using a similar water flow
simulation with rain, then generate biomes using a succession and disruption
simulation, and finally generate rooms using all of that data. 

This project is related to MuddyReality, which is the C++ implementation of the
same engine.  The two are built to use the same world data.  Eventually the
hope is to be able to run small worlds and rapidly test out new features with
the python variant in order to later translate them into the C++ engine to
enable their use in larger worlds.

## Status

This project is currently in alpha.  It's a side project I'm working on purely
for fun and pleasure.  It advances in short bursts when I've got downtime.
It's a long term project I expect to continue slowly chipping away at over the
course of the next decade.

## Development Setup

### Python Version

MuddyReality.py requires Python 3.12.  The game server uses `telnetlib`, which
was removed from Python in 3.13, and the dependencies pinned in
`requirements.txt` don't support newer versions of Python.  The Docker image
uses Python 3.12 as well.

On macOS, install Python 3.12 with Homebrew.  This adds `python3.12` to your
`PATH` alongside any other versions you have, and leaves `python3` unchanged.

```
$ brew install python@3.12
$ python3.12 --version
```

On other platforms, install Python 3.12 using your package manager or a version
manager such as `pyenv`.

### Creating the Virtual Environment

Install the project's dependencies into a virtual environment named `.venv` in
the top level directory.  From the top level directory:

```
$ python3.12 -m venv .venv
$ source .venv/bin/activate
$ python -m pip install --upgrade pip
$ python -m pip install -r requirements.txt
```

Keep the virtual environment at `.venv`.  `mypy.ini` and `pyrightconfig.json`
expect to find it there.

Homebrew's Python won't install packages outside of a virtual environment, and
`pip install` will fail with an `externally-managed-environment` error.  Install
the project's packages into `.venv` instead.  Don't use
`--break-system-packages`, which installs packages into Homebrew's Python and
can break it.  Don't use `pipx` for the project's packages either: it installs
each package in its own isolated environment, where the project can't import
it.

To start over, run `deactivate` if the virtual environment is active, delete
`.venv`, and repeat the steps above.  Do the same if the virtual environment
stops working after Homebrew upgrades Python 3.12.

```
$ rm -rf .venv
```

### Using the Virtual Environment

Activate the virtual environment in each new shell before working on the
project.  While it's active, `python` and `pip` run from the virtual
environment.  Deactivate it when you're done.

```
$ source .venv/bin/activate
$ deactivate
```

You can also run the virtual environment's Python without activating it:

```
$ .venv/bin/python main.py server
```

To lint the code and run the unit tests:

```
$ ./build.sh
```

Start your editor from a shell with the virtual environment active, so that
its language servers and linters can find the project's packages.

## Running

Both the game and the generator are run through `main.py` in the top level
directory.  Its first argument chooses what to run: `server` or `generator`.
Everything after that is passed to the chosen command.  Use `--help` after a
command to list all of its arguments.

```
$ python main.py server --help
$ python main.py generator --help
```

The examples in this section assume the virtual environment is active.  To run
the game or the generator in Docker instead, see
[Running with Docker](#running-with-docker).

### Game

To run the game, run the `server` command.  Stop the server with `Ctrl-C`.

```
$ python main.py server
```

The `server` command's most commonly used arguments are:

* `--world [name]`: Run the game with the world named by `[name]`.  `[name]` must be a directory under `data/worlds/` that contains a `world.json` file and a `rooms/` directory with rooms defined in `json`.  Defaults to `base`, a small hand-built world.
* `--port [port]` (`-p`): Run the game on `[port]`.  Defaults to `3000`.
* `--host [host]` (`-H`): The address to listen on.  Defaults to all addresses.

```
$ python main.py server --world base --port 4000
```

Connect to the game with a telnet client, or with `nc`.  macOS no longer
includes `telnet`, but `nc` works just as well.

```
$ nc localhost 3000
```

The server saves accounts to `data/accounts/` and characters to
`data/characters/`.

### Generator

To generate worlds for the game, run the `generator` command.

```
$ python main.py generator [name]
```

`[name]` is the only required argument, and represents the name of the world.
The world is saved to `data/worlds/[name]/`, and `[name]` is the same name that
will be passed to `--world` to run the game.  For example, to generate a small
world and then play in it:

```
$ python main.py generator tiny --width 12 --room-width 50
$ python main.py server --world tiny
```

Generation runs in four stages, each building on the ones before it: heights,
water, biomes and rooms.  The results are saved in `data/worlds/[name]/`:
`world.json` holds the world, `rooms/` holds the rooms, and `terrain.png`,
`water.png` and `biomes.png` are images of the heights, water and biomes
stages.  When you run the generator again for an existing world, stages that
were already generated are reused unless you ask to regenerate them.

The default world is 100 rooms wide, for 10,000 rooms in total, and takes much
longer to generate than a small world.  Use a small `--width` when testing.

The generator takes a number of optional arguments that can be used to control
how the world is generated.

World shape:

* `--width [width]`: Set the width of the game world in number of rooms.  The world is square, with `width * width` rooms.  Takes an integer.  Defaults to `100` rooms.
* `--room-width [width]`: Set the width of a room in the game world in number of meters.  This will impact the simulations used to generate the world as well as certain aspects of how resources are used in the game.  Takes an integer.  Defaults to `100` meters.

Stages to run.  With none of these, all four stages are run.

* `--generate-heights`: Only run the heights stage.
* `--generate-water`: Run the stages up to and including water.
* `--generate-biomes`: Run the stages up to and including biomes.
* `--generate-rooms`: Run all four stages.

Stages to regenerate.  Regenerating a stage doesn't regenerate the stages
after it, so pass their flags as well, or use `--regenerate-all`.

* `--regenerate-all`: Regenerate the whole world, replacing anything previously generated.  Required to change the `--width` or `--room-width` of an existing world.
* `--rengerate-heights`: Regenerate the heights.  Note the spelling of this flag.
* `--regenerate-water`: Regenerate the water.
* `--regenerate-biomes`: Regenerate the biomes.
* `--regenerate-rooms`: Regenerate the rooms.

Water simulation:

* `--water-algorithm [algorithm]`: The algorithm used to place water, either `inria` or `dandrino`.  Defaults to `inria`.
* `--water-initial-amount [depth]`: The depth of water, in meters, placed on every point of the world before it flows to low areas.  Defaults to `30` meters.  Used by the `inria` algorithm.
* `--water-snapshot`: Save an image of the water after each iteration of the simulation to `snaps/`, then an animation of the whole simulation to `snaps/animation.gif`.  The `snaps/` directory must already exist.
* `--water-flat-terrain`: Run the water simulation on flat terrain instead of the generated heights.
* `--water-debug`: Print debugging output from the water simulation.  Used by the `inria` algorithm.

## Running with Docker

The Docker image contains Python 3.12 and all of the project's dependencies,
so it can run the game and the generator without a virtual environment.  Run
the commands below from the top level directory.

### Building the Image

```
$ docker build -t muddyreality .
```

The image contains a copy of the code and data, so rebuild it after changing
them, as well as after changing `requirements.txt` or the `Dockerfile`.  To
avoid rebuilding for code and data changes, mount the repository as described
in [Developing with Docker](#developing-with-docker).

### Running the Game

The image runs the game server by default.  Mount `data/` so that accounts,
characters and worlds are read from and saved to your copy of the repository.
Without the mount, they are lost when the container exits.

```
$ docker run --rm -it -p 3000:3000 -v "$(pwd)/data:/src/data" muddyreality
```

Stop the server with `Ctrl-C`, and connect to it with `nc localhost 3000` as
when running it locally.  To pass arguments to the server, add the `server`
command and its arguments after the image name:

```
$ docker run --rm -it -p 3000:3000 -v "$(pwd)/data:/src/data" muddyreality server --world tiny
```

If you change the port with `--port`, change the `-p` option to match.  For
example, use `-p 4000:4000` with `--port 4000`.

### Running the Generator

Run the `generator` command with `data/` mounted, so that the generated world
is saved to your copy of the repository:

```
$ docker run --rm -v "$(pwd)/data:/src/data" muddyreality generator tiny --width 12 --room-width 50
```

To use `--water-snapshot`, create `snaps/` and mount it as well:

```
$ mkdir -p snaps
$ docker run --rm -v "$(pwd)/data:/src/data" -v "$(pwd)/snaps:/src/snaps" muddyreality generator snapshots --width 12 --water-snapshot
```

### Developing with Docker

To run your working copy of the code and data without rebuilding the image,
mount the whole repository over the copy in the image.  This works for the
server, the generator and `build.sh`:

```
$ docker run --rm -it -p 3000:3000 -v "$(pwd):/src" muddyreality
$ docker run --rm -v "$(pwd):/src" muddyreality generator tiny --width 12 --room-width 50
$ docker run --rm -v "$(pwd):/src" --entrypoint bash muddyreality build.sh
```

Changes take effect the next time a container starts.  The server doesn't pick
up changes while it's running, so stop it with `Ctrl-C` and start it again.
You only need to rebuild the image after changing `requirements.txt` or the
`Dockerfile`.

### Linux Hosts

On macOS, Docker Desktop makes the files that containers create in mounted
directories owned by you.  On Linux, containers run as root by default, so
generated worlds, saved accounts and Python's cache files will be owned by
root.  Run the container as your own user to avoid this:

```
$ docker run --rm -it -p 3000:3000 -v "$(pwd):/src" --user "$(id -u):$(id -g)" -e MPLCONFIGDIR=/tmp/matplotlib muddyreality
```

`MPLCONFIGDIR` gives matplotlib, which the generator uses, a writable settings
directory, since your user doesn't have a home directory in the container.

## Documentation

Further documentation on each component can be found in the relevant README
file.

- `generator`: [README](./generator/README.md)
- `game`: [README](./game/README.md)
