# dayfilter

Filter time-series based on sun movement

## Installation

```plaintext
pip install dayfilter
```

DayFilter depends on [suntime](https://github.com/SatAgro/suntime). Due to known [issue](https://github.com/SatAgro/suntime/issues/12) of suntime, please use my fork of suntime on test-pypi. To install, use:

```plaintext
pip uninstall -y suntime
pip install -i https://test.pypi.org/simple/ suntime-yasirroni
```

I can't bundle my fork of suntime into DayFilter due to LICENSE incompatibility issue.

## Usage

Simple use case of getting `list` of `bool`

```python
from datetime import datetime
from dayfilter import is_daytime

date_string = '2010-01-01-16:58:30.00000'
date_datetime = datetime.strptime(date_string, '%Y-%m-%d-%H:%M:%S.%f')

# WASHINGTON DC DULLES INT'L AR [STERLING - ISIS], VA. data
latitude = 38.98
longitude = -77.47
time_zone = -5

is_daytime(date_datetime, latitude, longitude, time_zone)
```

Using `DayFilter` class for multiple call

```python
from dayfilter import DayFilter
import pandas as pd
from datetime import datetime

# WASHINGTON DC DULLES INT'L AR [STERLING - ISIS], VA. data
latitude = 38.98
longitude = -77.47
time_zone = -5

f = DayFilter(latitude, longitude, time_zone)

date_strings = [
    '2010-01-01-05:58:42.00000',
    '2010-01-01-06:59:22.00000',
    '2010-01-01-13:22:23.00000',
    '2010-01-01-14:54:55.00000',
    '2010-01-01-15:31:45.00000',
    '2010-01-02-17:12:22.00000',
    '2010-01-02-15:12:32.00000',
    '2010-01-02-16:59:32.00000',
    '2010-01-02-18:00:11.00000',
]
date_format = '%Y-%m-%d-%H:%M:%S.%f'
date_datetimes = [datetime.strptime(date_string, date_format) for date_string in date_strings]

df = pd.DataFrame(index=date_datetimes, data=[1,2,3,4,5,6,7,8,9])

df_ = f.filter(df)
print(df_)
```

Adcanced use of `DayFilter` class with custom filter

```python
from dayfilter import DayFilter
from dayfilter.post_process import shift_sr_down, shift_ss_up
from dayfilter.logic import logic_daytime

f2 = DayFilter(latitude, longitude, time_zone, post_processes=[shift_sr_down, shift_ss_up], logic=logic_daytime)

df__ = f2.filter(df)
print(df__)

print(f.get_sr_ss(df_.index[0]))
print(f.get_sr_ss(df_.index[0], post_processes=True))
```

## TODO

1. Consider refactor to astral due to suntime LICENSE.
    a. Astral is slower and have same bug with the original suntime
    b. Soulution of the suntime bug exist on yasirroni/suntime

## License

This project is licensed in MIT License, but depends on [`suntime` that use LGPL license](https://github.com/SatAgro/suntime/blob/master/LICENSE).
