from discontrol.Client import Client
from discontrol.Message import Message
from random import randint
import time
class DisFlood:
    def __init__(self,client : Client):
        self.Client : Client = client
        self.ChannelId : int = 0
        self.Interval : float = 0
        self.CountMessagesForInterval : int = 10
        self.CountMessages : int = 0
    def SetChannel(self,ChannelId : int):
        self.ChannelId = ChannelId
    def SetInterval(self,Interval : float):
        self.Interval = Interval
    def SetCountMessages(self,CountMessages : int):
        self.CountMessages = CountMessages
    def SetCountMessagesForInterval(self, CountMessagesForInterval : int):
        self.CountMessagesForInterval = CountMessagesForInterval
    def Flood(self,Content : str,ReturnMessages : bool=False):
        Messages = []
        md = 0
        for i in range(0,self.CountMessages):
            for ii in range(0,self.CountMessagesForInterval):
                if md > self.CountMessages - 1:
                    return
                md+=1
                Messages.append(self.Client.send_message(self.ChannelId,Content.replace("!rand!",f"{randint(0,10000)}"),ReturnMessages)) 
            if md > self.CountMessages - 1:
                    return
            time.sleep(self.Interval)
        return Messages
        


