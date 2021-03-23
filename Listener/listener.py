
from threading import Thread, Lock
from sys import stdout
import select
import json
import base64
import traceback
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text

from Flags import flags
import Chromos
o = Chromos.Chromos()

class listener_nonrecver(Thread):
    '''
    Listener calls cliser receiver
    '''
    def __init__(self, cliser_object, timeout):
        super(listener_nonrecver, self).__init__()

        self.cliser_obj = cliser_object
        self.request = cliser_object.s
        self.timeout = timeout
        self.__stop = False
        self.__lives = 4
        self.lock = Lock()
        
        return

    def run(self):
        self.lock.acquire()
        while self.lock.locked():
            try:
                ready_sockets, _, _ = select.select([self.request], [], [], self.timeout)
                if(ready_sockets): self.cliser_obj.receive()
                if(self.__stop==True):
                    o.error_info("Listener Died!")
                    break
            except Exception as exc:
                self.__lives -= 1
                print('Lives:', self.__lives)
                traceback.print_exc()
                if(self.__lives<=0):
                    self.lock.release()
                    o.error_info('Recv Lives ended! Requires Rebirth!')
                    return
                pass
        return

    def stop(self):
        self.lock.release()
        self.__stop = True

    pass

class listen(Thread):
    '''
    Standalone Listener
    '''
    def __init__(self, cliser_obj, timeout, parser=None, single_encoder=False):
        super(listen, self).__init__()
        
        self.cliser_obj = cliser_obj
        self.s = cliser_obj.s
        self.sque = cliser_obj.sque
        self.ackrecv = cliser_obj.ackrecv
        self.timeout = timeout
        self.timeout2 = 0.01
        self.__stop = False
        self.__lives = 4
        self.lock = Lock()
        self.parser = parser
        self.message = cliser_obj.message
        self.__rstyle = Style.from_dict({
            '': '#00eb00 bold',
            'username':'#0091ff',
            'at':'white',
            'host':'#ed9a00',
            'prompt': '#ff0000 bold',
            'msg': "#00eb00 bold"
        })
        self.single_encoder = single_encoder
        self.daemon = True

        return

    def run(self):
        self.lock.acquire()
        while self.lock.locked():
            try:
                ready_sockets, _, _ = select.select([self.s], [], [], self.timeout)
                if(ready_sockets):
                    packet_pickle = b''
                    while(ready_sockets):
                        pp = self.s.recv(40960)
                        ready_sockets, _, _ = select.select([self.s], [], [], self.timeout2)
                        packet_pickle += pp
                        if(pp==b''): break
                        elif(flags.FLAG_PACKET_COMPLETE in packet_pickle): break
                    packets = packet_pickle.split(flags.FLAG_PACKET_COMPLETE)        
                    try:
                        while(b'' in packets):
                            packets.remove(b'')
                    except:
                        pass

                    __msgs = []
                    
                    if(packets==[b'']): return
                    __data = ''
                    for packet_pickle in packets:
                        self.recv_packet = base64.b64decode(packet_pickle)
                        content, msgid, __from, __to, __data = self.message.uncover(self.recv_packet)
                        if(content == 'text'): 
                            self.ackrecv(msgid)
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

                            # Parse Now
                            if(self.parser):
                                self.parser(__data, fromuser=__from)
                                    
                            if(__data == 'q!'):
                                # self.lock.release()
                                self.__stop = True
                                self.cliser_obj.stop()

                        elif(content == 'key'):
                            if(self.parser): self.parser('', fromuser='', pack=self.recv_packet)

                if(self.__stop):
                    o.error_info("Listener Died!")
                    break

            except Exception as exc:
                self.__lives -= 1
                print("Lives:", self.__lives)
                traceback.print_exc()
                if(self.__lives<=0):
                    self.lock.release()
                    o.error_info("Recv Lives ended! Requires Rebirth!")
                    return
                pass
    
    def stop(self):
        self.lock.release()
        self.__stop = True

    pass
