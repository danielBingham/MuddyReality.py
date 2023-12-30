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
    take_snapshot = False 

    terrain = np.array(world.terrain) * 2000

    # Grid dimension constants
    dim = world.width 
    shape = [ world.width ] * 2
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
    # water = np.zeros_like(terrain)
    water = np.ones_like(terrain) * world.initial_water 
    #water = np.zeros_like(terrain)
    #mid = math.floor(len(water) / 2)
    #for x in range(len(water[mid])):
    #    water[math.floor(len(water)/2)][x] = 4

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
            # Add precipitation. This is done by via simple uniform random distribution,
            # although other models use a raindrop model
            water += rain_per_iteration

        if debug:
            print("\n\nWater: ")
            print(water)
            print("\n\nStart_water: ")
            print(start_water)
            print("\n\nTotal_water: ")
            print(np.sum(water))

        terrain_water = terrain + water

        #if debug:
        #    print("\n\nTerrain+Water: ")
        #    print(terrain_water)

        # Calculate the hydrostatic flux from each cell to each of its neighbors.
        delta_height_north = terrain_water - np.roll(terrain_water, 1, 0)
        delta_height_north_east = terrain_water - np.roll(terrain_water, (1, 1), (0,1))
        delta_height_east = terrain_water - np.roll(terrain_water, 1, 1)
        delta_height_south_east = terrain_water - np.roll(terrain_water, (-1, 1), (0, 1))
        delta_height_south = terrain_water - np.roll(terrain_water, -1, 0)
        delta_height_south_west = terrain_water - np.roll(terrain_water, (-1, -1), (0, 1))
        delta_height_west = terrain_water - np.roll(terrain_water, -1, 1)
        delta_height_north_west = terrain_water - np.roll(terrain_water, (1, -1), (0, 1))

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
        
        #if debug:
        #    print("\n\nScaling factor: ")
        #    print(scaling_factor)

        flux_north = scaling_factor * flux_north / 2
        flux_north_east = scaling_factor * flux_north_east / 2
        flux_east = scaling_factor * flux_east / 2
        flux_south_east = scaling_factor * flux_south_east / 2
        flux_south = scaling_factor * flux_south / 2
        flux_south_west = scaling_factor * flux_south_west / 2
        flux_west = scaling_factor * flux_west / 2
        flux_north_west = scaling_factor * flux_north_west / 2

        #flux_north = flux_north / total_flux * (water/2)
        #flux_south = flux_south / total_flux * (water/2)
        #flux_east = flux_east / total_flux * (water/2)
        #flux_west = flux_west / total_flux * (water/2)

        deltaWater = - iteration_length  / cell_area * (flux_north + flux_north_east + flux_east + flux_south_east + flux_south + flux_south_west + flux_west + flux_north_west)
        deltaWater += iteration_length  / cell_area * (
            np.roll(flux_north, -1, 0) 
            + np.roll(flux_north_east, (-1, -1), (0, 1))
            + np.roll(flux_east, -1, 1) 
            + np.roll(flux_south_east, (1, -1), (0, 1))
            + np.roll(flux_south, 1, 0) 
            + np.roll(flux_south_west, (1, 1), (0, 1))
            + np.roll(flux_west, 1, 1)
            + np.roll(flux_north_west, (-1, 1), (0, 1))
        )

        if debug:
            print("\n\nTerrain+Water: ")
            print(terrain_water)

            print("\n\n deltaWater: ")
            print(deltaWater)

        water += deltaWater
        water = np.maximum(water, np.zeros_like(water))
       
        if debug:
            print("\n\nNew Water: ")
            print(water)

        # Apply evaporation
        water = np.maximum(water - evaporation_per_iteration, np.zeros_like(water))

        if take_snapshot:
            snapshot.snapWater(water, 'snaps/' + str(iteration) + '.png')

    if take_snapshot:
        images = []
        for iteration in range(0, iterations):
            images.append(imageio.imread('snaps/' + str(iteration) + '.png'))
        imageio.mimsave('snaps/animation.gif', images)

    world.water = water 
