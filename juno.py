import argparse

from MotherShip import MotherShip

parser = argparse.ArgumentParser(description="Package for easy-straight-forward socket communication with 128-bit AES encryption.")
parser.add_argument("--bind", "-b", dest="bind_ip", required=False, action="store", type=str, default="localhost", help="Bind IP")
parser.add_argument("--port", "-p", dest="bind_port", required=False, action="store", type=int, default=45284, help="Bind Port")
parser.add_argument("--timeout", "-t", dest="timeout", required=False, action="store", type=int, default=30, help="Timeout [30s]")
parser.add_argument("--username", "-u", dest="username", required=False, action="store", type=str, default="", help="Username")
parser.add_argument("--server", "-s", dest="server", required=False, action="store_true", help="Initiate a server instance")
args = parser.parse_args()

m = MotherShip(username=args.username, host=args.bind_ip, port=args.bind_port, init_server=args.server)
m.deck()
