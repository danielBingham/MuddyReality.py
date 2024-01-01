import math

from game.interpreters.command import Command
import game.library.environment as environment
import game.library.items as ItemLibrary

class Craft(Command):
    'Create a new item from materials in inventory or room.'

    def describe(self):
        return "craft - create new items from a set of materials"

    def help(self):
        return """
craft [target] with [op:tool], [op:material], [op:material], [op:etc...]

Attempt to craft a material or tool with materials or tools.  If the [target] can be crafted with the listed [materials] and [tools] and  all materials and tools are in the character's inventory, then a new [target] will be created.  Materials will be used up to create the [target], but tools will remain in the character's inventory.
        """

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't craft in your sleep.")
            return

        if not arguments:
            player.write("You can't craft nothing!")
            return

        # Split the arguments on white space.
        splitArguments = arguments.split('with')

        if len(splitArguments) != 2:
            player.write("What do you want to craft with?")
            return

        # Keywords describing the item to be crafted
        craftKeywords = splitArguments[0].strip()

        # Keywords describing the materials to craft the item.
        materialKeywords = splitArguments[1].split(',')
        materialKeywords[:] = [keyword.strip() for keyword in materialKeywords]

        materials = []
        for keyword in materialKeywords:
            material = ItemLibrary.findItemByKeywords(player.character.inventory, keyword)
            if material:
                materials.append(material)
            else:
                player.write("Couldn't find " + keyword + " in your inventory.")

        # Get the craft target assuming the keyword is the whole name.
        craftTarget = self.store.items.getById(craftKeywords)

        if not craftTarget:
            player.write(craftKeywords + " is not something you can craft.")
            return
      
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
        crafted = self.store.items.instance(craftTarget.getId())

        # Remove the materials from the inventory.
        for matchedMaterial in matchedMaterials:
            player.character.inventory.remove(matchedMaterial)

        # Add the craft target to the inventory.
        player.character.inventory.append(crafted)

        # Success message.
        player.write("You craft " + crafted.name)
        environment.writeToRoom(player.character, player.character.title + " crafts " + crafted.name)

class Harvest(Command):
    'Harvest materials.'

    def describe(self):
        return "harvest - harvest materials"

    def help(self):
        return """
harvest [target]

Harvest materials from an object in your environment.  The object can be either in your inventory or in the room your character currently occupies.
        """

    def step(self, player):
        item = player.character.action_data['harvesting']
        item_harvest = item.traits["Harvestable"]

        player.character.reserves.calories -= math.floor(item_harvest.calories / item_harvest.time)
        

    def finish(self, player):
        item = player.character.action_data['harvesting']
        in_inventory = player.character.action_data['in_inventory']

        results = ""
        for product in item.traits["Harvestable"].products:
            if len(results) > 0:
                results += ", "
            results += str(product.amount) + " " + product.product
           
            for instance in range(0, product.amount): 
                productItem = self.store.items.instance(product.product)
                player.character.inventory.append(productItem)

        if item.traits["Harvestable"].consumed:
            if in_inventory:
                player.character.inventory.remove(item)
            else:
                player.character.room.items.remove(item)
        elif item.traits["Harvestable"].replaced_with:
            itemId = item.traits["Harvestable"].replaced_with
            if in_inventory:
                player.character.inventory.remove(item)
                player.character.inventory.append(self.store.items.instance(itemId))
            else:
                player.character.room.items.remove(item)
                player.character.room.items.append(self.store.items.instance(itemId))
        else:
            item.traits["Harvestable"].harvested = True

        player.write("You " + item.traits["Harvestable"].action + " " + results + " from " + item.description + ".")
        environment.writeToRoom(player.character, player.character.name + " " + item.traits["Harvestable"].action + " from " + item.description + ".")


    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't harvest in your sleep.")
            return

        if not arguments:
            player.write("Harvest what?")
            return
        
        item = ItemLibrary.findItemByKeywords(player.character.inventory, arguments)
        in_inventory = True
        if not item:
            item = ItemLibrary.findItemByKeywords(player.character.room.items, arguments)
            in_inventory = False

        if not item:
            player.write("You can't find a " + arguments + " to harvest.")
            return

        if "Harvestable" not in item.traits:
            player.write("You can't harvest " + item.description)
            return

        player.character.action = self
        player.character.action_time = item.traits["Harvestable"].time
        player.character.action_data = {
            "harvesting": item,
            "in_inventory": in_inventory
        }



