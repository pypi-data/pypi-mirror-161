import time

try:
    from .Lock import Lock
except:
    from Lock import Lock

# 在低速率的时候能限制准确. 
# 高速率例如每秒50次以上, 实际速率会降低, 速率越高降低越多. 
# 
# It takes a rate limit string in the form of "X/Y" where X is the number of requests and Y is the
# duration. 
# The duration can be specified in seconds (s), minutes (m), hours (h), or days (d). 
# The class has a Take() method that will block until it is approve
#
# The Take() method should be thread-safe.
#
class RateLimit:
    def __init__(self, rate:str):
        self.history = None
        self.rate = rate
        self.num, self.duration = self._parse_rate()
        self.history = []
        self.lock = Lock()
        self.sleeptime = float(self.duration) / float(self.num)

    def _parse_rate(self):
        num, period = self.rate.split('/')
        num = int(num)
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        return (num, duration)

    def Take(self):
        self.lock.Acquire()
        current_time = time.time()

        if not self.history:
            self.history.append(current_time)
            self.lock.Release()
            return 

        while len(self.history) > self.num:
            if self.history and self.history[-1] <= current_time - self.sleeptime:
                self.history.pop()
            else:
                time.sleep(self.sleeptime)
  
        time.sleep(self.sleeptime)
        self.history.insert(0, current_time)
        self.lock.Release()

if __name__ == "__main__":
    def y(r):
        while True:
            r.Take()
            yield "1"

    import sys 
    t = RateLimit(sys.argv[1] + "/s") 
    
    from ProgressBar import ProgressBar
    pb = ProgressBar(y(t))
    for i in pb:
        pass
