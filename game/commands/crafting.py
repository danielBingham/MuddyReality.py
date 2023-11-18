from interpreter.command import Command
import services.equipment as equipment

class Craft(Command):
    'Create a new item from materials in inventory or room.'

    def __init__(self, library):
        Command.__init__(self, library)
        self.crafting = CraftingService(library)

    def execute(self, player, arguments):
        """
            > craft <item> with <material>, <material>, ...
        
            Craft <item> from the listed materials, if possible.  
        """

        if not arguments:
            player.write("You can't craft nothing!")
            return

        # Split the arguments on white space.
        splitArguments = arguments.split('with')

        # Keywords describing the item to be crafted
        craftKeywords = splitArguments[0]

        # Keywords describing the materials to craft the item.
        materialKeywords = splitArguments[1].split(',')

        materials = []
        for keyword in materialKeywords:
            material = equipment.findItemInInventory(player, keyword)A
            if material:
                materials.append(material)
            else:
                player.write("Couldn't find " + keyword + " in your inventory.")

        # Get the craft target assuming the keyword is the whole name.
        craftTarget = self.library.items.getById(craftKeywords)
        for requiredMaterial in craftTarget.traits["Craftable"].requiredMaterials:
            for material in materials:
                

        # Confirm we have all the materials we need to craft the target.


        # Get an array of materials, first that matches the keyword in the
        # inventory.  If not found in the inventory, first that matches the
        # keyword in the room.

        # Get all items that match the craft keyword.  Then select the first
        # for which the requirements are met.






