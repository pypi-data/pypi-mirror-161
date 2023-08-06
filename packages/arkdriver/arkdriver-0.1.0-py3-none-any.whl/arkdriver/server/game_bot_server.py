from pathlib import Path
from arkdriver.server.stream import Stream
import socket
import selectors
import types
from arkdriver.driver import Admin
from arkdriver.lib import Ini


class GameBotServer:
    """
    Every Admin bot will be running this service
    """
    ADMIN = None

    def __init__(self, host: str = None, port: int = None):
        self.host = host or '127.0.0.1'
        self.port = port or 65432
        self.selector = selectors.DefaultSelector()
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.client_sockets = {}
        self.client_keys = {}

        if self.ADMIN is None:
            file_path = Path(__file__).parent.parent / Path('config.ini')
            config = Ini(file_path)
            password = config['SERVER']['password']
            player_id = config['BOT']['player_id']
            self.ADMIN = Admin(password=password, player_id=player_id)

    def connect(self):
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.host, self.port))
        self.lsock.listen()
        print(f"Listening on {self.host}:{self.port} (press CTRL-C to close server)")
        self.lsock.setblocking(False)
        self.selector.register(self.lsock, selectors.EVENT_READ, data=None)
        self.connected = True

    def disconnect(self):
        self.shutdown()
        self.selector.close()
        self.connected = False

    def accept_wrapper(self, key):
        sock = key.fileobj
        conn, (host, port) = sock.accept()  # Should be ready to read
        addr = f"{host}:{port}"
        print(f"Accepted connection from {addr}")

        self.client_sockets[addr] = sock
        self.client_keys[addr] = key

        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)

    def read(self, addr: str):
        sock = self.client_sockets[addr]
        fragments = bytearray()
        try:
            while True:
                chunk = bytearray(sock.recv(4096))  # Should be ready to read
                if not chunk:
                    break
                fragments += chunk
        except BlockingIOError:
            recv_data = bytes(fragments)
            return recv_data

    def write(self, addr, data):
        stream = Stream.new(data)
        print(f'\033[93m[{addr}] {"Sending:":>}\t{str(data):<}\033[0m')
        sock = self.client_sockets[addr]
        key = self.client_keys[addr]
        sent = sock.send(stream.encode())
        key.data.outb = key.data.outb[sent:]

    def disconnect_client(self, addr):
        print(f"Closing connection to {addr}")
        sock = self.client_sockets[addr]
        self.selector.unregister(sock)
        sock.close()
        del self.client_keys[addr]
        del self.client_sockets[addr]

    def shutdown(self):
        addresses = list(self.client_keys.keys())
        for addr in addresses:
            self.send_disconnect(addr)
            self.disconnect_client(addr)

    def send_disconnect(self, addr):
        sock = self.client_sockets[addr]
        data = self.client_keys[addr].data
        sent = sock.send("exit".encode())  # Should be ready to write
        data.outb = data.outb[sent:]

    def service_connection(self, key, mask):
        data = key.data
        addr = data.addr
        self.client_sockets[addr] = key.fileobj
        self.client_keys[addr] = key
        recv_data = None

        if mask & selectors.EVENT_READ:
            recv_data = self.read(addr)
            if recv_data:
                stream = Stream(stream=recv_data)
                print(f'\033[93m[{addr}] {"Received:":>}\t{stream.decode():<}\033[0m')
                self.ADMIN.command_list.append(stream.decode())
                data.outb += recv_data
            else:
                self.disconnect_client(addr)
        if mask & selectors.EVENT_WRITE:
            if recv_data:
                stream = Stream(stream=recv_data)
                outgoing_data = {"success": f"{stream.decode()}"}
                self.write(addr, outgoing_data)  # Should be ready to write

    def run(self):
        self.connect()
        try:
            while True:
                events = self.selector.select(timeout=None)
                for selector_key, mask in events:
                    if selector_key.data is None:
                        self.accept_wrapper(selector_key)
                    else:
                        self.service_connection(selector_key, mask)
                self.ADMIN.execute()
        except KeyboardInterrupt:
            print("\nCaught keyboard interrupt, exiting:")
        finally:
            self.disconnect()
            print("All connections closed.")

    def __repr__(self):
        attr = {
            'connected': self.connected,
            'host': self.host,
            'port': self.port
            }
        items = []
        for k, v in attr.items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96mGameBotServer\033[0m({args})>\033[0m'


if __name__ == "__main__":
    class A:
        def __init__(self):
            self.a = 1

        def __getitem_(self, item):
            return self.__dict__[item]

        def keys(self):
            return self.__dict__.keys()

        def __str__(self):
            return f"<A(a={repr(self.a)})>"

        def __repr__(self):
            return f"<A(a={repr(self.a)})>"

    game_server = GameBotServer()
    game_server.run()
