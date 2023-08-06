import hashlib

def Md5sum(string:str) -> str:
    hashlib.md5(string.encode('utf-8')).hexdigest()