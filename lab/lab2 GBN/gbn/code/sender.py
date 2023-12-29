from typing import Deque
from collections import deque
from onl.packet import Packet
from onl.device import Device, OutMixIn
from onl.sim import Environment, Store
from onl.utils import Timer

class GBNSender(Device, OutMixIn):
    def __init__(
        self,
        env: Environment,
        seqno_width: int,
        timeout: float,
        window_size: int,
        message: str,
        debug: bool = False,
    ):
        """
        GBNSender类的构造函数。
        :param env: 环境对象。
        :param seqno_width: 序列号的位宽。
        :param timeout: 超时时间。
        :param window_size: 滑动窗口大小。
        :param message: 要发送的消息。
        :param debug: 是否开启调试模式。
        """
        self.env = env
        self.seqno_width = seqno_width
        self.seqno_range = 2**self.seqno_width
        self.window_size = window_size
        assert self.window_size <= self.seqno_range - 1
        self.timeout = timeout
        self.debug = debug
        self.message = message
        self.seqno = 0
        self.absno = 0
        self.seqno_start = 0
        self.outbound: Deque[Packet] = deque()
        self.finish_channel: Store = Store(env)
        self.timer = Timer(
            self.env,
            self.timeout,
            auto_restart=True,
            timeout_callback=self.timeout_callback,
        )
        self.proc = env.process(self.run(env))

    def new_packet(self, seqno: int, data: str) -> Packet:
        """
        创建一个新的分组。
        :param seqno: 分组的序列号。
        :param data: 分组的数据。
        :return: 新创建的分组。
        """
        return Packet(time=self.env.now, size=40, packet_id=seqno, payload=data)

    def send_packet(self, packet: Packet):
        """
        发送一个分组。
        :param packet: 要发送的分组。
        """
        self.dprint(f"send {packet.payload} on seqno {packet.packet_id}")
        assert self.out
        self.out.put(packet)

    def run(self, env: Environment):
        """
        run函数：负责发送滑动窗口内所有可以发送的分组，并在发送后等待ACK或超时。
        """
        while len(self.outbound) < self.window_size and self.absno < len(self.message):
            packet = self.new_packet(self.seqno, self.message[self.absno])
            self.send_packet(packet)
            self.outbound.append(packet)
            self.seqno = (self.seqno + 1) % self.seqno_range
            self.absno += 1
        yield self.finish_channel.get()

    def put(self, packet: Packet):
        """
        put函数：处理从接收端收到的ACK。
        """
        ackno = packet.packet_id
        self.dprint(f"receive ack {ackno}")
        if ackno in [pkt.packet_id for pkt in self.outbound]:
            while self.seqno_start != ackno:
                self.outbound.popleft()
                self.seqno_start = (self.seqno_start + 1) % self.seqno_range
            self.outbound.popleft()
            self.seqno_start = (self.seqno_start + 1) % self.seqno_range
            while len(self.outbound) < self.window_size and self.absno < len(self.message):
                packet = self.new_packet(self.seqno, self.message[self.absno])
                self.send_packet(packet)
                self.outbound.append(packet)
                self.seqno = (self.seqno + 1) % self.seqno_range
                self.absno += 1
            self.timer.restart(self.timeout)
            if self.absno >= len(self.message) and len(self.outbound) == 0:
                self.finish_channel.put(True)

    def timeout_callback(self):
        """
        timeout_callback函数：在超时时被调用，重新发送缓冲区中的所有分组。
        """
        self.dprint("timeout")
        for packet in self.outbound:
            self.send_packet(packet)

    def dprint(self, s):
        """
        dprint函数：用于调试输出。
        :param s: 要输出的字符串。
        """
        if self.debug:
            print(f"[sender](time: {self.env.now:.2f})", end=" -> ")
