import random
from typing import List, Dict

from onl.device import UDPDevice
from onl.sim import Environment, ProcessGenerator, Store

from dns_packet import DNSPacket


def decode_ip(data: bytes) -> str:
    ip_tup = []
    ip_tup.append(str(data[-4]))
    ip_tup.append(str(data[-3]))
    ip_tup.append(str(data[-2]))
    ip_tup.append(str(data[-1]))
    return ".".join(ip_tup)


class DNSClient(UDPDevice):
    def __init__(self, env: Environment, urls: List[str], debug: bool = False):
        super().__init__()
        self.env = env
        self.debug = debug
        self.urls = urls
        self.finish_channel = Store(env)
        self.responses: List[Dict] = list()
        self.proc = env.process(self.run(env))

    def run(self, env: Environment) -> ProcessGenerator:
        for url in self.urls:
            self.env.timeout(random.randint(10, 30))
            self.send_url_request(url)
        yield self.finish_channel.get()

    def send_url_request(self, url: str):
        self.send(DNSPacket.generate_request(url))

    def recv_callback(self, data: bytes):
        """Called when receiving DNS reply from DNS server"""
        resp = DNSPacket(data)
        self.responses.append({"rcode": resp.RCODE, "ip": decode_ip(data)})
        if len(self.responses) == len(self.urls):
            self.finish_channel.put(True)
