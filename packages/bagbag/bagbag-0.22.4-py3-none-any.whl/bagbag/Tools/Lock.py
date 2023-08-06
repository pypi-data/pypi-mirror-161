import multiprocessing

# > The `Lock` class is a wrapper around the `multiprocessing.Lock` class
class Lock():
    def __init__(self):
        self.lock = multiprocessing.Lock()
    
    def Acquire(self):
        """
        The function Acquire() is a method of the class Lock. It acquires the lock
        """
        self.lock.acquire()

    def Release(self):
        """
        The function releases the lock
        """
        self.lock.release()

if __name__ == "__main__":
    from threading import Thread
    from time import sleep

    counter = 0

    def increase(by, lock):
        global counter

        lock.Acquire()

        local_counter = counter
        local_counter += by

        sleep(0.1)

        counter = local_counter
        print(f'counter={counter}')

        lock.Release()

    lock = Lock()

    # create threads
    t1 = Thread(target=increase, args=(10, lock))
    t2 = Thread(target=increase, args=(20, lock))

    # start the threads
    t1.start()
    t2.start()

    # wait for the threads to complete
    t1.join()
    t2.join()

    print(f'The final counter is {counter}')