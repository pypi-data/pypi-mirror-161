import hashlib

def Md5sum(string:str) -> str:
    return hashlib.md5(string.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    print(Md5sum("abc"))
