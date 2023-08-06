from typing import Iterable

def Range(startOrEnd:int, end:int=None) -> Iterable:
    """
    "If the second argument is provided, return a range from the first argument to the second argument,
    otherwise return a range from 0 to the first argument."
    
    :param startOrEnd: The first number in the range. If end is not specified, this is the last number
    in the range
    :type startOrEnd: int
    :param end: The end of the range
    :type end: int
    :return: A range object
    """
    if end:
        return range(startOrEnd, end)
    else:
        return range(0, startOrEnd)

if __name__ == "__main__":
    print([i for i in Range(10)])
    print([i for i in Range(20, 30)])