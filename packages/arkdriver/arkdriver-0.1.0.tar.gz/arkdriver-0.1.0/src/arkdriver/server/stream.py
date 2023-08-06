from arkdriver.server.header import Header
import json
import pickle


class Stream:
    r"""
    The Stream is a protocol which organizes messages being sent through the
    sockets. Each message is formatted int three parts: dimension, header, and data.

        Stream = [Dimension Stream][Header Stream][Data Stream]
            - Dimension Stream: length of the header stream.
            - Header Stream: extra data about the body, credentials, etc.
            - Data Stream: the raw data being sent.
        Ex.
                         Dimension      Header Stream                               Data Stream
            Stream   =   0036   |   {body_length: 19, body_type: 'json'}   |    {'data': 'my data'}
            Code     =  Stream(b"0036{body_length: 19, body_type: 'json'}{'data': 'my data'}")

            Stream   =   0038   |   {body_length: 19, body_type: 'pickle'} |    \x8\a43\x92\x213\x1
            Code     =  Stream(b"0038{body_length: 19, body_type: 'pickle'}\x8\a43\x92\x213\x1")

            Stream   =   0035   |   {body_length: 19, body_type: 'str'}   |     this is my data str
            Code     =  Stream(b"0035{body_length: 19, body_type: 'str'}this is my data str")
    """
    @classmethod
    def new(cls, data, **kwargs) -> 'Stream':
        if isinstance(data, dict) or isinstance(data, list):
            body = json.dumps(data).encode()
            data_type = "json"
        elif isinstance(data, str):
            body = data.encode()
            data_type = "str"
        else:
            body = pickle.dumps(data)
            data_type = "pickle"
        header = Header(body_type=data_type, body_length=len(body), **kwargs)
        return cls(body=body, header=header)

    def __init__(self, stream: bytes = None, header: Header = None, body: bytes = None):
        self.header_length = stream and Header.dimension(stream) or len(header)
        self.header = stream and Header.from_stream(stream) or header
        self.body = stream and stream[Header.DIMENSION + self.header_length:] or body

    def decode(self):
        data_type = self.header.body_type
        if data_type == "json":
            return json.loads(self.body.decode())
        elif data_type == "str":
            return self.body.decode()
        elif data_type == "pickle":
            return pickle.loads(self.body)

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, item):
        return self.__dict__[item]

    def encode(self) -> bytes:
        header_stream = bytearray(self.header and self.header.encode() or Header().encode())
        dimension_stream = bytearray(f"{len(header_stream)}".rjust(Header.DIMENSION, "0").encode())
        data_stream = bytearray(self.body)
        return bytes(dimension_stream + header_stream + data_stream)

    def __repr__(self):
        items = []
        for k, v in dict(self).items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96mStream\033[0m({args})>\033[0m'


if __name__ == "__main__":
    # From data
    data = "my message"
    stream = Stream.new(data)
    print("Encoded:", stream.encode())
    print("Decoded:", stream.decode(), "\n")

    data = ["item 1", "item 2", "item 3"]
    stream = Stream.new(data)
    print("Encoded:", stream.encode())
    print("Decoded:", stream.decode(), "\n")

    data = {"data": "my data"}
    stream = Stream.new(data)
    print("Encoded:", stream.encode())
    print("Decoded:", stream.decode(), "\n")

    class A:
        def __init__(self):
            self.a = 1

        def __getitem_(self, item):
            return self.__dict__[item]

        def keys(self):
            return self.__dict__.keys()

        def __str__(self):
            return f"<A(a={repr(self.a)})>"

    data = b'\x80\x04\x95\x1f\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x01A\x94\x93\x94)\x81\x94}\x94\x8c\x01a\x94K\x01sb.'
    stream = Stream.new(data)
    print("Encoded:", stream.encode())
    print("Decoded:", stream.decode(), "\n")

    # From streams
    header_stream = b'{"body_type": "pickle", "body_length": 42}'
    dimension_stream = bytearray(f"{len(header_stream)}".rjust(Header.DIMENSION, "0").encode())
    body_stream = bytearray(b'\x80\x04\x95\x1f\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x01A\x94\x93\x94)\x81\x94}\x94\x8c\x01a\x94K\x01sb.')
    stream = Stream(stream=dimension_stream + header_stream + body_stream)
    print("Stream:", stream)
    print("Encoded:", stream.encode())
    print("Decoded:", stream.decode(), "\n")
