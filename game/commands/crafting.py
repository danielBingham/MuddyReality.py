import math

from game.interpreters.command.command import Command


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
            player.write("Craft what with what?")
            return

        # Split the arguments on "with" to differentiate the craft target from
        # the materials.
        splitArguments = arguments.split('with')

        if len(splitArguments) != 2:
            player.write("What do you want to craft with?")
            return

        # Keywords describing the item to be crafted
        craftKeywords = splitArguments[0].strip()

        # Get the craft target assuming the keyword is the whole name.
        craftTarget = self.store.items.getById(craftKeywords)

        if not craftTarget:
            player.write("%s is not something you can craft." % craftKeywords.title())
            return

        if "Craftable" not in craftTarget.traits:
            player.write("%s is not something you can craft." % craftKeywords.title())
            return

        # Keywords describing the materials to craft the item.
        if ',' in splitArguments[1]:
            materialKeywords = splitArguments[1].split(',')
            materialKeywords[:] = [keyword.strip() for keyword in materialKeywords]
        else:
            materialKeywords = [splitArguments[1].strip()]

        materials = []
        for keyword in materialKeywords:
            material = self.library.item.findItemByKeywords(player.character.inventory, keyword)
            if material:
                materials.append(material)
            else:
                player.write("Couldn't find '%s' in your inventory." % keyword)

        # Determine whether we have the materials necessary to craft the target.
        matchedMaterials = [] 
        for requiredMaterial in craftTarget.traits["Craftable"].requiredMaterials:
            for material in materials:
                if "Material" in material.traits \
                        and requiredMaterial.type in material.traits["Material"].types:
                    matchedMaterials.append(material)
                    break

        if len(matchedMaterials) != len(craftTarget.traits["Craftable"].requiredMaterials):
            player.write("You don't have all the materials needed to craft %s." % craftTarget.name)
            return

        # Remove the materials we're planning to use from the list.
        for matchedMaterial in matchedMaterials:
            materials.remove(matchedMaterial)

        # Confirm we have all the tools we need to craft it.
        matchedTools = []
        for requiredTool in craftTarget.traits["Craftable"].requiredTools:
            # We're using 'material' here because the materials list will
            # contain both the materials needed and the tools needed.
            for material in materials:
                if "Tool" in material.traits \
                        and requiredTool == material.traits["Tool"].type:
                    matchedTools.append(material)
                    break

        if len(matchedTools) != len(craftTarget.traits["Craftable"].requiredTools):
            player.write("You don't have all the tools needed to craft %s." % craftTarget.name)
            return

        # Clone the craft target.
        crafted = self.store.items.instance(craftTarget.getId())

        # Remove the materials from the inventory.
        for matchedMaterial in matchedMaterials:
            player.character.inventory.remove(matchedMaterial)

        # Add the craft target to the inventory.
        player.character.inventory.append(crafted)

        # Success message.
        player.write("You craft %s." % crafted.name)
        self.library.room.writeToRoom(player.character, "%s crafts %s." % (player.character.name.title(), crafted.name))


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

        calorie_cost_per_step = math.floor(item_harvest.calories / item_harvest.time)
        player.character.reserves.calories -= calorie_cost_per_step 

    def cancel(self, player):
        self.finish(player, True)

    def finish(self, player, cancelled=False):
        item = player.character.action_data['harvesting']
        in_inventory = player.character.action_data['in_inventory']
        harvest = item.traits["Harvestable"]

        results = ""
        for product in harvest.products:
            amount = product.amount
            if cancelled:
                amount = math.floor(amount * ((harvest.time - player.character.action_time) / harvest.time))
            if amount <= 0:
                continue

            if len(results) > 0:
                results += ", "
            results += str(amount) + " " + product.product

            for instance in range(0, amount): 
                productItem = self.store.items.instance(product.product)
                player.character.inventory.append(productItem)

        if len(results) == 0:
            player.write("\nYou didn't harvest long enough to produce anything.")
            return


        if harvest.consumed:
            if in_inventory:
                player.character.inventory.remove(item)
            else:
                player.character.room.items.remove(item)
        elif harvest.replaced_with:
            itemId = harvest.replaced_with
            if in_inventory:
                player.character.inventory.remove(item)
                player.character.inventory.append(self.store.items.instance(itemId))
            else:
                player.character.room.items.remove(item)
                player.character.room.items.append(self.store.items.instance(itemId))
        else:
            harvest.harvested = True

        player.write("\nYou %s %s from %s." % (harvest.action, results, item.description))
        self.library.room.writeToRoom(player.character, 
                                      "%s %s from %s." %
                                      (player.character.name, harvest.action, item.description))

    def execute(self, player, arguments):
        if player.character.position == player.character.POSITION_SLEEPING:
            player.write("You can't harvest in your sleep.")
            return

        if not arguments:
            player.write("Harvest what?")
            return

        item = self.library.item.findItemByKeywords(player.character.inventory, arguments)
        in_inventory = True
        if not item:
            item = self.library.item.findItemByKeywords(player.character.room.items, arguments)
            in_inventory = False

        if not item:
            player.write("You can't find a '%s' to harvest." % arguments)
            return

        if "Harvestable" not in item.traits:
            player.write("You can't harvest %s." % item.description)
            return

        if item.traits["Harvestable"].harvested:
            player.write("%s has already been harvested.  There's nothing left!" % item.description)
            return

        player.write("You begin to harvest %s." % item.description)

        player.character.action = self
        player.character.action_time = item.traits["Harvestable"].time
        player.character.action_data = {
            "harvesting": item,
            "in_inventory": in_inventory
        }



