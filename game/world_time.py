class WorldTime:

    MONTH_NAME = [ "", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    SEASON_NAME = ["", "winter", "late winter", "early spring", "spring", "late spring", "early summer", "summer", "late summer", "early fall", "fall", "late fall", "early winter"]

    def __init__(self, loops_a_second):
        self.loops_a_second = loops_a_second

        self.loops_a_minute = self.loops_a_second
        self.loops_an_hour = 60 * self.loops_a_minute
        self.loops_a_day = 24 * self.loops_an_hour
        self.loops_a_month = 30 * self.loops_a_day
        self.loops_a_year = 12 * self.loops_a_month

        self.year = 1
        self.month = 1
        self.day = 1
        self.hour = 0
        self.minute = 0
        self.second = 0

        self.night = self.hour >= 20 or self.hour <= 6

        self.loop = 0

        self.events = {}

    def after(self, loops, action):
        target_loop = self.loop + loops
        if not target_loop in self.events:
            self.events[target_loop] = []
        self.events[target_loop].append(action)

    def tick(self):
        self.loop += 1

        if self.loop % self.loops_a_second == 0:
            self.second += 1

        if self.second >= 60:
            self.second = 0
            self.minute += 1

        if self.minute >= 60:
            self.minute = 0
            self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1

        if self.day > 30:
            self.day = 1
            self.month += 1

        if self.month > 12:
            self.month = 1
            self.year += 1

        self.night = self.hour >= 20 or self.hour <= 6

        if self.loop in self.events:
            for action in self.events[self.loop]:
                action()
