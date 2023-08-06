import time
import datetime as dt
def current_time():
    return time.time() * 1000

def check_time_format(timestamp):
    format=False
    ts = int(timestamp)
    try:
            dt.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            format=False
    except Exception as e:
            format=True
        
    return format
    