from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import telethon

class TelegramGeo():
    def __init__(self):
        self.Long = None
        self.Lat = None 
        self.AccessHash = None
    
    def __repr__(self):
        return f"TelegramGeo(Long={self.Long}, Lat={self.Lat}, AccessHash={self.AccessHash})"
        
    def __str__(self):
        return f"TelegramGeo(Long={self.Long}, Lat={self.Lat}, AccessHash={self.AccessHash})"
        
class TelegramPhoto():
    def __init__(self):
        self.ID = None
        self.AccessHash = 0
    
    def __repr__(self):
        return f"TelegramPhoto(ID={self.ID}, AccessHash={self.AccessHash})"
        
    def __str__(self):
        return f"TelegramPhoto(ID={self.ID}, AccessHash={self.AccessHash})"
        
# File and Audio
class TelegramFile():
    def __init__(self):
        self.Name = ""
        self.Size = 0
        self.ID = None 
        self.AccessHash = 0
    
    def __repr__(self):
        return f"TelegramFile(Name={self.Name}, Size={self.Size}, ID={self.ID}, AccessHash={self.AccessHash})"
        
    def __str__(self):
        return f"TelegramFile(Name={self.Name}, Size={self.Size}, ID={self.ID}, AccessHash={self.AccessHash})"
        
class TelegramMessage():
    def __init__(self, client:TelegramClient):
        self.client = client
        self.PeerType = None 
        self.Chat = TelegramPeer(client=self.client)
        self.ID = None 
        self.Time = None 
        self.Action = None 
        self.File = None
        self.Photo = None
        self.Geo = None
        self.Message = None
        self.User = None
    
    def __repr__(self):
        return f"TelegramMessage(PeerType={self.PeerType}, Chat={self.Chat}, ID={self.ID}, Time={self.Time}, Action={self.Action}, File={self.File}, Photo={self.Photo}, Message={self.Message}, User={self.User})"
        
    def __str__(self):
        return f"TelegramMessage(PeerType={self.PeerType}, Chat={self.Chat}, ID={self.ID}, Time={self.Time}, Action={self.Action}, File={self.File}, Photo={self.Photo}, Message={self.Message}, User={self.User})"
        
class TelegramPeer():
    def __init__(self, Type:str=None, Name:str=None, Username:str=None, ID:int=None, AccessHash:int=None, PhoneNumber:int=None, LangCode:str=None, client:TelegramClient=None):
        """
        :param Type: The type of the entity. Can be either "user" or "channel" (group)
        :type Type: str
        :param Name: The name of the user or channel
        :type Name: str
        :param Username: The username of the user or channel
        :type Username: str
        :param ID: The ID of the user or chat
        :type ID: int
        :param AccessHash: This is a unique identifier for a user or group. It is used to identify a user
        or group in a secure way
        :type AccessHash: int
        :param PhoneNumber: The phone number of the user
        :type PhoneNumber: int
        :param LangCode: The language code of the user
        :type LangCode: str
        """
        self.Type = Type # channel(group), user
        self.Name = Name # 名字, First Name + Last Name 或者 Title 
        self.Username = Username 
        self.ID = ID
        self.AccessHash = AccessHash
        self.PhoneNumber = PhoneNumber 
        self.LangCode = LangCode 
        self.Resolved = False # 是否已解析. 只设置一个ID, 解析之后就补上其它的字段.
        self.client = client # telethon.sync.TelegramClient
    
    def History(self, limit:int=100, offset:int=0) -> list:
        """
        It takes a chat object, and returns a list of messages in that chat.
        
        :param limit: The maximum number of messages to be returned, defaults to 100
        :type limit: int (optional)
        :param offset: The offset of the first message to be returned, defaults to 0
        :type offset: int (optional)
        :return: A list of TelegramMessage objects
        """
        res = []
        getmessage = self.client.get_messages(self.ID, limit=limit, offset_id=offset)
        for message in getmessage:
            # if message.id == 5:
            #     import ipdb
            #     ipdb.set_trace()
            msg = TelegramMessage(self.client)
            msg.PeerType = self.Type 
            msg.Chat = self 
            msg.ID = message.id 
            msg.Time = int(message.date.timestamp())
            if message.action:
                msg.Action = message.action.to_dict()["_"]
            if message.media:
                if message.document:
                    msg.File = TelegramFile()
                    msg.File.ID = message.document.id 
                    msg.File.AccessHash = message.document.access_hash
                    msg.File.Size = message.document.size 
                    for attr in message.media.document.attributes:
                        if attr.to_dict()['_'] == "DocumentAttributeFilename":
                            msg.File.Name = attr.to_dict()['file_name']
                elif message.photo:
                    msg.Photo = TelegramPhoto()
                    msg.Photo.ID = message.photo.id
                    msg.Photo.AccessHash = message.photo.access_hash
                elif message.geo:
                    msg.Geo = TelegramGeo()
                    msg.Geo.AccessHash = message.geo.access_hash
                    msg.Geo.Lat = message.geo.lat 
                    msg.Geo.Long = message.geo.long
                # else: 
                #     import ipdb 
                #     ipdb.set_trace()
                #     print(message)
            if message.message:
                msg.Message = message.message
            if message.from_id:
                msg.User = TelegramPeer(ID=message.from_id.user_id, client=self.client)
            res.append(msg)
        return res

    def Resolve(self):
        """
        Resolve Peer, get information by peer id. 
        """
        if self.ID:
            obj = self.client.get_entity(self.ID)
            # import ipdb
            # ipdb.set_trace()
            if type(obj) == telethon.tl.types.Channel:
                self.Type = "channel"
                self.Name = obj.title
            elif type(obj) == telethon.tl.types.User:
                self.Type = "user"
                self.Name = " ".join([i for i in filter(lambda x: x != None, [obj.first_name, obj.last_name])])
            
            self.AccessHash = obj.access_hash
            self.Username = obj.username 
            self.ID = obj.id

    def __repr__(self):
        return f"TelegramPeer(Type={self.Type}, Name={self.Name}, Username={self.Username}, ID={self.ID}, AccessHash={self.AccessHash})"

    def __str__(self):
        return f"TelegramPeer(Type={self.Type}, Name={self.Name}, Username={self.Username}, ID={self.ID}, AccessHash={self.AccessHash})"

# It's a wrapper for the `telethon` library that allows you to use it in a more Pythonic way
class Telegram():
    def __init__(self, appid:str, apphash:str, sessionString:str=None):
        """
        __init__(self, appid:str, apphash:str, sessionString:str=None):
        
        :param appid: Your app's APP ID
        :type appid: str
        :param apphash: This is a hash that is generated by Telegram when you register your app
        :type apphash: str
        :param sessionString: This is the session string that you get from the Telegram API
        :type sessionString: str
        """
        self.client = TelegramClient(StringSession(sessionString), appid, apphash)
        self.client.start()

        me = self.client.get_me()
        print(me.stringify())

    def SessionString(self) -> str:
        """
        It takes the session object from the client object and saves it to a string
        :return: The session string is being returned.
        """
        return self.client.session.save()
    
    def ResolvePeerByUsername(self, username:str) -> TelegramPeer:
        """
        It resolves a username to a TelegramPeer object.
        
        :param username: The username of the peer you want to resolve
        :type username: str
        :return: A TelegramPeer object.
        """
        tp = TelegramPeer()

        obj = self.client.get_entity(username)
        if type(obj) == telethon.tl.types.Channel:
            tp.Type = "channel"
            tp.Name = obj.title
        elif type(obj) == telethon.tl.types.User:
            tp.Type = "user"
            tp.Name = " ".join(filter(lambda x: x != None, [obj.first_name, obj.last_name]))
        
        tp.AccessHash = obj.access_hash
        tp.Username = obj.username 
        tp.ID = obj.id

        tp.client = self.client

        return tp

if __name__ == "__main__":
    import json 
    ident = json.loads(open("Telegram.ident").read())
    app_id = ident["appid"]
    app_hash = ident["apphash"]
    sessionString = ident["session"]

    tg = Telegram(app_id, app_hash, sessionString)
    peer = tg.ResolvePeerByUsername(ident["username"])
    print(peer)
  
    for i in peer.History():
        if i.User:
            i.User.Resolve()
        print(i)



