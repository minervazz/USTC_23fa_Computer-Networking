import json
from pathlib import Path
from typing import Optional, List
from onl.packet import Packet
from onl.device import Device, OutMixIn
from onl.sim import Environment


class GBNReceiver(Device, OutMixIn):
    def __init__(
        self,
        env: Environment,
        seqno_width: int,
        window_size: int,
        debug: bool = False,
    ):
        self.env = env
        
        self.seqno_width = seqno_width
        self.seqno_range = 2**self.seqno_width
        self.window_size = window_size
        assert self.window_size <= self.seqno_range - 1
        self.seqno_start = 0
        self.message = ""
        self.debug = debug

    def new_packet(self, ackno: int) -> Packet:
        return Packet(time=self.env.now, size=40, packet_id=ackno)

    def put(self, packet: Packet):
        seqno = packet.packet_id
        data = packet.payload
        if seqno != self.seqno_start:
            recent_orderno = (self.seqno_start + self.seqno_range - 1) % self.seqno_range
            ack_pkt = self.new_packet(recent_orderno)
            assert self.out
            self.out.put(ack_pkt)
            self.dprint(
                f"send ack {self.seqno_start}"
            )
            return
        self.message += data
        ack_pkt = self.new_packet(self.seqno_start)
        self.seqno_start = (self.seqno_start + 1) % self.seqno_range
        assert self.out
        self.out.put(ack_pkt)
        self.dprint(
            f"send ack {self.seqno_start}"
        )

    def dprint(self, s: str):
        if self.debug:
            print(f"[receiver](time: {self.env.now:.2f})", end=" -> ")
            print(s)
