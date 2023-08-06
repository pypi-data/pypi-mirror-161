class TimeMock:
   _time = 0


   @classmethod
   def time(cls):
      return cls._time


   @classmethod
   def set_time(cls, new_time):
      cls._time = new_time
