# MuddyReality.py

A multi-user dungeon written in python with a focus on realism.  Best used to
create open world, survival, crafting MUDs.

Includes two main pieces: the game itself and world generators.   The game is
stored in `game` and run with `main.py`.  The generators are stored in
`generator` and run with `generate.py`.  They both work with data stored in
`data`.

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

## Running

### Game

To run the game, execute the `main.py` file in the top level directory.

```
$ python3 main.py
```

The `main.py` file takes two optional arguments:

* `--world [name]`: Run the game with the world named by `[name]`.  `[name]` must be a directory under `data/worlds/` that contains a `world.json` file and a `rooms/` directory with rooms defined in `json`.
* `--port [port]`: Run the game on `[port]`.

```
$ python3 --world test --port 3000
```

### Generator

To generate worlds for the game, execute the `generate.py` file in the top level directory.

```
$ python3 generate.py [name]
```

`[name]` is the only required argument, and represents the name of the world.
This is the same name that will be used with `main.py` to run the game.

The generator takes a number of optional arguments that can be used to control
how the world is generated.

* `--width [width]`: Set the width of the game world in number of rooms.  Takes an integer. Defaults to `100` rooms.
* `--room-width [width]`: Set the width of a room in the game world in number of meters.  This will impact the simulations used to generate the world as well as certain aspects of how resources are used in the game. Takes an integer. Defaults to `100` meters.
* `--initial-water [height]`: Set the initial height of water across the world in meters.  Used to when generating water in the world.  The total volume of water in the world will be `height * (width * room_width)^2`.  Defaults to `30` meters.
* `--heights-only`: A boolean flag that tells the generator to only run the heightmap portion of the generation.
* `--water-only`: A boolean flag telling the generator to only run the water placement portion of the generation.  The heightmap portion must have already been run for world `[name]`.
* `--biomes-only`: A boolean flag telling the generator to only run the biome succession portion of the generation.  The heightmap and water portions must have already been run for world `[name]`.
* `--rooms-only`: A boolean flag telling the generator to only run the room generation portion of the generation.  The preceding portions (heightmap, water, biomes) must have already been run.
* `--regenerate`: A boolean flag telling teh generator to regenerate the world instead of reusing any previously generated portions.

## Documentation

Further documentation on each component can be found in the relevant README
file.

- `generator`: [README](./generator/README.md)
- `game`: [README](./game/README.md)
