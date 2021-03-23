
import threading
import select
import traceback
from queue import Queue
import json
import base64
import socket
from hashlib import md5
import warnings
from time import sleep
from sys import exit

from Connection.negotiate import OfferNegotiation
from Connection.base import NegotiationBase
from ident.username import Username
from TxRx.txrx import send_rec
from TxRx.message import Message
from Chromos import Chromos
o = Chromos()

class client(send_rec):
    '''
    Client Side Transactions handler class
    '''
    __msgidlen = 8
    def __init__(self,
        username:str=None, 
        HOST:str='localhost', 
        PORT:int=45284):

        self.HOST = HOST
        self.PORT = PORT
        self.s = None
        self.rque = Queue()
        self.sque = {}
        self.__key = None
        self.cpub, self.__cpri = NegotiationBase().load_keys(path='./CKeys', prefix='client_')
        self.connectedto = 'server'

        print(o.red(self.HOST +"/" + str(self.PORT)))

        self.username = Username(username=username)
        if(self.username is None): self.get_username()

        self.encs = {}
        self.message = Message(self.encs, self.sque)

        send_rec.__init__(self)
        return
    
    def __repr__(self):
        return '[\x1b[1;34m%s\x1b[0m]'.join(['<', ' username=', ' host=', ' port=', ' connectedto=', '>']) % ('Client Instance', str(self.username), self.HOST, str(self.PORT), str(self.connectedto))
        
    def get_username(self):
        username = input(o.red("Username: "))
        if(username):
            self.username = Username(username=username)
            return
        self.get_username()
        return

    def start(self):
        print(o.green('\nWelcome, to Client-Side Configuration Program'))

        self.connect()

    def connect(self)->bool:
        '''
        Connect Now!
        '''
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))

        o.info_y('Connected to Server at %s %d' % (self.HOST, self.PORT))
        try:
            flag, self.e, __username = OfferNegotiation().authenticate(username=str(self.username), conn=self.s)
            if(flag):
                o.info("Connection Live")
                __username = Username(UID=__username)
                self.encs[str(__username)] = self.e
                self.connectedto = __username
                self.auto_recv()
                return True
            o.error_info('Authentication Failed!')
        except BrokenPipeError:
            o.error_info('Pipe Broken during Authentication!')
        except ConnectionResetError:
            o.error_info('Connection Reset during Authentication!')
        except:
            traceback.print_exc()
            o.error_info('Beware! Authentication incomplete!\nBeware of MIM Attack!')
            self.stop()
        return False

    def disconnect(self)->bool:
        if(self.s._closed is False):
            try:
                self.send('q!')
            except AttributeError:
                o.error_info_b("Attribute Error, probably Encryptor is not initialised!")
            except BrokenPipeError:
                o.error_info("Disconnected!")
            finally:
                print(o.blue("Connection Closed from " + str(self.s.getsockname()[0]) + " at " + str(self.s.getsockname()[1])))
                self.s.close() 
                return True
        else: o.error_info_b('No Exising Connection!')
        return False

    def stop(self)->bool:
        try:
            if(self.listen_obj.is_alive()): self.listen_obj.stop()
        except:
            pass
        if(self.s):
            self.disconnect()   
        print(o.red('Client Shutdown Complete!'))
        return True

    pass

