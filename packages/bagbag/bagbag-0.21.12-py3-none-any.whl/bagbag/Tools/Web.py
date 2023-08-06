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

class RequestArgs():
    def Get(self, *args, **kwargs) -> str | None:
        return request.args.get(*args, **kwargs)

class RequestForm():
    def Get(self, *args, **kwargs) -> str | None:
        return request.form.get(*args, **kwargs)

class Request():
    Args = RequestArgs()
    Form = RequestForm()

    def Method(self) -> str:
        return request.method

    def Json(self) -> dict | list:
        return request.get_json(force=True)
    
    def Data(self) -> str:
        return request.data.decode("utf-8")

class Web():
    def __init__(self, name:str=__name__):
        self.app = Flask(name)
        
        self.Route = self.app.route 
        self.Request = Request()
        self.Response = Response()
        
    def Run(self, host:str, port:int, block:bool=True):
        if block:
            self.app.run(host, port, True)
        else:
            Thread(self.app.run, host, port, True)