import os

def Basedir(path:str) -> str:
    return os.path.dirname(path)

def Join(*path) -> str:
    return os.path.join(*path)

if __name__ == "__main__":
    print(Join("a", "b"))