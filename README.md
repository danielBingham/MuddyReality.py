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
