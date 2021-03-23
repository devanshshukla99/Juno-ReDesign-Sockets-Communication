
# Testing MotherShip

from Server.server import server
from Client.client import client
from time import sleep

def test():
    s = server(HOST='localhost', PORT=45284)
    c = client(HOST='localhost', PORT=45284)
    s.connect()
    sleep(1)
    assert c.connect() == True
    s.stop()
    c.stop()