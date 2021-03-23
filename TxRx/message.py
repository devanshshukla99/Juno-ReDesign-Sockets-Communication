
from hashlib import md5
from os import urandom
import json
from sys import stdout
from Crypto.Cipher import AES
from Excs.exceptions import IllegalReceipt

class Message():
    """
    Class for formally addressing each msg an id with verification
    msgid: 8 character hex string unique to each packet
    """
    __msgidlen = 8
    _msg_history = []
    def __init__(self, encfs:'Encryptors', sque:'Send Queue') -> None:
        self._msg = ''
        self.encryptors = encfs
        self.sque = sque
        return

    def cover(self, from_user:'From', to_user:'To', msg:'Message', encryptor=None, forwarded:'is forwarded [F]'=False) -> str:
        if(not encryptor): encryptor = self.__get_encoder(from_user=from_user, to_user=to_user)
        msg, tag, nonce = encryptor.encoder(msg)
        pack =  {
            "msgid": urandom(self.__msgidlen).hex(),
            "encfv": encryptor.version(),
            'content-type': 'text',
            'nonce': nonce,
            "From": from_user,
            "To": to_user,
            "msg": msg,
            'tag': tag,
            "md5sum": md5(msg.encode()).hexdigest(),
            "Forwarded": str(forwarded)
            }

        self._msg_history.append(pack)
        self.sque[pack['msgid']] = None
        return json.dumps(pack)

    def __get_encoder(self, from_user:'From', to_user:'To'): # Username can be subbed for uid       
        if(to_user in self.encryptors): return self.encryptors[to_user]
        elif(from_user in self.encryptors): return self.encryptors[from_user]
        # stdout.write('\x1b[1;31mDefault encoder! \x1b[0m')
        # stdout.flush()
        return list(self.encryptors.values())[0]

    def uncover(self, pack, encryptor=None) -> None:
        """
        Function to verify and decode message
        """
        pack = json.loads(pack)
        if(md5(pack['msg'].encode()).hexdigest() == pack['md5sum']):
            self._msg_history.append(pack)
            if(not encryptor): encryptor = self.__get_encoder(from_user=pack['From'], to_user=pack['To'])
            nonce = pack['nonce']
            if(pack['content-type'] == 'text'): return pack['content-type'], pack['msgid'], pack['From'], pack['To'], encryptor.decoder(pack['msg'], pack['tag'], nonce)
            elif(pack['content-type'] == 'key'): return pack['content-type'], pack['msgid'], pack['From'], pack['To'], ''
            elif(pack['content-type'] == 'ack'): 
                if(pack['msgid'] in self.sque):
                    self.sque.pop(pack['msgid'])
                    return pack['content-type'], pack['msgid'], pack['From'], pack['To'], encryptor.decoder(pack['msg'], pack['tag'], nonce)
                raise IllegalReceipt
        return None, None, None, None

    def ackowledge(self, msgid, from_user:'From', to_user:'To', encryptor=None):
        if(not encryptor): encryptor = self.__get_encoder(from_user=from_user, to_user=to_user)
        msg, tag, nonce = encryptor.encoder('RAck!')
        pack =  {
            "msgid": msgid,
            "encfv": encryptor.version(),
            'content-type': 'ack',
            'nonce': nonce,
            "From": from_user,
            "To": to_user,
            "msg": msg,
            'tag': tag,
            "md5sum": md5(msg.encode()).hexdigest(),
            "Forwarded": 'False'
            }

        return json.dumps(pack)

    def verify(self, pack):
        """
        Function to verify message checksum
        """
        if(md5(pack['msg'].encode()).hexdigest() == pack['md5sum']):
            return True
        return False

    def print(self, pack):
        pack = json.loads(pack)
        pack['msg'] = '...'
        stdout.write('{:<1}{:<57}{:<1}'.format('+', '-'*57, '+') + '\n')
        for i in pack:
            stdout.write("{:<2}{:<8}{:^2}|{:^2}{:<32} {:<32}".format('|', i, '\t', '\t', pack[i], '|'))
            stdout.write('\n')
        stdout.write('{:<1}{:<57}{:<1}'.format('+', '-'*57, '+') + '\n')
        stdout.flush()

        return
