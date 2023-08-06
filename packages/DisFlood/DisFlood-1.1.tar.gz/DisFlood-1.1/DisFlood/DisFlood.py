from discontrol.Client import Client
from discontrol.Message import Message
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
        for i in range(0,self.CountMessages):
            for ii in range(0,self.CountMessagesForInterval):
                if len(Messages) > self.CountMessages - 1:
                    return
                Messages.append(self.Client.send_message(self.ChannelId,Content,ReturnMessages)) 
            if len(Messages) > self.CountMessages - 1:
                    return
            time.sleep(self.Interval)
        return Messages
        


