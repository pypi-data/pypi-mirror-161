import queue 
from typing import Any

# > A `Chan` is a thread-safe queue with a `Size` method
class Chan():
    def __init__(self, size=0) -> None:
        self.q = queue.Queue(maxsize=size)
    
    def Size(self) -> int:
        """
        This function returns the size of the queue
        :return: The size of the queue
        """
        return self.q.qsize()
    
    def Get(self, block:bool=True, timeout:int=None) -> Any:
        """
        The function Get() returns the next item from the queue
        
        :param block: If True, the Get() method will block until an item is available. If False, it will
        return immediately with an exception if no item is available, defaults to True
        :type block: bool (optional)
        :param timeout: If the queue is empty, block for up to timeout seconds
        :type timeout: int
        :return: The get method returns the next item in the queue.
        """
        return self.q.get(block=block, timeout=timeout)
    
    def Put(self, item:Any, block:bool=True, timeout:int=None):
        """
        Put(self, item:Any, block:bool=True, timeout:int=None):
        
        :param item: The item to be put into the queue
        :type item: Any
        :param block: If True, the Put() method will block until the queue has space available. If
        False, it will raise a queue.Full exception if the queue is full, defaults to True
        :type block: bool (optional)
        :param timeout: If the optional argument timeout is not given or is None, block if necessary
        until an item is available. If the timeout argument is a positive number, it blocks at most
        timeout seconds and raises the Full exception if no item was available within that time.
        Otherwise (block is false), put an item on
        :type timeout: int
        """
        self.q.put(item, block=block, timeout=timeout)

if __name__ == "__main__":
    q = queue.Queue(maxsize = 3)