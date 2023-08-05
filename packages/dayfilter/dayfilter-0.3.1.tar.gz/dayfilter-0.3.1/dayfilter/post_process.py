from datetime import timedelta

def ceil_sr(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[0] = ceil_date_hour(inp[0])
    return inp

def ceil_ss(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[1] = ceil_date_hour(inp[1])
    return inp

def floor_sr(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[0] = floor_date_hour(inp[0])
    return inp

def floor_ss(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[1] = floor_date_hour(inp[1])
    return inp

def shift_sr_up(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[0] = shift_date_hour(inp[0])
    return inp

def shift_ss_up(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[1] = shift_date_hour(inp[1])
    return inp

def shift_sr_down(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[0] = shift_date_hour(inp[0], hours=-1)
    return inp

def shift_ss_down(inp):
    """
    Args:
        inp (list): [sr, ss]

    Returns:
        (list): [sr, ss]
    """
    inp[1] = shift_date_hour(inp[1], hours=-1)
    return inp

def ceil_date_hour(dt):
    # sr and ss have precision up to minute, thus ceil and floor only on hour
    return floor_date_hour(dt) + timedelta(hours=1)

def floor_date_hour(dt):
    # sr and ss have precision up to minute, thus ceil and floor only on hour
    return dt.replace(minute=0)

def shift_date_hour(dt, hours=1):
    return dt + timedelta(hours=hours)
