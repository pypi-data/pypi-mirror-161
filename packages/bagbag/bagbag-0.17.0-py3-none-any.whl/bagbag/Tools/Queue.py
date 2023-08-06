from __future__ import annotations

try:
    from .MySQL_SQLite import MySQL
    from .MySQL_SQLite import SQLite
except:
    from MySQL_SQLite import MySQL
    from MySQL_SQLite import SQLite

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
    
    def New(self, queueName="__queue__empty__name__") -> NamedQueue:
        if queueName != "__queue__empty__name__":
            queueName = "__queue__name__" + queueName
        
        if queueName not in self.db.Tables():
            self.db.Table(queueName).AddColumn("data", "text")
        
        return NamedQueue(self.db, queueName, self)
        
class NamedQueue():
    def __init__(self, db:MySQL|SQLite, name:str, tq:Queue) -> None:
        self.db = db 
        self.name = name 
        self.tq = tq 
    
    def Size(self) -> int:
        return self.db.Table(self.name).Count()
    
    def Get(self, waiting=True) -> str|None:
        r = self.db.Table(self.name).First()
        if not r:
            if not waiting:
                return None 
            else:
                while not r:
                    time.sleep(0.3)
                    r = self.db.Table(self.name).First()
        
        self.db.Table(self.name).Where("id", "=", r["id"]).Delete()

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