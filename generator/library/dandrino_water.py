import numpy as np
import imageio

import generator.utils.util as util
import generator.utils.snapshot as snapshot

class DandrioWater:

    def __init__(self, world, arguments):
        self.world = world

        self.take_snapshot = False
        if arguments.water__snapshot:
            self.take_snapshot = True

        # Grid dimension constants
        self.dim = self.world.width
        self.shape = [ self.world.width ] * 2
        self.cell_width = self.world.room_width
        self.cell_area = self.cell_width ** 2

        # Water-related constants
        self.rain_rate = 0.0008 * self.cell_area 
        self.evaporation_rate = 0.0005 

        # Slope constants
        self.min_height_delta = 0.05
        self.repose_slope = 0.03
        self.gravity = 30.0
        # Unused?
        # gradient_sigma = 0.5

        # The numer of iterations is proportional to the grid dimension. This is to 
        # allow changes on one side of the grid to affect the other side.
        self.iterations = int(1.4 * self.dim)

    def generate(self):
        """
        :returns:   `void`
        """

        print("Generating water using dandrio's algorithm...")

        # terrain = world.terrain
        terrain = np.zeros_like(self.world.terrain)

        # The amount of water. Responsible for carrying sediment.
        water = np.zeros_like(terrain)

        # The water velocity.
        # velocity = np.zeros_like(terrain)

        for iteration in range(0, self.iterations):
            print('Water Iteration: %d / %d' % (iteration + 1, self.iterations))

            # Add precipitation. This is done by via simple uniform random distribution,
            # although other models use a raindrop model
            water += np.random.rand(*self.shape) * self.rain_rate

            # Compute the normalized gradient of the terrain height to determine where 
            # water and sediment will be moving.
            gradient = np.zeros_like(terrain, dtype='complex')
            gradient = util.simple_gradient(terrain)
            gradient = np.select([np.abs(gradient) < 1e-10],
                                 [np.exp(2j * np.pi * np.random.rand(*self.shape))],
                                 gradient)
            gradient /= np.abs(gradient)

            # Compute the difference between teh current height the height offset by
            # `gradient`.
            # neighbor_height = util.sample(terrain, -gradient)
            # height_delta = terrain - neighbor_height

            water = util.displace(water, gradient)

            # Update velocity
            # velocity = self.gravity * height_delta / self.cell_width

            # Apply evaporation
            water *= 1 - self.evaporation_rate
    
            if self.take_snapshot:
                snapshot.snapWater(water, 'snaps/' + str(iteration) + '.png')
       
        if self.take_snapshot:
            images = []
            for iteration in range(0, self.iterations):
                images.append(imageio.imread('snaps/' + str(iteration) + '.png'))
            imageio.mimsave('snaps/animation.gif', images)

        self.world.water = terrain
