import os
import sys 
from . import Path

def Exit(num:int=0):
    sys.exit(num)

System = os.system 

def Mkdir(path:str):
    os.makedirs(path, exist_ok=True)