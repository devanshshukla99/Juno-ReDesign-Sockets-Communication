
import socketserver
from threading import Thread, Lock, current_thread
from sys import stdout, exit
import select
import traceback

from ident.ident import IDENT
from ident.username import Username
from Connection.negotiate import AcceptNegotiation
from Chromos import Chromos
o = Chromos()

class server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    '''
    Server Class
    Handles incoming connections!
    '''
    def __init__(self,
        HOST:str='localhost',
        PORT:int=45284,
        username:str='server',
        forever:bool=True):

        self.allow_reuse_address = True
        self.clients = {}
        self.username = Username(username=username)
        self.HOST = HOST
        self.PORT = PORT
        self.forever = forever
        self.nof_requests = 4
        super().__init__((HOST, PORT), server.__TCPHandler)
        return
    
    def __repr__(self):
        return '[\x1b[1;34m%s\x1b[0m]'.join(['<', ' username=', ' host=', ' port=', ' nclient=', '>']) % ('Server Instance', str(self.username), self.HOST, str(self.PORT), len(self.clients))

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.

        In addition, exception handling is done here.

        """
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        # finally:
        #     self.shutdown_request(request)

    def connect(self)->None:
        """
        Starts Listening.
        """
        if(self.forever is True):
            self.server_thread = Thread(target=self.serve_forever)
            self.server_thread.start()
        elif(type(self.forever) is int):
            for _ in range(0, self.forever):
                self.server_thread = Thread(target=self.handle_request)
                self.server_thread.start()
                self.server_thread.join()
        o.info_y(''.join(['Listenting at ', str(self.HOST) , ':', str(self.PORT)]))
        return

    def stop(self)->None:
        stdout.write(o.red('Stopping!\n'))
        stdout.flush()
        try:
            if(self.clients):
                for client in list(self.clients.values()):
                    client.stop()
                    self.shutdown_request(client.s)
        except:
            traceback.print_exc()
        finally:
            if(self.forever is True):
                self.shutdown()
        stdout.write(o.red('Served Shutdown Complete!\n'))
        stdout.flush()
        return
        
    class __TCPHandler(socketserver.BaseRequestHandler):
        """
        The request handler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
        """
        timeout = 2

        def handle(self):
            """
            Handles Requests
            """
            rs, _, _ = select.select([self.request], [], [], self.timeout)
            if(rs):
                stdout.write('\n')
                stdout.flush()
                o.info_y("Authentication Request from %s at %d " % (str(self.client_address[0]), self.client_address[1]))
                try:
                    flag, enc, CPub, __username = AcceptNegotiation().authenticate(username=str(self.server.username), conn=self.request)
                    if(flag):
                        if(CPub):
                            o.info_y('Allowed Connection from %s at %d' % (str(self.client_address[0]), self.client_address[1]))
                            __username = Username(UID=__username)
                            self.server.clients[str(__username)] = IDENT(username=__username, soc=self.request, enc=enc, CPub=CPub, server_obj=self.server)
                            return
                    o.error_info('Authentication Failed!')
                except BrokenPipeError:
                    o.error_info('Pipe Broken during Authentication!')
                except ConnectionResetError:
                    o.error_info('Connection Reset during Authentication!')
                except Exception as e:
                    traceback.print_exc()
                    o.error_info('Beware! Authentication incomplete!\nBeware of MIM Attack!')
                    self.server.shutdown_request(self.request)
                    
    pass
