SHOW_WARNING = 0
SHOW_INFO = 1
SHOW_ERROR = 2
SHOW_DEBUG = 3
SHOW_LOGS = 4
SHOW_CURRENT = [SHOW_INFO, SHOW_WARNING, SHOW_ERROR, SHOW_DEBUG, SHOW_LOGS]
# SHOW_CURRENT = []


def setCurrentShow(show_types):
    global SHOW_CURRENT
    SHOW_CURRENT.clear()
    for t in show_types:
        if 0 <= t < 5 and isinstance(t, int):
            SHOW_CURRENT.append(t)


def getCurrentShow():
    global SHOW_CURRENT
    return list(SHOW_CURRENT)


def disableLogs():
    global SHOW_CURRENT
    try:
        SHOW_CURRENT.remove(SHOW_LOGS)
    except ValueError:
        pass


def enableLogs():
    global SHOW_CURRENT
    if SHOW_LOGS not in SHOW_CURRENT:
        SHOW_CURRENT.append(SHOW_LOGS)
