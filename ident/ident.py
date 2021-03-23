
import select
import pickle
import json
import codecs
import base64
from os import urandom
from hashlib import md5
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text
from sys import stdout
import traceback

from Listener.listener import listen
from Relay.relay import Relay_Server
from Flags import flags
from TxRx.message import Message
from Chromos import Chromos
o = Chromos()

class IDENT():
    '''
    Client Identification Module
    Handles all transactions with the Client
    '''
    __msgidlen = 8
    def __init__(self,
        username: 'Client Username',
        soc: 'Socket',
        enc: 'TSE Instance',
        CPub: 'Client Public Key',
        server_obj: 'Server Object'):
        '''
        Args:
            username: str - Client's Username
            soc: socket
            enc: TSE Instance
            CPub: Client's Public Key
            server_obj: server object
        '''
        super().__init__()

        self.username = username # client username
        self.server_username = server_obj.username # server username
        self.s = soc
        self.HOST = self.s.getpeername()[0]
        self.PORT = self.s.getpeername()[1]
        self.e = enc
        self.sque = {}
        self.cpub = CPub
        self.server_obj = server_obj
        self.clients = server_obj.clients
        self.listen_obj = None
        self.relay_obj = None
        self.message = Message({self.username: enc}, self.sque)

        self.connected = [str(self.username), str(self.server_username)]

        self.__rstyle = Style.from_dict({
            '': '#00eb00 bold',
            'username':'#0091ff',
            'at':'white',
            'host':'#ed9a00',
            'prompt': '#ff0000 bold',
            'msg': "#00eb00 bold"
        })
        self.auto_recv()

    def __repr__(self):
        try:
            return '[\x1b[1;34m%s\x1b[0m]'.join(['<', ' username=', ' _closed=', ' laddr=', 'raddr', '>']) % ('Ident Instance', str(self.username), str(self.s._closed), str(self.s.getsockname()), str(self.s.getpeername()))
        except OSError:
            return '[\x1b[1;34m%s\x1b[0m]'.join(['<', ' username=', ' _closed=']) % ('Ident Instance', str(self.s._closed))

    def ident(self):
        print(o.red("User: "), self.user)
        print(o.red("Host: "), self.host)
        print(o.red("Port: "), self.port)

    def forward(self, msg: 'Message', from_user: 'Sender Username')->bool:
        packet_pickle = base64.b64encode(self.message.cover(from_user=str(from_user), to_user=str(self.username), msg=msg).encode())
        self.s.sendall(packet_pickle)
        self.s.sendall(flags.FLAG_PACKET_COMPLETE)
        return True
    
    def forward_pack(self, pack):
        print(pack)
        self.s.sendall(base64.b64encode(pack))
        self.s.sendall(flags.FLAG_PACKET_COMPLETE)

    def send(self, msg: 'Message')->bool:       
        packet_pickle = base64.b64encode(self.message.cover(from_user=str(self.server_username), to_user=str(self.username), msg=msg).encode())
        self.s.sendall(packet_pickle)
        self.s.sendall(flags.FLAG_PACKET_COMPLETE)

        return True

    def ackrecv(self, msgid) -> bool:
        pack = self.message.ackowledge(msgid=msgid, from_user=str(self.connected[1]), to_user=str(self.connected[0]), encryptor=None)
        pack = base64.b64encode(pack.encode())
        try:
            self.s.sendall(pack)
            self.s.sendall(flags.FLAG_PACKET_COMPLETE)
            return True
        except OSError:
            traceback.print_exc()
            o.error_info("Connection Collapsed;")
        except BrokenPipeError:
            traceback.print_exc()
            o.error_info("Connection Collapsed;")
        except Exception as exc:
            traceback.print_exc()

    def auto_recv(self, stop=False)->None:
        if(stop):
            self.listen_obj.stop()
            return
        self.listen_obj = listen(self, 4, parser=self.parser)
        # CHK
        self.listen_obj.start()
        return

    def __set_up_e2e(self, timeout=30)->None:
        msg = flags.FLAG_SEND_E2E_KEY + self.server_obj.clients[self.connected[1]].cpub.decode() + flags.FLAG_SEND_E2E_KEY
        self.forward(msg, from_user=self.connected[1])
        rs, _, _ = select.select([self.s], [], [], timeout)
        if(rs):
            self.server_obj.clients[self.connected[1]].forward(flags.FLAG_RECV_E2E_KEY + self.receive(True)[0] + flags.FLAG_RECV_E2E_KEY, from_user=self.connected[0])
            self.listen_obj.stop()
            self.server_obj.clients[self.connected[1]].listen_obj.stop()
            self.relay_msgs()
        else:
            o.error_info("TSE Key Not Recved!") 
        return
    
    def set_up_e2e(self, timeout=30)->None:
        msg = flags.FLAG_SEND_E2E_KEY + self.server_obj.clients[self.connected[1]].cpub.decode() + flags.FLAG_SEND_E2E_KEY
        msg, tag, nonce = self.e.encoder(msg)
        pack =  {
            "msgid": urandom(self.__msgidlen).hex(),
            "encfv": 'None',
            'content-type': 'key',
            'seq': 0,
            'nonce': nonce,
            "From": str(self.server_username),
            "To": str(self.username),
            "msg": msg,
            'tag': tag,
            "md5sum": md5(msg.encode()).hexdigest(),
            "Forwarded": 'True'
            }
        pack = json.dumps(pack).encode()
        self.forward_pack(pack)

        rs, _, _ = select.select([self.s], [], [], timeout)
        if(rs):
            # self.server_obj.clients[self.connected[1]].forward(flags.FLAG_RECV_E2E_KEY + self.s.recv(4096) + flags.FLAG_RECV_E2E_KEY, from_user=self.connected[0])
            pack = self.s.recv(40960)
            self.clients[self.connected[1]].forward_pack(pack)
            self.listen_obj.stop()
            self.server_obj.clients[self.connected[1]].listen_obj.stop()
            self.relay_msgs()
        else:
            o.error_info('TSE Key Not Recved!') 
        return

    def receive(self, __rtn__=False):
        timeout = 0
        ready_sockets, _, _ = select.select([self.s], [], [], timeout)
        packet_pickle = b''
        if(ready_sockets):
            '''
            [!] Boot Loop, on closed connection
            
            while(ready_sockets):
                packet_pickle += self.s.recv(40960)
                ready_sockets, _, _ = select.select([self.s], [], [], timeout)
            '''
            packet_pickle = self.s.recv(40960)
            ready_sockets, _, _ = select.select([self.s], [], [], timeout)
            
            while(ready_sockets):
                pp = self.s.recv(4096)
                ready_sockets, _, _ = select.select([self.s], [], [], timeout)
                packet_pickle += pp
                if(pp==b''):
                    break
                elif(flags.FLAG_PACKET_COMPLETE in packet_pickle):
                    break
            packets = packet_pickle.split(flags.FLAG_PACKET_COMPLETE)        
            try:
                while(b'' in packets):
                    packets.remove(b'')
            except:
                pass
            __msgs = []
            if(packets==[b'']):
                return
            __data = ''
            for packet_pickle in packets:
                self.recv_packet = base64.b64decode(packet_pickle)
                __from, __to, __data = self.message.uncover(self.recv_packet)
                __rmessage = FormattedText([
                        ('class:username', __from),
                        ('class:at',       '@'),
                        ('class:host',     'cliser'),
                        ('class:prompt',    '> '),
                        ('class:msg', str(__data))
                    ])

                stdout.write('\n')
                print_formatted_text(__rmessage, style=self.__rstyle, end='')
                stdout.write('\n')
                stdout.flush()
                __msgs.append(__data)

                if(__data=='q!' or __data==''):
                    self.s.close()
                    return ["Closing Regards "]

                elif(__data[:11]=='/connect to'):
                    stdout.write("Connecting to " + __data[12:])
                    stdout.flush()
                    if(__data[12:] in self.server_obj.clients):
                        self.connected[1] = __data[12:]
                        if(self.server_obj.clients[__data[12:]].connected[-1] != str(self.username)):
                            self.server_obj.clients[__data[12:]].send(str(self.username) + " wants to talk to you! Ack!")
                            self.send("Waiting for " + __data[12:] + "'s reply" )
                        else:     
                            self.set_up_e2e()
                    else:
                        self.send("Counter Client Not Found!")
                
                elif(__data=="/clients"):
                    self.send(str(list(self.clients.keys())))

                elif(__data=="/who"):
                    self.send(str(self.server_obj.username))

            if(__rtn__):
                return __msgs

        return
   
    def parser(self, __data, fromuser=None, pack=None)->None:
        if(not __data):
            if(pack):
                self.forward(pack)
                return

        if(__data == '/who'):
            self.send(str(self.server_username))
        elif(__data=="/clients"):
            self.send(str(list(self.clients.keys())))

        elif(__data[:11]=="/connect to"):
            stdout.write("Connecting to " + __data[12:])
            stdout.flush()
            if(__data[12:] in self.clients):
                self.connected[1] = __data[12:]
                if(self.clients[__data[12:]].connected[-1] != str(self.username)):
                    self.clients[__data[12:]].send(str(self.username) + " wants to talk to you! Ack!")
                    self.send("Waiting for " + __data[12:] + "'s reply" )
                else:     
                    self.set_up_e2e()
            else:
                self.send("Client Not Found!")

        return
    
    def _single_RelayMsg(self):
        self.server_obj.clients[self.connected[1]].s.send(self.s.recv(4096*2))
        return

    def reset_connection(self):
        try:
            self.relay_obj.stop()
        except Exception as exc:
            o.error_info("Relay is Alive!")
            pass
        try:
            self.listen_obj.start()
        except Exception as exc:
            o.error_info("Connection w/ " + self.connected[0] + " collpsed!")
            pass
        try:
            self.server_obj.clients[self.connected[1]].listen_obj.start()
        except Exception as exc:
            o.error_info("Connection w/ " + self.connected[1] + " collpsed!")
            pass

    def relay_msgs(self):
        self.relay_obj = Relay_Server(self.s, self.server_obj.clients[self.connected[1]].s, self.server_obj)
        try:
            self.relay_obj.start()
        except BrokenPipeError:
            self.reset_connection()
            pass
        except Exception as exc:
            traceback.print_exc()
            pass
        
    def stop(self):
        if(self.listen_obj):
            if(self.listen_obj.is_alive()):
                self.listen_obj.stop()
        if(self.relay_obj):
            if(self.relay_obj.is_alive()):
                self.relay_obj.stop()
        try:
            self.send('q!')
        except:
            pass
        if(not self.s._closed):
            self.server_obj.shutdown_request(self.s)
        self.server_obj.clients.pop(str(self.username))
        o.info(str(self.username) + " DC'ed")
        return

    pass
