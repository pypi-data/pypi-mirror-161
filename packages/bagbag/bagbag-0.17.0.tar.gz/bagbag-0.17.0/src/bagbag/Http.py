import requests 
from urllib3.exceptions import InsecureRequestWarning
from requests_toolbelt.utils import dump

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from io import BytesIO, SEEK_SET, SEEK_END

try:
    from .String import String
except:
    from String import String

class responseStream(object):
    def __init__(self, request_iterator):
        self._bytes = BytesIO()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)
    
    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)

class Response():
    def __init__(
        self, 
        Headers:dict=None, 
        Content:str=None, 
        StatusCode:int=None, 
        URL:str=None, 
        Debug:str=None
    ):
        self.Headers = Headers # dict[str]str
        self.Content = Content # str 
        self.StatusCode = StatusCode # int
        self.URL = URL # str
        self.Debug = Debug # str
    
    def __str__(self) -> str:
        Debug = None
        if self.Debug != None:
            if len(self.Debug) > 160:
                Debug = String(self.Debug[:160]).Repr() + "..."
            else:
                Debug = String(self.Debug[:160]).Repr() 
        
        Content = None 
        if self.Content != None:
            if len(self.Content) > 160:
                Content = String(self.Content[:160]).Repr() + "..."
            else:
                Content = String(self.Content[:160]).Repr()
        return f"Http.Response(\n    URL={self.URL}, \n    StatusCode={self.StatusCode}, \n    Headers={self.Headers}, \n    Debug={Debug}, \n    Content={Content}\n)"

    def __repr__(self) -> str:
        return str(self)

def makeResponse(response:requests.Response, Debug:bool, ReadBodySize:int) -> Response:
    resp = Response()

    if Debug:
        resp.Debug = dump.dump_all(response).decode("utf-8")
    
    st = responseStream(response.iter_content(512))
    if not ReadBodySize:
        content = st.read()
    else:
        content = st.read(ReadBodySize)
    if content:
        resp.Content = content.decode("utf-8")
    
    resp.Headers = response.headers 
    resp.StatusCode = response.status_code
    resp.URL = response.url 
    
    return resp

def Head(url:str, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.head(
                url, 
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def Get(url:str, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None,  TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.get(
                url, 
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def PostRaw(url:str, Data:str, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.post(
                url, 
                data=Data,
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def PostJson(url:str, Json:dict,Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.post(
                url, 
                json=Json,
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def PostForm(url:str, Data:dict, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.post(
                url, 
                data=Data,
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def Delete(url:str, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.delete(
                url, 
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def PutForm(url:str, Data:dict,Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.put(
                url, 
                data=Data,
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def PutRaw(url:str, Data:str, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False, Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.put(
                url, 
                data=Data,
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

def PutJson(url:str, Json:dict, Timeout:str=None, ReadBodySize:int=None, FollowRedirect:bool=True, HttpProxy:str=None, TimeoutRetryTimes:int=0, InsecureSkipVerify:int=False,Debug:bool=False):
    timeouttimes = 0
    while True:
        try:
            response = requests.put(
                url, 
                json=Json,
                timeout=Timeout, 
                allow_redirects=FollowRedirect,
                proxies={
                    'http': HttpProxy,
                    "https": HttpProxy,
                },
                verify=(not InsecureSkipVerify),
                stream=True
            )

            return makeResponse(response, Debug, ReadBodySize)
        except requests.exceptions.Timeout as e:
            timeouttimes += 1
            if TimeoutRetryTimes < timeouttimes:
                raise e

if __name__ == "__main__":
    # resp = Head("https://httpbin.org/redirect/2", Debug=True)
    # print(resp)

    # resp = Get("https://httpbin.org", Debug=True)
    # print(resp)

    resp = PutForm("http://127.0.0.1:8878", {"a": "b", "c": "d"})
    print(resp)