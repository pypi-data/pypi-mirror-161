from __future__ import annotations
from curses import keyname
import redis 

class RedisLock():
    def __init__(self, lock):
        self.lock = lock

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

class Redis():
    def __init__(self, host: str, port: int = 6379, database: int = 0, password: str = ""):
        """
        It creates a Redis object.
        
        :param host: The hostname or IP address of the Redis server
        :type host: str
        :param port: The port number of the Redis server. The default is 6379, defaults to 6379
        :type port: int (optional)
        :param database: The database number to connect to, defaults to 0
        :type database: int (optional)
        :param password: The password to use to connect to the Redis server
        :type password: str
        """
        self.rdb = redis.Redis(host=host, port=port, db=database, password=password)
    
    def Ping(self) -> bool:
        """
        This function returns a boolean value that indicates whether the connection to the Redis server
        is still alive
        :return: A boolean value.
        """
        return self.rdb.ping()
    
    # https://redis.readthedocs.io/en/v4.3.4/commands.html#redis.commands.core.CoreCommands.set
    # ttl, second
    def Set(self, key:str, value:str, ttl:int=None) -> (bool | None):
        """
        It sets the value of a key in the database.
        
        :param key: The key to set
        :type key: str
        :param value: The value to be stored in the key
        :type value: str
        :param ttl: Time to live in seconds
        :type ttl: int
        :return: The return value is a boolean value.
        """
        return self.rdb.set(key, value, ex=ttl)
    
    # https://redis.readthedocs.io/en/v4.3.4/commands.html#redis.commands.core.CoreCommands.get
    def Get(self, key:str) -> (str | None):
        """
        It gets the value of a key from the redis database.
        
        :param key: The key to get the value of
        :type key: str
        :return: A string or None
        """
        res = self.rdb.get(key)
        if res:
            return res.decode('utf-8')
        else:
            return res

    # https://redis.readthedocs.io/en/v4.3.4/commands.html#redis.commands.core.CoreCommands.delete
    def Del(self, key:str) -> bool:
        """
        It deletes the key from the database
        
        :param key: The key to delete
        :type key: str
        :return: The return value is a boolean value.
        """
        return self.rdb.delete(key) == 1
    
    # https://redis.readthedocs.io/en/latest/connections.html?highlight=lock#redis.Redis.lock
    def Lock(self, key:str) -> RedisLock:
        """
        It returns a RedisLock object.
        
        :param key: The key to lock
        :type key: str
        :return: A RedisLock object.
        """
        return RedisLock(self.rdb.lock(key))

if __name__ == "__main__":
    r = Redis("10.69.69.1")
    r.Ping()
    print(1, r.Get("key"))
    print(2, r.Set("key", "value"))
    print(3, r.Get("key"))
    print(4, r.Del("key"))
    print(5, r.Get("key"))
    l = r.Lock("lock_key")
    l.Acquire()
    l.Release()