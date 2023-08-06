import re

def FindAll(pattern:str, string:str, multiline=False) -> list:
    if multiline:
        return re.findall(pattern, string, re.MULTILINE)
    else:
        return re.findall(pattern, string)

        