from game.store.models.base import NamedModel
from game.store.models.base import JsonSerializable

class Time(JsonSerializable):

    MONTH_NAME = [ "", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    SEASON_NAME = ["", "winter", "late winter", "early spring", "spring", "late spring", "early summer", "summer", "late summer", "early fall", "fall", "late fall", "early winter"]

    def __init__(self):
        self.loops_a_second = 10 

        # 1 game minute == 1 real second
        self.loops_a_minute = self.loops_a_second

        # 1 game hour == 1 real minute
        self.loops_an_hour = 60 * self.loops_a_minute

        # 1 game day == 24 real minutes 
        self.loops_a_day = 24 * self.loops_an_hour

        # 1 game month == 12 real hours
        self.loops_a_month = 30 * self.loops_a_day

        # 1 game year == 6 real days
        self.loops_a_year = 12 * self.loops_a_month

        self.year = 1
        self.month = 1
        self.day = 1
        self.hour = 0
        self.minute = 0

        self.season = "winter"
        self.night = self.hour >= 20 or self.hour <= 6

        self.loop = 0
        self.average_loop_time = 0

    def toJson(self):
        data = {}

        data['year'] = self.year
        data['month'] = self.month
        data['day'] = self.day
        data['hour'] = self.hour
        data['minute'] = self.minute
        data['night'] = self.night
        data['loop'] = self.loop

        return data

    def fromJson(self, data):
        self.year = data['year']
        self.month = data['month']
        self.day = data['day']
        self.hour = data['hour']
        self.minute = data['minute']

        self.night = data['night']
        self.loop = data['loop']
        return self


class World(NamedModel):

    def __init__(self):
        super(World, self).__init__()

        self.name = '' 
        self.width = 0 
        self.room_width = 0  

        self.rooms = []
        self.time = Time()

    def toJson(self):
        data = {}

        data['name'] = self.name
        data['width'] = self.width
        data['roomWidth'] = self.room_width

        data['rooms'] = self.rooms

        if self.time:
            data['time'] = self.time.toJson()

        return data

    def fromJson(self, data):
        self.name = data['name']
        self.width = data['width']
        self.room_width = data['roomWidth']

        self.rooms = data['rooms']

        if 'time' in data:
            self.time.fromJson(data['time'])
        else:
            self.time.month = 6
            self.time.hour = 8
            self.time.night = False
            self.time.season = "summer"

        return self

