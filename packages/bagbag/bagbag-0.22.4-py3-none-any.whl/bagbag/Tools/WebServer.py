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
    from Thread import Thread

class Response():
    Make = make_response
    Abort = abort
    Redirect = redirect
    Render = render_template

class RequestArgs():
    def Get(self, name:str, default:str="") -> str | None:
        return request.args.get(name, default)

class RequestForm():
    def Get(self, name:str, default:str="") -> str | None:
        return request.form.get(name, default)

class Request():
    Args = RequestArgs()
    Form = RequestForm()

    def Method(self) -> str:
        return request.method

    def Json(self) -> dict | list:
        return request.get_json(force=True)
    
    def Data(self) -> str:
        return request.get_data().decode("utf-8")

class WebServer():
    def __init__(self, name:str=__name__):
        self.app = Flask(name)
        
        self.Route = self.app.route 
        self.Request = Request()
        self.Response = Response()
        
    def Run(self, host:str, port:int, block:bool=True, debug:bool=False):
        """
        Runs the Flask app on the specified host and port, optionally in a separate thread
        If block is False then debug will always be False
        
        :param host: The hostname to listen on. Set this to '0.0.0.0' to have the server available
        externally as well. Defaults to '127.0.0.1' or 'localhost'
        :type host: str
        :param port: The port to run the server on
        :type port: int
        :param block: If True, the server will run in the main thread. If False, it will run in a
        separate thread, defaults to True
        :type block: bool (optional)
        :param debug: If True, the server will reload itself on code changes, and it will also provide a
        helpful debugger if things go wrong, defaults to False
        :type debug: bool (optional)
        """
        if block:
            self.app.run(host, port, debug)
        else:
            Thread(self.app.run, host, port, False)

if __name__ == "__main__":
    w = WebServer()

    @w.Route("/")
    def index():
        return "Hello World!"

    @w.Route("/json")
    def json():
        return {"key": "value"}

    @w.Route("/param/<pname>")
    def param(pname):
        return pname

    @w.Route('/method', methods=['GET', 'POST'])
    def login():
        return w.Request.Method()

    # curl 'http://localhost:8080/getArg?key=value'
    @w.Route("/getArg")
    def getArg():
        return w.Request.Args.Get("key", "")

    # curl -XPOST -F "key=value" http://localhost:8080/form
    @w.Route("/form", methods=["POST"])
    def postForm():
        return w.Request.Form.Get("key")

    # curl -XPOST -d '{"key":"value"}' http://localhost:8080/postjson
    @w.Route("/postjson", methods=["POST"])
    def postJson():
        return w.Request.Json()

    # curl -XPOST -d 'Hello World!' http://localhost:8080/postData
    @w.Route("/postData", methods=["POST"])
    def postData():
        return w.Request.Data()

    w.Run("0.0.0.0", 8080, block=False, debug=False)

    import time
    time.sleep(8888)