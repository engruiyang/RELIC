import time
class SystemClock:
    def now_ms(self)->int: return int(time.time()*1000)
    def monotonic_ms(self)->int: return int(time.monotonic()*1000)
