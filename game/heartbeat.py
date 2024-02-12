class Heartbeat:

    def __init__(self, store, library):
        self.store = store
        self.library = library


    def heartbeat(self):
        """
        A method called on every loop that can be used for actions that need to
        take place every so many loops.  Used to control autonomous timing in
        the game world.

        Parameters
        ----------
        loop_counter:   integer
            An integer loop counter recording which iteration of the game loop
            this is.  Reset to 0 when it hits max_integer.

        Returns
        -------
        void
        """

        time = self.store.world.time

        # Save characters once per game hour, real life minute.
        if time.loop % time.loops_an_hour == 0:
            self.saveCharacters()

        # Advance any actions or action timers.
        if time.loop % time.loops_a_minute == 0:
            self.advanceActions()

        # Do reserves calculations once per game minute.
        if time.loop % time.loops_a_minute == 0:
            self.calculateReserves()

        # Do sleep calculations once per game hour.
        if time.loop % time.loops_an_hour == 0:
            self.calculateSleep()


    def saveCharacters(self):
        """
        Save all the characters currently playing the game.
        """

        for player in self.store.players:
            if not player.character:
                continue
            self.store.saveCharacter(player.character)


    def advanceActions(self):
        """
        Advance any player actions currently in progress.
        """

        for player in self.store.players:
            if not player.character:
                continue
            if not player.character.action:
                continue

            player.character.action_time -= 1
            if player.character.action_time > 0:
                player.prompt.is_off = True
                player.write(".", wrap=False)
                player.character.action.step(player)
            else:
                player.character.action.finish(player)
                player.character.action = None
                player.character.action_data = {}
                player.character.action_time = 0
                player.prompt.is_off = False

    def calculateReserves(self):
        """
        Calculate any changes in character reserves (aside from sleep).
        """

        for player in self.store.players:
            character = player.character
            if not character:
                continue

            self.library.character.adjustCalories(character, -2)
            self.library.character.adjustThirst(character, -2)

            if character.position == character.POSITION_STANDING:
                self.library.character.adjustWind(character, 3)
            elif character.position == character.POSITION_RESTING:
                self.library.character.adjustWind(character, 5)
                self.library.character.adjustEnergy(character, 100)

    def calculateSleep(self):
        """
        Do sleep calculations. 
        
        The player's tiredness is self.stored as a 'sleep reserve' under
        `character.reserves.sleep`.  It's self.stored as an integer
        representing the number of hours they can stay awake without suffering
        any kind of tiredness penalty.  The reserve is reduced by `1` for each
        hour the character stays awake and increases by `2` for each hour spent
        sleeping, roughly matching a schedule with 8 hours of sleep and 16
        hours awake.
        
        Once the sleep reserve is drained below zero the player starts to
        suffer tiredness penalties.  The primary penalty is a risk of falling
        asleep that increases steadily up to 248 hours spent awake past the 16
        hours rested (16+248 = 264), the record number of hours any human has
        remained awake.
        """

        for player in self.store.players:
            if not player.character:
                continue

            character = player.character

            # If they're awake, then get more tired.
            if character.position != character.POSITION_SLEEPING:
                self.library.character.adjustSleep(character, -1)

            # If they're asleep they recover.
            elif character.position == character.POSITION_SLEEPING:
                self.library.character.adjustSleep(character, 2)

                # It takes two full nights of sleep to recover all of your energy.
                self.library.character.adjustEnergy(character, 625)
