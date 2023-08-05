from datetime import timedelta

def logic_daytime(inp):
    """
    Args:
        inp (tuple or list): (sr, ss, ds)

    Returns:
        bool: True or False
    """
    sunrise = timedelta(hours=inp[0].hour, minutes=inp[0].minute)
    sunset = timedelta(hours=inp[1].hour, minutes=inp[1].minute)
    time = timedelta(hours=inp[2].hour, minutes=inp[2].minute)
    if sunrise <= time < sunset:
        return True
    else:
        return False

def logic_nighttime(sr, ss, ds):
    """
    Args:
        inp (tuple or list): (sr, ss, ds)

    Returns:
        bool: True or False
    """
    sunrise = timedelta(hours=inp[0].hour, minutes=inp[0].minute)
    sunset = timedelta(hours=inp[1].hour, minutes=inp[1].minute)
    time = timedelta(hours=inp[2].hour, minutes=inp[2].minute)
    if sunrise <= time < sunset:
        return False
    else:
        return True
