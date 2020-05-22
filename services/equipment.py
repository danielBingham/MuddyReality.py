class EquipmentService:
    'Provides functions for handling equipment.'

    def wield(character, weapon):
        if MeleeWeapon not in weapon.uses:
            return False

        character.equipment['wield'] = weapon

        if character.player:
            character.player.write('You wield ' + weapon.name + '.')


