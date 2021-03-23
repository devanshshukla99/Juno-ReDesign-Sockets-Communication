#Program to read and write password with decryption key

from numpy import sin, cos, tan, array, unique
from itertools import permutations
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

class encf6:
    """
    Encoder Function 6
    """
    def __init__(self, key:'TSE Key', aeskey:'AES Key'):
        # super(encf6, self).__init__()

        self.n = 0
        self.__k1 = key
        self.__k2 = self.__k1[::-1]
        self.__keylen = self.__k1.size
        self.__aeskey = aeskey

        self.__splt = None
        self.ver_splitter = "v2"

        self.get_splitter()

        return

    def __repr__(self) -> str:
        return ''.join(['<', 'encf6 ', '(', self.ver_splitter, ')', ' Instance @', str(hex(id(self))), ' n(', str(self.__k1.size), ')', '>'])

    def get_splitter(self) -> None:
        if(self.ver_splitter=='v2'): self.__new_splitter()
        elif(self.ver_splitter=='v1'): self.__old_splitter()
        else: print("\n\033[1;31m[\033[1;34m!\033[1;31m] \033[1;31mError, Splitter of specified version not Found! ")
        return

    def version(self) -> str:
        return '_'.join(['encf6', self.ver_splitter])
        
    def __old_splitter(self, length_required=25):

        #Splt

        a1 = 0
        a2 = 0
        a3 = 0
        a4 = 0
        a5 = 0
        a6 = 0
        a7 = 0
        a8 = 0
        a9 = 0
        a10 = 0

        __splt = []

        k = 0
        l = 0
        m = 0

        for k in range(0, length_required):
            a1 = 0
            a2 = 0

            while(a1==0):
                a1 = str(self.__k1[m + l + k + 0]*self.__k1[m + l + k + 10]) + str(self.__k1[m + l + k + 10]*self.__k1[m + l + k + 20]) + str(self.__k1[m + l + k + 20]*self.__k1[m + l + k + 30]) + str(self.__k1[m + l + k + 30]*self.__k1[m + l + k + 40]*self.__k1[m + l + k + 50])
                a3 = a1[::-1]

                a5 = str(self.__k1[m + l + k + 20]*self.__k1[m + l + k + 30]) + str(self.__k1[m + l + k + 0]*self.__k1[m + l + k + 10]) +  str(self.__k1[m + l + k + 30]*self.__k1[m + l + k + 40]*self.__k1[m + l + k + 50]) + str(self.__k1[m + l + k + 10]*self.__k1[m + l + k + 20])
                a7 = a5[::-1]

                k += 1

            while(a2==0):
                a2 = str(self.__k2[m + l + k + 0]*self.__k2[m + l + k + 10]) + str(self.__k2[m + l + k + 10]*self.__k2[m + l + k + 20]) + str(self.__k2[m + l + k + 20]*self.__k2[m + l + k + 30]) + str(self.__k2[m + l + k + 30]*self.__k2[m + l + k + 40]*self.__k2[m + l + k + 50]) 
                a4 = a2[::-1]

                a6 = str(self.__k2[m + l + k + 20]*self.__k2[m + l + k + 30]) + str(self.__k2[m + l + k + 0]*self.__k2[m + l + k + 10]) + str(self.__k2[m + l + k + 30]*self.__k2[m + l + k + 40]*self.__k2[m + l + k + 50])  + str(self.__k2[m + l + k + 10]*self.__k2[m + l + k + 20]) 
                a8 = a6[::-1]

                k += 1

            __splt.append(str(a1))
            __splt.append(str(a2))
            __splt.append(str(a5))
            __splt.append(str(a6))

            __splt.append(str(a3))
            __splt.append(str(a4))
            __splt.append(str(a7))
            __splt.append(str(a8))

        k = 0
        l = 55
        m = 25

        for k in range(0, length_required):
            a1 = 0
            a2 = 0

            while(a1==0):
                a1 = str(self.__k1[m + l + k + 10]*self.__k1[m + l + k + 20]*self.__k1[m + l + k + 30]) + str(self.__k1[m + l + k + 0]*self.__k1[m + l + k + 10]) + str(self.__k1[m + l + k + 20]*self.__k1[m + l + k + 30]) + str(self.__k1[m + l + k + 40]*self.__k1[m + l + k + 50])
                a3 = a1[::-1]

                a5 = str(self.__k1[m + l + k + 20]*self.__k1[m + l + k + 30]) + str(self.__k1[m + l + k + 30]*self.__k1[m + l + k + 40]*self.__k1[m + l + k + 50]) + str(self.__k1[m + l + k + 10]*self.__k1[m + l + k + 20]) + str(self.__k1[m + l + k + 0]*self.__k1[m + l + k + 10]) 
                a7 = a5[::-1]

                k += 1

            while(a2==0):
                a2 = str(self.__k2[m + l + k + 10]*self.__k2[m + l + k + 20]*self.__k2[m + l + k + 30]) + str(self.__k2[m + l + k + 0]*self.__k2[m + l + k + 10]) + str(self.__k2[m + l + k + 20]*self.__k2[m + l + k + 30]) + str(self.__k2[m + l + k + 40]*self.__k2[m + l + k + 50]) 
                a4 = a2[::-1]

                a6 = str(self.__k2[m + l + k + 20]*self.__k2[m + l + k + 30]) + str(self.__k2[m + l + k + 30]*self.__k2[m + l + k + 40]*self.__k2[m + l + k + 50])  + str(self.__k2[m + l + k + 10]*self.__k2[m + l + k + 20]) + str(self.__k2[m + l + k + 0]*self.__k2[m + l + k + 10])
                a8 = a6[::-1]

                k += 1

            __splt.append(str(a1))
            __splt.append(str(a2))
            __splt.append(str(a5))
            __splt.append(str(a6))

            __splt.append(str(a3))
            __splt.append(str(a4))
            __splt.append(str(a7))
            __splt.append(str(a8))

        self.__splt = unique(array(__splt))

    def __new_splitter(self, length_required=1) -> None:
        kp1 = self.__k1[0:128]
        kp2 = self.__k1[128:256]

        __splt = []

        m1 = sin(max(kp1)/max(kp2)) 
        m2 = cos(max(kp1)/max(kp2)) + 1
        m3 = tan(max(kp1)/max(kp2))

        for p in range(0, length_required):
            v1 = '0'
            
            while(v1=='0' or v2=='0' or v3=='0' or v4=='0' or v5=='0' or v6=='0' or v7=='0' or v8=='0'):
                v1 = str(int(kp1[p + 0]*kp1[p + 20] * m1))
                v2 = str(int(kp2[p + 20]*kp2[p + 0] * m2))
                v3 = str(int(kp1[p + 0]*kp1[p + 40] * m3))
                v4 = str(int(kp2[p + 40]*kp2[p + 0] * m1))
                v5 = str(int(kp1[p + 20]*kp1[p + 40] * m2))
                v6 = str(int(kp2[p + 40]*kp2[p + 20] * m3))
                v7 = str(int(kp1[p + 0]*kp1[p + 60] * m1))
                v8 = str(int(kp2[p + 60]*kp2[p + 0] * m2))

                p += 1

            __values__ = [v1, v2, v3, v4, v5, v6, v7, v8]
            # __values__ = ['a', 'b', 'c', 'd', 'e', 'f']
            __original_array__ = array(list(permutations(__values__)))            
            # print(len(__original_array__))

            for __og_ar in __original_array__:
                __splt.append(''.join([
                    __og_ar[0], __og_ar[1], __og_ar[2], __og_ar[3], __og_ar[4], __og_ar[5], __og_ar[6], __og_ar[7]
                ]))

        self.__splt = unique(array(__splt)) 
        
        return

    def encoder(self, data:'Data to Encrypt (str)'):
        """
        Returns:
            Encrypted Data, Tag, Nonce
        """
        cipher = AES.new(self.__aeskey, AES.MODE_OCB)
        data, tag = cipher.encrypt_and_digest(data.encode())
        data = b64encode(data).decode()

        __trans_data = ''
        __new_data = ''
        __n = 0
        for i in range(0, len(data)):
            __trans_data = int((ord(data[i]) + self.__k1[__n]))
            __new_data += str(__trans_data + self.__k2[__n])
            __new_data += str(self.__splt[i])
            if(__n >= self.__keylen - 1): __n = 0
            __n += 1
        __n = 0

        return __new_data, b64encode(tag).decode(), b64encode(cipher.nonce).decode()

    def decoder(self, data:'Encrypted Data', tag:'Associated Tag', nonce:'Nonce') -> str:
        """
        Returns:
            Decrypted Data
        """
        tag = b64decode(tag.encode())
        nonce = b64decode(nonce.encode())

        __u = []
        __data = data.strip("\n")
        __u.append(data)

        __data = []
        __splt_len = self.__splt.size
        
        for i in range(0, __splt_len):
            __u = __u[-1].split(self.__splt[i])
            if(__u[0] == ''): break
            __data.append(__u[0])

        for i in range(0, __splt_len):
            for j in range(0, len(__u)):
                __u_ = __u[j].split(self.__splt[i])
                if(__u_[0] == ''): break
                __data.append(__u_[0])

        __new_data = ""
        __n = 0
        __data = array(__data, dtype=int)
        for __dataindex in __data:
            t = int(__dataindex - self.__k1[__n] - self.__k2[__n])
            if(t < 0): t=0
            if(__n >= self.__keylen - 1): __n = 0
            __new_data += chr(t)
            __n += 1
        __n = 0

        __new_data = b64decode(__new_data.encode())
        cipher = AES.new(self.__aeskey, AES.MODE_OCB, nonce=nonce)
        __new_data = cipher.decrypt_and_verify(__new_data, tag)
        
        return __new_data.decode()

    def encodef(self, file_name) -> None:
        file_ = open(file_name, "r")
        data = file_.read()
        file_.close()
        
        data = encoder(data)
        
        file_ = open(file_name, "w")
        file_.write(data)
        file_.write("\n")
        file_.close()

        return

    def decodef(self, file_name) -> None:
        data = ""
        
        file_ = open(file_name, "r")
        data = file_.read()
        
        new_data = self.decoder(data, __k1, __k2)
        print("*\n", new_data)

        return

    pass
