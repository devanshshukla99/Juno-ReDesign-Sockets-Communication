# Base for Server-Client Sockets

import select
from threading import Thread, Lock
from hashlib import md5 
from os import urandom
import json
from sys import stdout
from base64 import b64encode, b64decode

from Flags import flags

class LockedThread(Thread):
    lock = Lock()
    def __init__(self, target, args=()):
        Thread.__init__(self, target=target, args=args + (self.lock, ))
        self.daemon = True
        return
    pass

class SocketsBase:

    def __init__(self):
        return

    def prt(self):
        print(self)

    @property
    def pack(self):
        return self._pack

    @pack.setter
    def pack(self, value):
        '''
        to_user: 'To', msg: 'Message'
        value := (to, msg, encryptor)
        '''        
        to_user = value[0] or str(self.connectedto)
        msg = value[1]
        encryptor = value[2]
        from_user = str(self.username)
        if(not encryptor): encryptor = self.__get_encoder(from_user=from_user, to_user=to_user)
        if(encryptor):
            msg, tag, nonce = encryptor.encoder(msg)
            self._pack =  {
                "msgid": urandom(self.__msgidlen).hex(),
                "encfv": encryptor.version(),
                'content-type': 'text',
                'nonce': nonce,
                "From": from_user,
                "To": to_user,
                "msg": msg,
                'tag': tag,
                "md5sum": md5(msg.encode()).hexdigest(),
                "Forwarded": str(None)
                }
        return

    def send(self, msg:str, to=None):
        self.pack = (to, msg, '')
        msg = b64encode(json.dumps(self.pack).encode())
        self.sendall(msg)
        self.sendall(flags.FLAG_PACKET_COMPLETE)
        self.sque[self.pack['msgid']] = None
        return

    def acksend(self, pack):
        msg = 'RAck!'
        to_user = pack['From'] or str(self.connectedto)
        from_user = str(self.username)
        encryptor = self.__get_encoder(from_user=from_user, to_user=to_user)
        msg, tag, nonce = encryptor.encoder(msg)
        _ackpack =  {
            "msgid": pack['msgid'],
            "encfv": encryptor.version(),
            'content-type': 'ack',
            'nonce': nonce,
            "From": from_user,
            "To": to_user,
            "msg": msg,
            'tag': tag,
            "md5sum": md5(msg.encode()).hexdigest(),
            }
        self.sendall(b64encode(json.dumps(_ackpack).encode()))
        self.sendall(flags.FLAG_PACKET_COMPLETE)
        return

    def listen(self):
        t = LockedThread(target=self.__recv_listener, args=(0.5, ))
        self.threads.append(t)
        t.start()
        return

    def __get_encoder(self, from_user, to_user):
        encoders = list(self.encs.values())
        if(from_user in encoders): return self.encs[from_user]
        elif(to_user in encoders): return self.encs[to_user]
        return encoders[0]

    def recv_pack(self, timeout:int=0):
        _recv = b''
        rs, _, _ = select.select([self], [], [], timeout)
        while(rs):
            _recv = b''.join([_recv, self.recv(40960)])
            rs, _, _ = select.select([self], [], [], timeout)
        _recv = _recv.split(flags.FLAG_PACKET_COMPLETE)
        _recv.remove(b'')
        for pack in _recv:
            pack = json.loads(b64decode(pack).decode())
            if(pack['content-type'] == 'ack'):
                self.sque.pop(pack['msgid'])
            elif(pack['content-type'] == 'text'):
                self.rque.put(pack)
                self.acksend(pack)
        return

    def __recv_listener(self, timeout:int, lock):
        lock.acquire()
        while(lock.locked()):
            _recv = b''
            rs, _, _ = select.select([self], [], [], timeout)
            while(rs):
                _recv = b''.join([_recv, self.recv(40960)])
                rs, _, _ = select.select([self], [], [], timeout)
                if(not lock.locked()): return
            _recv = _recv.split(flags.FLAG_PACKET_COMPLETE)
            _recv.remove(b'')
            for pack in _recv:
                pack = json.loads(b64decode(pack).decode())
                if(pack['content-type'] == 'ack'):
                    self.sque.pop(pack['msgid'])
                elif(pack['content-type'] == 'text'):
                    self.rque.put(pack)
                    self.acksend(pack)
        return

    def unpack(self, pack):
        if(md5(pack['msg'].encode()).hexdigest() == pack['md5sum']):
            from_user = pack['From']
            to_user = pack['To']
            encryptor = self.__get_encoder(from_user=from_user, to_user=to_user)
            if(pack['content-type'] == 'text'): return pack['content-type'], pack['From'], pack['To'], encryptor.decoder(pack['msg'], pack['tag'], pack['nonce'])
            elif(pack['content-type'] == 'key'): return pack['content-type'], pack['From'], pack['To'], ''
        else:
            raise SystemError
        return None, None, None, None
    
    pass