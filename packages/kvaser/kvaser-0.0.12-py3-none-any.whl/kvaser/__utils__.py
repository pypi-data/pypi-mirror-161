
def filesize(size, digits=2):
    """From bytes to kilo, mega, tera
    """
    power = 1024
    Dic_powerN = {0: 'B', 1: 'kB', 2: 'MB', 3: 'GB', 4: 'TB'}
    if size < power:
        return size, Dic_powerN[0]
    n = 1
    if size <= power**2:
        size /= power
    else:
        while size  > power:
            n  += 1
            size /= power**n
    size = round(size*(10**digits))/(10**digits)
    return size, Dic_powerN[n]
