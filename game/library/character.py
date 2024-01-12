class CharacterLibrary:
    """
    A library containing behavior for acting on and interacting with Characters. 
    """

    def __init__(self, library, store):
        """
        Initialize the CharacterLibrary.

        Parameters
        ----------
        library:    Library
            The game library, allowing access to other model's behaviors.
        store:  Store
            The game store.
        """

        self.library = library
        self.store = store

    def kill(self, character):
        """
        Kill a character and send their player back to the account menu.
        
        Parameters
        ----------
        character:  Character
            The character to kill.
        
        Returns
        -------
        CharacterLibrary:   Returns `self` to allow chaining.
        """
        
        if character.player:
            character.player.status = character.player.STATUS_ACCOUNT
            character.player.account_state = "menu"
        return self

    def adjustSleep(self, character, amount):
        """
        Adjust a character's sleep reserve and execute any follow on effects.
        
        Parameters
        ----------
        character:  Character
            The character who's sleep we wish to adjust.
        amount: int
            The amount we want to adjust the character's sleep by.  Can be positive or negative.
        
        Returns
        -------
        boolean:    True if the adjustment succeeded, False otherwise. 
        """
        
        character.reserves.sleep += amount
        return True

    def adjustCalories(self, character, amount):
        """
        Adjust a character's calorie reserve and execute any follow on effects.

        Parameters
        ----------
        character:  Character
            The character who's calories we wish to adjust.
        amount: int
            The amount we want to adjust the character's calories by.  Can be positive or negative.

        Returns
        -------
        boolean:    True if the adjustment succeeded, False otherwise. 
        """

        character.reserves.calories += amount
        if character.reserves.calories < 0:
            # Reduce the character's stamina by the amount they are starving.
            # If the stamina reaches 0, the character dies.
            #
            # Given that we're dividing calories by max_calories, and
            # max_calories is the number of calories needed to survive a day,
            # this results in stamina effectively being the number of days a
            # character can survive without eating.
            character.stamina = character.max_stamina + (character.reserves.calories / character.reserves.max_calories)
            if character.stamina <= 0:
                self.kill(character)
        return True

    def adjustThirst(character, amount):
        """
        Adjust a character's thirst reserve and execute any follow on effects.
        
        Parameters
        ----------
        character:  Character
            The character who's thirst we wish to adjust.
        amount: int
            The amount we want to adjust the character's thirst by.  Can be positive or negative.
        
        Returns
        -------
        boolean:    True if the adjustment succeeded, False otherwise. 
        """

        if character.reserves.thirst > character.reserves.max_thirst:
            return False
        character.reserves.thirst += amount
        if character.reserves.thirst < 0:
            character.stamina = character.max_stamina + 4 * (character.reserves.thirst / character.reserves.max_thirst)
            if character.stamina <= 0:
                self.kill(character)
        return True

    def adjustWind(self, character, amount):
        """
        Adjust a character's wind reserve and execute any follow on effects.

        Parameters
        ----------
        character:  Character
            The character who's wind we wish to adjust.
        amount: int
            The amount we want to adjust the character's wind by.  Can be positive or negative.

        Returns
        -------
        boolean:    True if the adjustment succeeded, False otherwise. 
        """
        
        # Wind can't go negative.
        if self.reserves.wind + amount < 0:
            return False
        self.reserves.wind = min(self.reserves.wind + amount, self.reserves.max_wind)
        return True

    def adjustEnergy(self, character, amount):
        """
        Adjust a character's energy reserve and execute any follow on effects.
        
        Parameters
        ----------
        character:  Character
            The character who's energy we wish to adjust.
        amount: int
            The amount we want to adjust the character's energy by.  Can be positive or negative.
        
        Returns
        -------
        boolean:    True if the adjustment succeeded, False otherwise. 
        """
        
        # Energy can't go negative.
        if self.reserves.energy + amount < 0:
            return False
        self.reserves.energy = min(self.reserves.energy + amount, self.reserves.max_energy)
        return True

    def calculateReserves(self, character):
        """
        Calculate the correct values for the user's max reserves based upon their attributes.

        Parameters
        ----------
        character:  Character
            The character who's reserves we want to calculate.
        """

        self.reserves.max_energy = self.attributes.stamina * 1000
        if self.reserves.energy >= self.reserves.max_energy:
            self.reserves.energy = self.reserves.max_energy

        self.reserves.max_wind = self.attributes.stamina * 3
        if self.reserves.wind >= self.reserves.max_wind:
            self.reserves.wind = self.reserves.max_wind