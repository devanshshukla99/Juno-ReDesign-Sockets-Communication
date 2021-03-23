
import select
from threading import Lock, Thread
from Flags import flags
import Chromos
o = Chromos.Chromos()

class RelayServer():

    def __init__(self, CT):
        self.connected = CT

    def set_up_e2e(self):        
        self.clients[self.connected[0]].send(flags.FLAG_SEND_E2E_KEY + self.clients[self.connected[1]].cpub + flags.FLAG_SEND_E2E_KEY)

    pass

class Relay_Server(Thread):
    """
    Relay Thread
    """
    def __init__(self, c1, c2, server_obj, timeout=10):
        super(Relay_Server, self).__init__()

        self.c1 = c1
        self.c2 = c2
        self.server_obj = server_obj
        self.timeout = timeout
        self.__stop = False
        self.cli_corr = []          # [[self.c1, server_obj]]
        self.lock = Lock()

        # self.get_client_list_conf()

    def get_client_list_conf(self):

        clients = list(self.server_obj.clients.values())

        if(self.c1 == clients[0].s):
            self.cli_corr.append([self.c1, clients[0]])
            self.cli_corr.append([self.c2, clients[1]])
        elif(self.c1 == clients[1].s):
            self.cli_corr.append([self.c1, clients[1]])
            self.cli_corr.append([self.c2, clients[0]])
        else:
            o.error_info("relay_msgs Failed! ")
            self.cli_corr = []
        return

    def run(self):

        # if(self.cli_corr == []):
        #     return
        
        self.lock.acquire()
        while self.lock.locked():
            ready_sockets, _, _ = select.select([self.c1, self.c2], [], [], self.timeout)
            if(ready_sockets):
                for rs in ready_sockets:
                    if(rs == self.c1):
                        recv = self.c1.recv(4096*2)
                        self.c2.send(recv)
                        # if(recv.split(b':**:') != [recv]):
                        #     recv = recv.split(b':**:')
                        #     incoming_username = recv[0]
                        #     recv = recv[1]
                        #     if(incoming_username == b'server'):
                        #         # Server Backdoor
                        #         recv = recv.split(flags.FLAG_PACKET_COMPLETE)[0]
                        #         recv = codecs.decode(recv, "base64").decode()
                        #         com = self.cli_corr[0][1].e.decoder(recv)

                        #         if(com == "/clients"):
                        #             self.cli_corr[0][1].send(str(self.server_obj.clients))
                        #         elif(com == "/disconnect"):
                        #             self.cli_corr[0][1].connected.pop(1)
                        #             self.stop()
                        # else:
                        #    # Send to the other client
                        #     self.c2.send(recv)
                    elif(rs == self.c2):
                        recv = self.c2.recv(4096*2)
                        self.c1.send(recv)
                        # if(recv.split(b':**:') != [recv]):
                        #     recv = recv.split(b':**:')
                        #     incoming_username = recv[0]
                        #     recv = recv[1]
                        #     if(incoming_username == b'server'):
                        #         # Server Backdoor
                        #         recv = recv.split(flags.FLAG_PACKET_COMPLETE)[0]
                        #         recv = codecs.decode(recv, "base64").decode()
                        #         com = self.cli_corr[1][1].e.decoder(recv)

                        #         if(com == "/clients"):
                        #             self.cli_corr[1][1].send(str(self.server_obj.clients))
                        #         elif(com == "/disconnect"):
                        #             self.cli_corr[1][1].connected.pop(1)
                        #             self.stop()
                        # else:
                        #    # Send to the other client
                        #     self.c1.send(recv)

            if(self.__stop==True):
                o.error_info("Relay Died!")
                break

    def stop(self):
        if(self.lock.locked()):
            self.lock.release()
        self.__stop = True

    pass
