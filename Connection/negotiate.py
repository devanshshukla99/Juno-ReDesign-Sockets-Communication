#Program for Connection Setup
'''
Konnect In Server Sequence
'''
__all__ = ['OfferNegotiation', 'AcceptNegotiation']

# from os import urandom
from os.path import isfile
import select

from TSE import tse
from Flags import flags
from .base import NegotiationBase
from Chromos import Chromos
o = Chromos()

# Server
class AcceptNegotiation(NegotiationBase):
    '''
    Accept, if apt.
    '''
    server_keys_path = './SKeys/'

    def __repr__(self):
        return '<Accept-Negotiate Instance>'

    def authenticate(self, username:str, conn:'socket', timeout:float=0.5):
        SPub, SPri = self.load_keys(self.server_keys_path, prefix='')
        hashSPub = self.ret_hash(SPub)
        rs, _, _ = select.select([conn], [], [], timeout)
        if(rs):
            data = conn.recv(4096)
            __data_splt_temp = data.split(b':0:')
            if(__data_splt_temp == [data] or len(__data_splt_temp) < 2): return False, None, None, None
            CPub = __data_splt_temp[0]
            tmp_hashSPub = __data_splt_temp[1]
            if(tmp_hashSPub==hashSPub):
                session = self.rand_gen(8).encode()
                __aes = self.osurandom(16) # AES Key
                __enc = tse.Key(aeskey=__aes) # Transport Security Encryption
                re_auth = __enc.exportKey().encode() # TSE

                hashCPub = self.ret_hash(CPub)
                encryptor = self.ret_enc(CPub)
                
                conn.sendall(b''.join([encryptor.encrypt(b''.join([hashCPub, b':0:', session, b':0:', __aes])), b':0:', re_auth]))

                session = self.ret_hash(session)
                re_auth = self.ret_hash(re_auth)

                rs, _, _ = select.select([conn], [], [], timeout)
                if(rs):
                    Get = conn.recv(4096).split(b':0:')

                    tmp_session = Get[0]
                    tmp_re_auth = Get[1]

                    if(tmp_session == session):
                        # print("session matched")
                        if(tmp_re_auth == re_auth):
                            # print("re_auth matched")
                            # Exchange Usernames 
                            encryptor = self.ret_enc(CPub)
                            conn.sendall(encryptor.encrypt(''.join([flags.USERNAME_PREFIX_POSTFIX, str(username), flags.USERNAME_PREFIX_POSTFIX]).encode()))
                            
                            decryptor = self.ret_enc(SPri)
                            data = conn.recv(4096)
                            data = decryptor.decrypt(data)

                            __susername = data.split(flags.USERNAME_PREFIX_POSTFIX.encode())[1].decode()
                            print(__susername)

                            return True, __enc, CPub, __susername
        print('Failed!')
        return False, None, None, None

    pass

# Client
class OfferNegotiation(NegotiationBase):
    '''
    Offer
    '''
    client_keys_path = './CKeys/'

    def __repr__(self):
        return '<Offer-Negotiate Instance>'

    def authenticate(self, username:str, conn:'socket', timeout:float=0.5):
        CPub, CPri = self.load_keys(self.client_keys_path, prefix='client_')
        if(isfile(self.client_keys_path + 'public.key') is False):
            o.error_info("Server Public Key Not Found! ")
            raise FileNotFoundError

        SPub = self.load_key(''.join([self.client_keys_path, 'public.key']))

        hashSPub = self.ret_hash(SPub)
        hashCPub = self.ret_hash(CPub)

        conn.sendall(CPub + b':0:' + hashSPub)

        rs, _, _ = select.select([conn], [], [], timeout)
        if(rs):
            Get = conn.recv(4096)

            __cget_array = Get.split(b':0:')
            Get = __cget_array[0]
            re_auth = __cget_array[1]
            
            decryptor = self.ret_enc(CPri)
            Get = decryptor.decrypt(Get)
            
            __cget_array = Get.split(b':0:')

            tmp_hashCPub = __cget_array[0]
            session = __cget_array[1]
            __aes = __cget_array[2]

            if(tmp_hashCPub == hashCPub):
                __enckey = re_auth.decode()
                session = self.ret_hash(session)
                re_auth = self.ret_hash(re_auth)
                
                conn.sendall(b''.join([session, b':0:', re_auth]))

                # Exchange Usernames and UIDs
                encryptor = self.ret_enc(SPub)
                conn.sendall(encryptor.encrypt(''.join([flags.USERNAME_PREFIX_POSTFIX, str(username), flags.USERNAME_PREFIX_POSTFIX]).encode()))

                decryptor = self.ret_enc(CPri)
                data = conn.recv(4096)
                data = decryptor.decrypt(data)

                __susername = data.split(flags.USERNAME_PREFIX_POSTFIX.encode())[1].decode()

                return True, tse.Key(aeskey=__aes, key=__enckey), __susername
        print('Failed!')
        return False, None, ''

    pass
