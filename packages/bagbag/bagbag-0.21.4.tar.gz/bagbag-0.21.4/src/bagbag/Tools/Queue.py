from __future__ import annotations

try:
    from .MySQL_SQLite import MySQL
    from .MySQL_SQLite import SQLite
    from .Lock import Lock 
except:
    from MySQL_SQLite import MySQL
    from MySQL_SQLite import SQLite
    from Lock import Lock

import time

try:
    from ..Base64 import Encode as b64encode
    from ..Base64 import Decode as b64decode
except:
    import sys 
    sys.path.append("..")
    from Base64 import Encode as b64encode
    from Base64 import Decode as b64decode

class Queue():  
    def __init__(self, db:MySQL|SQLite):
        self.db = db 
    
    def New(self, queueName="_queue_empty_name_") -> NamedQueue:
        queueName = ''.join(list(map(lambda x: x if x in "qazwsxedcrfvtgbyhnujmikolopQAZWSXEDCRFVTGBYHNUJMIKOLP0123456789" else "_", queueName)))
        
        if queueName != "_queue_empty_name_":
            queueName = "_queue_" + queueName
        
        if queueName not in self.db.Tables():
            self.db.Table(queueName).AddColumn("data", "text")
        
        return NamedQueue(self.db, queueName, self)
        
class NamedQueue():
    def __init__(self, db:MySQL|SQLite, name:str, tq:Queue) -> None:
        name = ''.join(list(map(lambda x: x if x in "qazwsxedcrfvtgbyhnujmikolopQAZWSXEDCRFVTGBYHNUJMIKOLP0123456789" else "_", name)))

        self.db = db 
        self.name = name 
        self.tq = tq 
        self.lock = Lock()
    
    def Size(self) -> int:
        return self.db.Table(self.name).Count()
    
    def Get(self, waiting=True) -> str|None:
        self.lock.Acquire()
        r = self.db.Table(self.name).First()
        if not r:
            if not waiting:
                self.lock.Release()
                return None 
            else:
                while not r:
                    time.sleep(0.3)
                    r = self.db.Table(self.name).First()
        
        self.db.Table(self.name).Where("id", "=", r["id"]).Delete()

        self.lock.Release()
        return b64decode(r["data"])
    
    def Put(self, string:str):
        self.db.Table(self.name).Data({
            "data": b64encode(string),
        }).Insert()

if __name__ == "__main__":
    db = MySQL("127.0.0.1", 3306, "root", "r", "test")
    q = Queue(db)
    qn = q.New("name")
    qn.Put("abc")
    print(qn.Size())
    print(qn.Get())