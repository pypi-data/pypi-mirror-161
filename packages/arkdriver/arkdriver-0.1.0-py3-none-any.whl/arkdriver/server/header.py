import json
from collections import defaultdict


class Header:
    r"""
    A header is a 1 of the 3 parts which make up the Stream:
        Stream = [Dimension Stream][Header Stream][Data Stream]
                - Dimension Stream: length of the header stream.
                - Header Stream: extra data about the body, credentials, etc.
                - Data Stream: the raw data being sent.
        Ex.
                         Dimension      Header Stream                               Data Stream
            Stream   =   0036   |   {body_length: 19, body_type: 'json'}   |    {'data': 'my data'}
            Stream   =   0038   |   {body_length: 19, body_type: 'pickle'} |    \x8\a43\x92\x213\x1
            Stream   =   0035   |   {body_length: 19, body_type: 'str'}   |     this is my data str
    """
    DIMENSION = 4  # Max header size is 4 decimal digits long (e.g. 9999 bytes)

    def __init__(self, header_stream: bytes = None, **kwargs):
        # https://www.whitehatsec.com/blog/list-of-http-response-headers/
        attrs = defaultdict(lambda: None)
        attrs.update(kwargs)
        self.body_length = attrs['body_length']
        self.body_type = attrs['body_type']
        self.credentials = attrs['credentials']
        self.methods = attrs['methods']
        self.from_address = attrs['from_address']
        self.to_address = attrs['to_address']
        self.expiration = attrs['expiration']
        self.connection = attrs['connection']
        self.encoding = attrs['encoding']
        self.transfer_encoding = attrs['transfer_encoding']
        self.location = attrs['location']
        self.security = attrs['security']
        self.__decode(header_stream)

    def __decode(self, data: bytes):
        if data:
            json_data = self.decode(data)
            self.__dict__.update(json_data)

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, item):
        return self.__dict__[item]

    def encode(self) -> bytes:
        json_data = json.dumps(dict(self))
        return json_data.encode()

    @classmethod
    def decode(cls, header_stream: bytes) -> 'Header':
        json_str = header_stream.decode()
        json_data = json.loads(json_str)
        return cls(**json_data)

    @classmethod
    def dimension(cls, stream) -> int:
        dimension_str = stream[:cls.DIMENSION].decode()
        return int(dimension_str)

    @classmethod
    def from_stream(cls, stream) -> 'Header':
        header_length = cls.dimension(stream)
        start = cls.DIMENSION
        end = cls.DIMENSION + header_length
        return cls.decode(stream[start: end])

    def __len__(self):
        return len(self.encode())

    def __repr__(self):
        items = []
        for k, v in dict(self).items():
            items.append(f"\033[34m{k}\033[90m=\033[0m{repr(v)}\033[0m")
        args = ', '.join(items)
        return f'<\033[96mHeader\033[0m({args})>\033[0m'


if __name__ == "__main__":
    # Header from stream
    header_stream = b'{"body_length": 42}'
    dimension_stream = bytearray(bytearray(f"{len(header_stream)}".rjust(Header.DIMENSION, "0").encode()))
    header_stream = bytearray(header_stream)
    body_stream = bytearray(b'\x80\x04\x95\x1f\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x01A\x94\x93\x94)\x81\x94}\x94\x8c\x01a\x94K\x01sb.')
    stream = dimension_stream + header_stream + body_stream
    print("\nRaw Stream:\t", stream)
    print("\tdimension stream:\t", dimension_stream)
    print("\theader stream:\t\t", header_stream)
    print("\tbody stream:\t\t", body_stream)

    print("\ndecode():\t", Header.decode(bytes(header_stream)))

    header = Header(header_stream)
    print("Header:\t\t", header)

    header = Header.from_stream(stream)
    print("Header from stream:\t\t", header)

    header = Header()
    header.length = 50
    header.type = "json"
    header.credentials = "jdfalkdjkldjasfjdsjfaljsfd"

    print("encode():\t", header.encode())
