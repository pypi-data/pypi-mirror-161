import re

def FindAll(pattern:str, string:str, multiline=False) -> list[list[str]]:
    res = []
    if multiline:
        reres = re.findall(pattern, string, re.MULTILINE)
    else:
        reres = re.findall(pattern, string)

    for i in reres:
        if type(i) == tuple:
            res.append(list(i))
        else:
            t = list()
            t.append(i)
            res.append(t)

    return res 

if __name__ == "__main__":
    print(FindAll("([a-z])([a-z])[0-9]+", "ac123bd456")) # ==> [['a', 'c'], ['b', 'd']]
    print(FindAll("([a-z])[0-9]+", "c123d456")) # ==> [['c'], ['d']]
    print(FindAll("[a-z][0-9]+", "c123d456")) # ==> [['c123'], ['d456']]
