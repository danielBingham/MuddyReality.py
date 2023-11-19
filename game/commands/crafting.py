from interpreter.command import Command
import services.equipment as equipment
import services.environment as environment

class Craft(Command):
    'Create a new item from materials in inventory or room.'

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
            material = equipment.findItemInInventory(player, keyword)
            if material:
                materials.append(material)
            else:
                player.write("Couldn't find " + keyword + " in your inventory.")

        # Get the craft target assuming the keyword is the whole name.
        craftTarget = self.library.items.getById(craftKeywords)
      
        # Determine whether we have the materials necessary to craft the target.
        matchedMaterials = [] 
        for requiredMaterial in craftTarget.traits["Craftable"].requiredMaterials:
            for material in materials:
                if "Material" in material.traits \
                        and requiredMaterial.type in material.traits["Material"].types:
                    matchedMaterials.append(material)
                    break

        if len(matchedMaterials) != len(craftTarget.traits["Craftable"].requiredMaterials):
            player.write("You don't have all the materials needed to craft " + craftTarget.name)
            return

        # Remove the materials we're planning to use from the list.
        for matchedMaterial in matchedMaterials:
            materials.remove(matchedMaterial)

        # Confirm we have all the tools we need to craft it.
        matchedTools = []
        for requiredTool in craftTarget.traits["Craftable"].requiredTools:
            for material in materials:
                if "Tool" in material.traits \
                        and requiredTool == material.traits["Tool"].type:
                    matchedTools.append(material)
                    break

        if len(matchedTools) != len(craftTarget.traits["Craftable"].requiredTools):
            player.write("You don't have all the tools needed to craft " + craftTarget.name)
            return


        # Clone the craft target.
        crafted = self.library.items.instance(craftTarget.getId())

        # Remove the materials from the inventory.
        for matchedMaterial in matchedMaterials:
            player.character.inventory.remove(matchedMaterial)

        # Add the craft target to the inventory.
        player.character.inventory.append(crafted)

        # Success message.
        player.write("You craft " + crafted.name)
        environment.writeToRoom(player, player.character.name + " crafts " + crafted.name)







