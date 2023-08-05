import time

class Stopwatch:
    def __init__(self, flags_limit=10, ticks=1):
        ''' ticks in seconds '''
        
        self.time1 = 0
        self.ticks = ticks
        self.stop_time = 0
        self.start_time_bool = False
        self.start_time = 0
        self.flags_limit = flags_limit
        self.flags = []
        
    def start(self):
        self.start_time_bool = True
        self.start_time = time.time() + (self.start_time - self.stop_time)

    def time(self):
        if self.start_time_bool:
            if self.start_time:
                time_now = time.time()
                self.time1 = time_now - self.start_time
                return self.time1 / self.ticks
            return 0
        else:
            if (self.start_time and self.stop_time):
                self.time1 = self.stop_time - self.start_time
                return self.time1 / self.ticks
            return 0
        
    def put_flag(self):
        if len(self.flags) <= self.flags_limit:
            self.flags.append(self.time())

    def stop(self):
        self.stop_time = time.time()
        self.start_time_bool = False
            
    def turn_off(self):
        self.time1 = 0
        self.stop_time = 0
        self.start_time_bool = False
        self.start_time = 0
        self.flags = []
    
