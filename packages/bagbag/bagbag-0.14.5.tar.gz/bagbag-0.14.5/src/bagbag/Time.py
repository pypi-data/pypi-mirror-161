import time
import datetime

Sleep = time.sleep
Now = time.time 

def Strftime(format:str, timestamp:float|int) -> str:
    """
    It converts a timestamp to a string.
    
    :param format: The format string to use
    :type format: str
    :param timestamp: The timestamp to format
    :type timestamp: float|int
    :return: A string
    """
    dobj = datetime.datetime.fromtimestamp(timestamp)
    return dobj.strftime(format)

def Strptime(format:str, timestring:str) -> int:
    """
    It takes a string of a date and time, and a format string, and returns the Unix timestamp of that
    date and time
    
    :param format: The format of the timestring
    :type format: str
    :param timestring: The string to be converted to a timestamp
    :type timestring: str
    :return: The timestamp of the datetime object.
    """
    dtime = datetime.datetime.strptime(timestring, format)
    dtimestamp = dtime.timestamp()
    return int(round(dtimestamp))

if __name__ == "__main__":
    print(Strptime("%Y-%m-%d %H:%M:%S", "2022-05-02 23:34:10"))
    print(Strftime("%Y-%m-%d %H:%M:%S", 1651520050))
    print(Strftime("%Y-%m-%d %H:%M:%S", Now()))