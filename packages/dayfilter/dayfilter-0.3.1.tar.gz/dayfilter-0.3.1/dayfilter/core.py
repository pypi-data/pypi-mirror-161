import pytz
from suntime import Sun
from datetime import timezone, timedelta

from .logic import logic_daytime, logic_nighttime

# TODO:
# 1. No need to make sr and ss if we already have the data
# 2. Reimplement suntime.Sun() for speed and because it use LGPL License
# 3. Make a class that will store latitude, longitude, and time_zone
# 4. Embed sun to the class

class DayFilter():
    def __init__(self, latitude, longitude, time_zone, post_processes=None, logic='daytime'):
        """
        Args:
            latitude (int or float): 
                latitude in degree
            longitude (int or float):
                longitude in degree
            time_zone (int): 
                time zone from UTC
            post_processes (list[function], optional): 
                list of function to post processing sunrise and suntime. Defaults to None.
            logic (str or function, optional): 
                strategy to evaluate. Defaults to 'daytime'.
        """
        self.sun = Sun(latitude, longitude)
        self.tz = timezone(timedelta(hours=time_zone))

        self.post_processes = post_processes

        if logic == 'daytime':
            self.logic = logic_daytime
        elif logic == 'nighttime':
            self.logic = logic_nighttime
        else:
            # support custom logic
            self.logic = logic

        # initials
        self.saved_date = None
        self._sr = None
        self._ss = None

    def filter(self, df):
        idx = self.get_indices(df.index)
        return df.iloc[idx]

    def get_indices(self, ds):
        return [i for i, x in enumerate(self.evaluate(ds)) if x]

    def evaluate(self, ds):
        # TODO: only use up YEAR-MONTH-DAY to support RLU cache
        return [self.evaluate_(ds_, self.sun, self.tz) for ds_ in ds]

    def evaluate_(self, ds, sun, tz):
        # TODO: use RLU cache
        this_date = (ds.year, ds.month, ds.day)
        if  self.saved_date != this_date:
            # save date
            self.saved_date = (ds.year, ds.month, ds.day)

            # get default sr and ss
            self._sr, self._ss = get_sr_ss(ds, sun, tz)
            
            # post_processes
            if self.post_processes is not None:
                for pp in self.post_processes:
                    self._sr, self._ss = pp([self._sr, self._ss])

        return self.logic((self._sr, self._ss, ds))

    def get_sr_ss(self, ds_, use_post_processes=False):
        # NOTE: there are two `get_sr_ss`, method of DayFilter and a separate function
        sr, ss = get_sr_ss(ds_, self.sun, self.tz)

        if use_post_processes:
            if self.post_processes is not None:
                for pp in self.post_processes:
                    sr, ss = pp([sr, ss])
            else:
                print('No post_process defined but called by get_sr_ss')

        return sr, ss

def are_nighttimes(ds, latitude, longitude, time_zone, params={}):
    sun = Sun(latitude, longitude)
    tz = timezone(timedelta(hours=time_zone))
    return [_is_nighttime(ds_, sun, tz, **params) for ds_ in ds]

def are_daytimes(ds, latitude, longitude, time_zone, params={}):
    sun = Sun(latitude, longitude)
    tz = timezone(timedelta(hours=time_zone))
    return [_is_daytime(ds_, sun, tz, **params) for ds_ in ds]

def is_nighttime(ds, latitude, longitude, time_zone, params={}):
    sun = Sun(latitude, longitude)
    tz = timezone(timedelta(hours=time_zone))
    return _is_nighttime(ds, sun, tz, **params)

def is_daytime(ds, latitude, longitude, time_zone, params={}):
    sun = Sun(latitude, longitude)
    tz = timezone(timedelta(hours=time_zone))
    return _is_daytime(ds, sun, tz, **params)

def _is_nighttime(ds, sun, tz, post_processes=None):
    sr, ss = get_sr_ss(ds, sun, tz)
    if post_processes is not None:
        for pp in post_processes:
                sr, ss = pp([sr, ss])
    return logic_nighttime((_sr, _ss, ds))

def _is_daytime(ds, sun, tz, post_processes=None):
    sr, ss = get_sr_ss(ds, sun, tz)
    if post_processes is not None:
        for pp in post_processes:
                sr, ss = pp([sr, ss])
    return logic_daytime((sr, ss, ds))

def get_sr_ss(ds_, sun, tz):
    # sr and ss have precision up to minute, thus ceil and floor only on hour
    sr = sun.get_sunrise_time(ds_, tz=tz).replace(tzinfo=None)
    ss = sun.get_sunset_time(ds_, tz=tz).replace(tzinfo=None)
    return sr, ss
