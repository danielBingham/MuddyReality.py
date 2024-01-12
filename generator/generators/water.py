###############################################################################
#
# Water generation algorithm.  Used to place accurate rivers, streams, and
# lakes in the world.
#
# Algorithm from here: https://hal.inria.fr/inria-00402079/document 
#
###############################################################################

import math
import numpy as np
import scipy as sp
import imageio

import generator.utils.util as util
import generator.utils.snapshot as snapshot


def generateWater(world):
    print("Generating water for world %s..." % world.name)

    # Print debugging output.
    debug = False 
    take_snapshot = True 

    terrain = np.array(world.terrain) * 2000

    # Grid dimension constants
    dim = world.width 
    shape = [world.width] * 2
    cell_width = world.room_width 
    cell_area = cell_width ** 2

    # Area of the pipes between the cells, in meters^2.
    pipe_area = cell_width*cell_width

    # Length of the pipes between the cells, in meters.
    pipe_length = cell_width 

    # Time helper values.
    seconds_per_year = 365*24*60*60
    seconds_per_day = 24*60*60
    seconds_per_hour = 60*60
    seconds_per_minute = 60

    # The length of an iteration in seconds.
    iteration_length = seconds_per_day

    # The total time to simulate in seconds.
    simulation_time = 3 * seconds_per_year 

    # The number of iterations to run.  Each iteration represents a delta-t of
    # iteration_length.  
    iterations = math.floor(simulation_time / iteration_length)

    # Minimum number of iterations to allow the simulation to reach the edges
    # of the map.
    if iterations < 1.4 * dim:
        iterations = math.floor(1.4 * dim)

    # The rate at which water height increases due to rain, measured in meters/s. 
    #
    # Initialized to the average value for Britain.
    rain_rate = 0.000000042

    # The rate at which water height decreases due to evaporation, measured in meters/s.
    #
    # Initialized to the average value for Britain.
    evaporation_rate = 0.00000003 

    # The amount water height is increased by rain per iteration in meters.
    rain_per_iteration = rain_rate * iteration_length

    # The amount water height is decreased by evaporation per iteration in meters.
    evaporation_per_iteration = evaporation_rate * iteration_length

    # In meters/s^2
    gravity_constant = 9.8

    # The water height in meters.  Represents the height of water on any
    # individual point on the map, equivalent to the value used to measure rain
    # accumulation.  Note: This is in meters, not meters^3.  This represents
    # water height, not water volume.
    water = np.ones_like(terrain) * world.initial_water 

    start_water = np.sum(water)

    # The flux of water between each grid cell and it's neighbors.  (Flux_north
    # is between each grid cell and its northern neighbor and so on).
    flux_north = np.zeros_like(terrain)
    flux_north_east = np.zeros_like(terrain)
    flux_east = np.zeros_like(terrain)
    flux_south_east = np.zeros_like(terrain)
    flux_south = np.zeros_like(terrain)
    flux_south_west = np.zeros_like(terrain)
    flux_west = np.zeros_like(terrain)
    flux_north_west = np.zeros_like(terrain)

    # The water velocity.
    velocity = np.zeros_like(terrain)

    if debug:
        print("\n\n Terrain: ")
        print(terrain)

    for iteration in range(0, iterations):
        print('Water days (iterations): %d / %d' % (iteration + 1, iterations))

        if iteration < iterations:
            # Add water through precipitation. 
            water += rain_per_iteration

        if debug:
            print("\n\nWater: ")
            print(water)
            print("\n\nStart_water: ")
            print(start_water)
            print("\n\nTotal_water: ")
            print(np.sum(water))

        terrain_water = terrain + water

        # Calculate the hydrostatic flux from each cell to each of its neighbors.

        # First we need to calculate the height difference between this cell
        # and its neighbors.  The height difference in this case includes both
        # the height of the terrain and the height of the water.
        #
        # To calculate the height difference between a cell and its neighbors,
        # we need to keep our coordinate system in mind:
        #
        #   nw(x-1,y-1)   n(x,y-1)   ne(x+1, y-1)
        #   w (x-1, y)    C(x.y)     e (x+1, y)
        #   sw(x-1, y+1)  s(x, y-1)  se(x+1, y+1)
        #
        # We're going to calculate the delta arrays by subtracting the
        # `terrain_water` array rolled in a particular direction from itself.
        # The rolls are a little counter intuitive. So we'll explain one:
        #
        #   delta_east = w(x,y) - w(x+1,y) = w(C) - w(e)
        #
        # To achieve that on an array level using rolls, we actually need to
        # roll the array west using `np.roll(terrain_water, -1, axis=1)`
        #
        # Which gives us:
        #
        #   nw  n   ne      n   ne  nw
        #   w   C   e   -   C   e   w 
        #   sw  s   se      s   se  sw
        #
        # `delta_east = terrain_water - np.roll(terrain_water, -1, axis=1)`

        # delta_height_north = w(c) - w(n) = w(x,y) - w(x,y-1) 
        #
        # nw    n   ne      sw  s   se
        # w     C   e   -   nw  n   ne
        # sw    s   se      w   C   e
        delta_height_north = terrain_water - np.roll(terrain_water, 1, axis=0)

        # delta_height_east = w(c) - w(e) = w(x,y) - w(x+1,y) 
        #
        # nw    n   ne      n   ne  nw 
        # w     C   e   -   C   e   w 
        # sw    s   se      s   se  sw 
        delta_height_east = terrain_water - np.roll(terrain_water, -1, axis=1)

        # delta_height_south = w(c) - w(s) = w(x,y) - w(x, y+1)
        #
        # nw    n   ne      w   C   e 
        # w     C   e   -   sw  s   se 
        # sw    s   se      nw  n   ne 
        delta_height_south = terrain_water - np.roll(terrain_water, -1, axis=0)

        # delta_height_west = w(c) - w(w) = w(x,y) - w(x-1, y)
        #
        # nw    n   ne      ne  nw  n 
        # w     C   e   -   e   w   C 
        # sw    s   se      se  sw  s 
        delta_height_west = terrain_water - np.roll(terrain_water, 1, axis=1)

        # To get the the corners, we just combine the rolls for each direction appropriately.
        delta_height_north_east = terrain_water - np.roll(terrain_water, (1, -1), axis=(0, 1))
        delta_height_south_east = terrain_water - np.roll(terrain_water, (-1, -1), axis=(0, 1))
        delta_height_south_west = terrain_water - np.roll(terrain_water, (-1, 1), axis=(0, 1))
        delta_height_north_west = terrain_water - np.roll(terrain_water, (1, 1), axis=(0, 1))

        # The flux out from C in each direction, is then calculated using the delta arrays.
        flux_north = np.maximum(0, flux_north + iteration_length * pipe_area * (gravity_constant * delta_height_north) / pipe_length)
        flux_north_east = np.maximum(0, flux_north_east + iteration_length * pipe_area * (gravity_constant * delta_height_north_east) / pipe_length)
        flux_east = np.maximum(0, flux_east + iteration_length * pipe_area * (gravity_constant * delta_height_east) / pipe_length)
        flux_south_east = np.maximum(0, flux_south_east + iteration_length * pipe_area * (gravity_constant * delta_height_south_east) / pipe_length)
        flux_south = np.maximum(0, flux_south + iteration_length * pipe_area * (gravity_constant * delta_height_south) / pipe_length)
        flux_south_west = np.maximum(0, flux_south_west + iteration_length * pipe_area * (gravity_constant * delta_height_south_west) / pipe_length)
        flux_west = np.maximum(0, flux_west + iteration_length * pipe_area * (gravity_constant * delta_height_west) / pipe_length)
        flux_north_west = np.maximum(0, flux_north_west + iteration_length * pipe_area * (gravity_constant * delta_height_north_west) / pipe_length)

        # Normalize the flux to the amount of water in each cell.
        total_flux = flux_north + flux_north_east + flux_east + flux_south_east + flux_south + flux_south_west + flux_west + flux_north_west
        scaling_factor = np.select([total_flux == 0, total_flux != 0], [np.ones_like(total_flux), water * (pipe_length*pipe_length) / (total_flux * iteration_length)])

        # Multiply by the scaling factor.
        #
        # NOTE: We also add a friction factor here.  The division by 2 is not
        # present in the original algorithm, but is necessary to prevent the
        # water from sloshing.  Without it, you can end up with a checkerboard
        # pattern, where all the water in one cell slams into its neighboring
        # cells in one iteration.  That will leave the central cell empty and
        # the neighboring cells with enough water to repeat the pattern with
        # *their* neighbors, eventually filling the whole grid with an
        # alternating checkerboard.  Limiting the flux to half the water
        # available in the cell prevents the checkerboard from happening,
        # though the water will still slosh randomly in flat areas.
        #
        # TODO Add an increasing energy loss term to force water to settle once
        # it fills a depression.  With the current algorithm, it will slosh
        # around indefinitely.
        flux_north = scaling_factor * flux_north / 2
        flux_north_east = scaling_factor * flux_north_east / 2
        flux_east = scaling_factor * flux_east / 2
        flux_south_east = scaling_factor * flux_south_east / 2
        flux_south = scaling_factor * flux_south / 2
        flux_south_west = scaling_factor * flux_south_west / 2
        flux_west = scaling_factor * flux_west / 2
        flux_north_west = scaling_factor * flux_north_west / 2

        # Create the water delta by subtracting the flux out and then adding the flux in.

        # For the flux out, we just sum the fluxes in all directions.  Each
        # directional flux array, `f_d(x,y)` represents the flux out for
        # `(x,y)` in direction`d`.
        flux_out = (
            flux_north 
            + flux_north_east 
            + flux_east 
            + flux_south_east 
            + flux_south 
            + flux_south_west 
            + flux_west 
            + flux_north_west
        )
        deltaWater = - iteration_length / cell_area * (flux_out)

        # Add the flux in
        #
        # To calculate the flux in, we want to add the flux out in the
        # appropriate direction for each of the neighboring cells. The flux we
        # want to add will be the one in the opposite direction from the
        # direction the neighbor lies in.  So for the cell to the east, we'll
        # add the flux_west.  For the cell to the west, we'll add the
        # flux_east.
        #
        # This means we need to roll them in the opposite directions we did for
        # calculating the delta_height.  So to calculate the delta_height_east
        # we rolled the array so that the height in the square immediately east
        # of C was in C.  But when adding the flux_east to the total flux_in,
        # we actually want the flux_ east for the square to the west of C.
        # Because the water flowing out of that square to the east is the water
        # that will flow into C from the west.
        #
        # So we want to roll flux_east such that:
        #
        # nw    n   ne      ne  nw  n
        # w     c   e   ->  e   w   c 
        # sw    s   se      se  sw  s 
        flux_in = (
            np.roll(flux_north, -1, axis=0) 
            + np.roll(flux_north_east, (-1, 1), axis=(0, 1))
            + np.roll(flux_east, 1, axis=1) 
            + np.roll(flux_south_east, (1, 1), axis=(0, 1))
            + np.roll(flux_south, 1, axis=0) 
            + np.roll(flux_south_west, (1, -1), axis=(0, 1))
            + np.roll(flux_west, -1, axis=1)
            + np.roll(flux_north_west, (-1, -1), axis=(0, 1))
       )
        deltaWater += iteration_length / cell_area * (flux_in)

        if debug:
            print("\n\nTerrain+Water: ")
            print(terrain_water)

            print("\n\n deltaWater: ")
            print(deltaWater)

        water += deltaWater

        # Want cannot go negative.  If it does, just zero it out.  We're mostly
        # removing precision issue with this.  For some reason, the arrays will
        # often end up with negative values to the power of 10^-16 when they
        # should be zeroed out.
        water = np.maximum(water, np.zeros_like(water))

        if debug:
            print("\n\nNew Water: ")
            print(water)

        # Apply evaporation
        water = np.maximum(water - evaporation_per_iteration, np.zeros_like(water))

        if take_snapshot:
            snapshot.snapWater(water, 'snaps/' + str(iteration) + '.png')

        # Compute the final water speeds.  We don't actually need the direction of
        # the velocity, just the magnitude, since we're just going to use this to
        # determine whether a room should be a lake or pond room vs a stream or
        # river room.
        #
        # We only want to do this on the final iteration.  In the erosion sim,
        # the velocity is needed to calculate sediment collection and
        # deposition values on each iteration.  But we're using it for a
        # different purpose here.  We only need the last one.
        #
        # Becuse we only need the speed, not the direction, we're going to
        # first collapse the 8 flux directions down to x and y.  Then we'll
        # take the magnitude to get the speed.
        # if iteration == iterations-1:
        #    velocity_x = (np.roll(flux_east, -1, axis=1) - flux_west + flux_east - np.roll(flux_west, 1, axis=1)) / (2 * pipe_length * water) 
        #        + (np.roll(flux_north_east, (1, 1), (0, 1)) - flux_south_west) - (np.roll(
        #    velocity_y = (np.roll(flux_north, 1, 0) - flux_south)

    if take_snapshot:
        images = []
        for iteration in range(0, iterations):
            images.append(imageio.imread('snaps/' + str(iteration) + '.png'))
        imageio.mimsave('snaps/animation.gif', images)

    world.water = water 
