import datetime


def t_s(timestamp):
    """ Convert different timestamps to datetime object"""
    try:
        if len(str(timestamp)) == 13:
            time = datetime.datetime.fromtimestamp(int(timestamp) / 1000)
        elif len(str(timestamp)) == 10:
            time = datetime.datetime.fromtimestamp(int(timestamp))
        elif len(str(timestamp)) == 16:
            time = datetime.datetime.fromtimestamp(int(timestamp / 1000000))
        elif len(str(timestamp)) == 12:
            time = datetime.datetime.fromtimestamp(int(timestamp.split('.')[0]))

        return time

    except UnboundLocalError:
        return timestamp