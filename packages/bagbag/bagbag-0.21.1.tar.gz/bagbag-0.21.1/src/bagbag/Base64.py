import base64 

def Encode(s:str) -> str:
    return base64.b64encode(bytes(s, "utf-8")).decode("utf-8")

def Decode(s:str) -> str:
    return base64.b64decode(s).decode("utf-8")

if __name__ == "__main__":
    data = Encode(open("Lg.py").read())
    print(Decode(data))
    