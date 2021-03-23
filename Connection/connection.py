# Program for Connection Setup

# Depreciated

raise DeprecationWarning

import os
from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib
from Crypto.Cipher import PKCS1_OAEP, AES
import select

from TSE import tse
from Flags import flags
from Chromos import Chromos
o = Chromos()

class Connection():

    def __init__(self, conn):
        self.server_keys_path = "./SKeys/"
        self.client_keys_path = "./CKeys/"

        self.conn = conn
        self.timeout = 2
        return

    def load_keys(self, path, prefix='')->None:
        path = ''.join([path, '/', prefix])
        if(os.path.isfile(path +"public.key") is False or os.path.isfile(path + "private.key") is False): self.generate_key(path, prefix)
        with open(''.join([path, "public.key",]), 'r') as f:
            public = f.read().encode()
        with open(''.join([path, "private.key"]), 'r') as f: 
            private = f.read().encode()
        return public, private

    def load_key(self, keypath):
        f = open(keypath, "r")
        key = f.read().encode()
        f.close()
        return key

    def generate_key(self, path, prefix):
        random = Random.new().read
        RSAKey = RSA.generate(1024, random)

        public = RSAKey.publickey().exportKey()
        private = RSAKey.exportKey()

        with open(path + prefix + "public.key", "w") as f:
            f.write(public.decode())
            f.flush()
        with open(path + prefix + "private.key", "w") as f:
            f.write(private.decode())
            f.flush()

        o.info_y("RSA Keys Generated! ")

        return True

    def rand_gen(self, n):
        return str(int.from_bytes(os.urandom(n), byteorder='big'))

    def ret_hash(self, __data):
        return hashlib.md5(__data).hexdigest().encode()

    def ret_enc(self, __key):
        __RSAKey = RSA.importKey(__key)
        return PKCS1_OAEP.new(__RSAKey)

    def connection_setting_server(self, username):
        SPub, SPri = self.load_keys(self.server_keys_path)
        hashSPub = self.ret_hash(SPub)
        rs, _, _ = select.select([self.conn], [], [], self.timeout)
        if(rs):
            data = self.conn.recv(4096)
            __data_splt_temp = data.split(b':0:')
            if(__data_splt_temp == [data] or len(__data_splt_temp) < 2): return False, 0, []

            CPub = __data_splt_temp[0]
            tmp_hashSPub = __data_splt_temp[1]
            if(tmp_hashSPub==hashSPub):
                session = self.rand_gen(8).encode()
                __aes = os.urandom(16)  # AES Key
                __enc = tse.Key(aeskey=__aes)   # Transport Security Encryption
                re_auth = __enc.exportKey().encode() # TSE

                hashCPub = self.ret_hash(CPub)
                encryptor = self.ret_enc(CPub)

                self.conn.sendall(b''.join([encryptor.encrypt(b''.join([hashCPub, b':0:', session, b':0:', __aes])), b':0:', re_auth]))

                session = self.ret_hash(session)
                re_auth = self.ret_hash(re_auth)

                rs, _, _ = select.select([self.conn], [], [], self.timeout)
                if(rs):
                    Get = self.conn.recv(4096).split(b':0:')

                    tmp_session = Get[0]
                    tmp_re_auth = Get[1]

                    if(tmp_session == session):
                        # print("session matched")
                        if(tmp_re_auth == re_auth):
                            # print("re_auth matched")
                            # Exchange Usernames 
                            encryptor = self.ret_enc(CPub)
                            self.conn.sendall(encryptor.encrypt(''.join([flags.USERNAME_PREFIX_POSTFIX, str(username), flags.USERNAME_PREFIX_POSTFIX]).encode()))
                            
                            decryptor = self.ret_enc(SPri)
                            data = self.conn.recv(4096)
                            data = decryptor.decrypt(data)

                            __susername = data.split(flags.USERNAME_PREFIX_POSTFIX.encode())[1].decode()
                            print(__susername)

                            return True, __enc, CPub, __susername
        print('Failed!')
        return False, 0, []

    def connection_setting_client(self, username):
        CPub, CPri = self.load_keys(self.client_keys_path, "client_")
        if(os.path.isfile(self.client_keys_path + "public.key")==False):
            o.error_info("Server Public Key Not Found! ")
            raise FileNotFoundError

        SPub = self.load_key(self.client_keys_path + "public.key")

        hashSPub = self.ret_hash(SPub)
        hashCPub = self.ret_hash(CPub)

        self.conn.sendall(CPub + b':0:' + hashSPub)

        rs, _, _ = select.select([self.conn], [], [], self.timeout)
        if(rs):
            Get = self.conn.recv(4096)

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
                
                self.conn.sendall(b''.join([session, b':0:', re_auth]))

                # Exchange Usernames and UIDs
                encryptor = self.ret_enc(SPub)
                self.conn.sendall(encryptor.encrypt(''.join([flags.USERNAME_PREFIX_POSTFIX, str(username), flags.USERNAME_PREFIX_POSTFIX]).encode()))

                decryptor = self.ret_enc(CPri)
                data = self.conn.recv(4096)
                data = decryptor.decrypt(data)

                __susername = data.split(flags.USERNAME_PREFIX_POSTFIX.encode())[1].decode()
                print(__susername)

                return True, tse.Key(aeskey=__aes, key=__enckey), __susername
        print('Failed!')
        return False, None, ''

    pass
