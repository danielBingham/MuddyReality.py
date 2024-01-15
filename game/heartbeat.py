import random 


class Heartbeat:

    def __init__(self, store, loops_a_second):
        self.store = store
        self.loops_a_second = loops_a_second

        self.game_minute = loops_a_second
        self.game_hour = 60 * self.game_minute
        self.game_day = 24 * self.game_hour


    def heartbeat(self, loop_counter):
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

        # Save characters once per game hour, real life minute.
        if loop_counter % self.game_hour == 0:
            self.saveCharacters()

        # Advance any actions or action timers.
        if loop_counter % self.game_minute == 0:
            self.advanceActions()

        # Do reserves calculations once per game minute.
        if loop_counter % self.game_minute == 0:
            self.calculateReserves()

        # Do sleep calculations once per game hour.
        if loop_counter % self.game_hour == 0:
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

            character.reserves.calories -= 2
            character.reserves.thirst -= 2 

            if character.position == character.POSITION_STANDING:
                character.reserves.wind = min(character.reserves.wind+3, character.reserves.max_wind)
            elif character.position == character.POSITION_RESTING:
                character.reserves.wind = min(character.reserves.wind+5, character.reserves.max_wind)
                character.reserves.energy = min(character.reserves.energy+100, character.reserves.max_energy)


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
                character.reserves.sleep -= 1

            # If they're asleep they recover.
            elif character.position == character.POSITION_SLEEPING:
                character.reserves.sleep += 2

                character.reserves.energy = min(character.reserves.energy+625, character.reserves.max_energy)

                if character.reserves.sleep >= 16:
                    character.position = character.POSITION_STANDING
                    player.write("You awaken, fully rested.")

            # If they're tired, they have an increasing chance of falling
            # asleep.
            if character.reserves.sleep < 0:
                chance = random.randint(0, 248)
                if abs(character.reserves.sleep) < chance:
                    character.position = character.POSITION_SLEEPING
                    player.write("You can't stay awake anymore.  You fall asleep.")
