
import sys
import pickle
import json
import codecs
import base64
import select
import traceback
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text
import re

from Flags import flags
from Listener.listener import listen
import Chromos
o = Chromos.Chromos()

class send_rec():
    """
    Tx Rx Class
    """
    def __init__(self):
        super(send_rec, self).__init__()
        self.__rectify_json = re.compile('(?<!\\\\)\'')
        self.s = None
        # self.spacket = {
        #             "From":str(self.username),
        #             "To":str(self.connectedto),
        #             "msg":"",
        #             "MD5SUM":""
        #             }
        # self.rpacket = {
        #             "From":str(self.connectedto),
        #             "To":str(self.username),
        #             "msg":"",
        #             "MD5SUM":""
        #             }
        self.e = None
        self.__rstyle = Style.from_dict({
            '': '#00eb00 bold',
            'username':'#0091ff',
            'at':'white',
            'host':'#ed9a00',
            'prompt': '#ff0000 bold',
            'msg': "#00eb00 bold"
        })

        return

    def _traditional_send(self, msg):
        msg = self.e.encoder(msg)
        self.s.sendall(msg.encode())

        return True

    def send(self, msg, encryptor=None):
        try:
            pack = self.message.cover(from_user=str(self.username), to_user=str(self.connectedto), msg=msg, encryptor=encryptor)
            pack = base64.b64encode(pack.encode())
        except AttributeError:
            o.error_info("Connection not yet established!")
        except:
            traceback.print_exc()
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

        return False

    def ackrecv(self, msgid) -> None:
        try:
            pack = self.message.ackowledge(msgid=msgid, from_user=str(self.username), to_user=str(self.connectedto), encryptor=None)
            pack = base64.b64encode(pack.encode())
        except AttributeError:
            o.error_info("Connection not yet established!")
        except:
            traceback.print_exc()
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


    def sendto(self, __username, msg):
        try:
            msg = self.encs[__username].encoder(msg)
            self.spacket["msg"] = msg       
            # packet_pickle = codecs.encode(pickle.dumps(self.spacket), "base64")
            packet_pickle = base64.b64encode(pickle.dumps(self.spacket))
            self.s.sendall(__username.encode() + b':**:' + packet_pickle)
            self.s.sendall(flags.FLAG_PACKET_COMPLETE)
            return True
        except KeyError: 
            o.error_info("UNF! No user Found!")
        except OSError:
            o.error_info("Connection Collapsed;")
        except BrokenPipeError:
            o.error_info("Connection Collapsed;")
        except Exception as exc:
            traceback.print_exc()

        return False

    def _traditional_receive(self):
        print(o.blue(" Receiving Message .... "))
        data = self.s.recv(4096)
        data = data.decode()
        data = self.e.decoder(data)
        print(o.red(" Receieved Message: " + data))

        if(data=="q!" or data==""):
            return False

        return True

    def receive(self, __rtn__=False):
        timeout = 0
        ready_sockets, _, _ = select.select([self.s], [], [], timeout)
        packet_pickle = b''
        self.__crlives = 4
        if(ready_sockets):
            """
            [!] Boot Loop, on closed connection
            
            while(ready_sockets):
                packet_pickle += self.s.recv(4096)
                ready_sockets, _, _ = select.select([self.s], [], [], timeout)
            """
            packet_pickle = self.s.recv(4096)
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
            try:
                __data = ''
                for packet_pickle in packets:
                    # self.rpacket = pickle.loads(codecs.decode(packet_pickle, "base64"))
                    # self.rpacket = json.loads(codecs.decode(packet_pickle, "base64"))
                    self.rpacket = json.loads(base64.b64decode(packet_pickle))
                    __data = self.rpacket["msg"]
                    __data = self.e.decoder(__data)

                __rmessage = FormattedText([
                    ('class:username', self.rpacket['From']),
                    ('class:at',       '@'),
                    ('class:host',     'cliser'),
                    ('class:prompt',    '> '),
                    ('class:msg', str(__data))
                        ])

                sys.stdout.write('\n')
                print_formatted_text(__rmessage, style=self.__rstyle, end='')
                sys.stdout.write('\n')
                sys.stdout.flush()
                __msgs.append(__data)

                if(__data == "q!" or __data == ""):
                    return ["Closing Regards "]
                
                elif(flags.FLAG_SEND_E2E_KEY in __data):
                    cpub_s = __data.split(flags.FLAG_SEND_E2E_KEY)[1] # Spouse CPUB
                    self.setup_e2e_tse_send(cpub_s.encode(), fromuser=self.rpacket['From'])

                elif(flags.FLAG_RECV_E2E_KEY in __data):
                    __key = __data.split(flags.FLAG_RECV_E2E_KEY)[2]
                    self.setup_e2e_tse_recv(__key.encode(), fromuser=self.rpacket['From'])

                elif(__data == "/who"):
                    self.send(str(self.username))
            
            except:
                sys.stdout.write(o.red("Decoding Failed!"))
                sys.stdout.flush()
                self.__crlives -= 1
                if(self.__crlives<=0):
                    o.error_info("Receiver fatally died!")
                    return
                raise OSError       # No Life

            if(__rtn__==True):
                return __msgs

        return

    def parser(self, __data, fromuser, pack=None):
        if(not __data):
            if(pack):
                __tse_status_ex = ['setup_e2e_tse_send', 'setup_e2e_tse_recv',]
                print(getattr(self, __tse_status_ex[json.loads(pack)['seq']]))
                pack = json.loads(pack)
                getattr(self, __tse_status_ex[pack['seq']])(pack)
                # self.setup_e2e_tse_recv(pack)
                return

        # if(flags.FLAG_SEND_E2E_KEY in __data):
        #     cpub_s = __data.split(flags.FLAG_SEND_E2E_KEY)[1] # Spouse CPUB
        #     self.setup_e2e_tse_send(cpub_s.encode(), fromuser=fromuser)

        # elif(flags.FLAG_RECV_E2E_KEY in __data):
        #     __key = __data.split(flags.FLAG_RECV_E2E_KEY)[2]
        #     self.setup_e2e_tse_recv(__key.encode(), fromuser=fromuser)

        elif(__data == "/who"):
            self.send(str(self.username))

        return
        
    def analyze_last_msg(self):
        return self.listen_obj.recv_packet

    def auto_recv(self, stop=False):
        if(stop):
            self.listen_obj.stop()
            return
        self.listen_obj = listen(self, 4, parser=self.parser, single_encoder=False)
        self.listen_obj.start()

    def clear_recv_line(self):
        rs, _, _ = select.select([self.s], [], [], 0)
        while(rs):
            _d_ = self.s.recv(4096000)
            rs, _, _ = select.select([self.s], [], [], 0)        
        return
 
    pass

