class TimeLibrary:
    """
    Library containing behavior for manipulating the world time.
    """

    def __init__(self, library, store):
        self.library = library
        self.store = store

    def reportHourChanges(self):
        time = self.store.world.time

        ## Time of day based on hour.
        if time.hour == 7:
            for player in self.store.players:
                player.write("It is dawn.")
        elif time.hour == 8:
            for player in self.store.players:
                player.write("It is morning.")
        elif time.hour == 12:
            for player in self.store.players:
                player.write("It is noon.")
        elif time.hour == 13:
            for player in self.store.players:
                player.write("It is afternoon.")
        elif time.hour == 19:
            for player in self.store.players:
                player.write("It is dusk.")
        elif time.hour == 20:
            for player in self.store.players:
                player.write("It is night.")


    def loop(self):
        """
        Advance world time by one loop.
        """

        time = self.store.world.time

        time.loop += 1

        if time.loop % time.loops_a_second == 0:
            time.minute += 1

        if time.minute >= 60:
            time.minute = 0
            time.hour += 1
            self.reportHourChanges()

        if time.hour >= 24:
            time.hour = 0
            time.day += 1

        if time.day > 30:
            time.day = 1
            time.month += 1

        if time.month > 12:
            time.month = 1
            time.year += 1

        if time.month == 12 or time.month <= 2:
            time.season = "winter"
        elif time.month >= 3 and time.month <= 5:
            time.season = "spring"
        elif time.month >= 6 and time.month <= 8:
            time.season = "summer"
        elif time.month >= 9 and time.month <= 11:
            time.season = "fall"

        # Reset the loop counter every 5 years.  This will keep the loop
        # counter under max int.  Not technically necessary in Python, but you
        # know... ;)
        if time.year % 5 == 0:
            time.loop = 0
            time.average_loop_time = 0

        time.night = time.hour >= 20 or time.hour <= 6

class WorldLibrary:
    """
    Library containing behavior of acting on the World.
    """

    def __init__(self, library, store):
        self.library = library
        self.store = store

        self.time = TimeLibrary(library, store)
