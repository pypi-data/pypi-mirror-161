from flask import Flask
from flask import request
from flask import make_response
from flask import abort, redirect
from flask import render_template

try:
    from ..Thread import Thread
except:
    import sys 
    sys.path.append("..")
    from ..Thread import Thread

class Response():
    Make = make_response
    Abort = abort
    Redirect = redirect
    Render = render_template

class Web():
    def __init__(self, host:str, port:int, block:bool=True, name:str=__name__):
        self.app = Flask(name)
        
        self.Route = self.app.route 
        self.Request = request
        self.Response = Response()

        if block:
            self.app.run(host, port, True)
        else:
            Thread(self.app.run, host, port, True)