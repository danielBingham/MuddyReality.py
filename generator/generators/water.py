###############################################################################
#
# Water generation algorithm.  Used to place accurate rivers, streams, and
# lakes in the world.
#
# Algorithm from here: https://hal.inria.fr/inria-00402079/document 
#
###############################################################################

from generator.library.dandrino_water import DandrinoWater 
from generator.library.inria_water import InriaWater

class WaterGenerator:

    def __init__(self, world, arguments):
        self.world = world
        self.arguments = arguments

        self.algorithm = 'inria'
        if arguments.water__algorithm:
            self.algorithm = arguments.water__algorithm


    def generate(self):
        print("Generating water for world %s..." % self.world.name)

        if self.algorithm == 'inria':
            generator = InriaWater(self.world, self.arguments) 
            generator.generate()
        elif self.algorithm == 'dandrino':
            generator = DandrinoWater(self.world, self.arguments)
            generator.generate()

