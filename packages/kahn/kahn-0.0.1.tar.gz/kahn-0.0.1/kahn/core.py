# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@panodata.org>
# License: GNU Affero General Public License, Version 3
import logging
import socket
from enum import Enum
from typing import Optional

import pynmea2
import serial

logger = logging.getLogger(__name__)


class Prefixes(Enum):
    SERIAL = "serial://"
    FILE = "file://"
    UDP_BROADCAST_NMEA0183 = "udp+broadcast+nmea0183://"


class ForwardingEngine:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target

        self.verify()

        self.reader: Optional[serial.Serial] = None
        self.writer: Optional[socket.socket] = None

        self.serial_port = self.source.replace(Prefixes.SERIAL.value, "")
        self.serial_baudrate = 9600
        self.serial_timeout = 3.0

        self.setup()

        self.running = False

    def verify(self):
        if not self.source.startswith(Prefixes.SERIAL.value):
            raise ValueError(f"source={self.source} not supported")

        if not self.target.startswith(Prefixes.FILE.value) and not self.target.startswith(
            Prefixes.UDP_BROADCAST_NMEA0183.value
        ):
            raise ValueError(f"target={self.target} not supported")

    def setup(self):
        self.reader = serial.Serial(port=self.serial_port, baudrate=self.serial_baudrate, timeout=self.serial_timeout)
        self.writer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.writer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.writer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def run(self):
        self.running = True
        while self.running:
            self.process()

    def process(self):

        try:
            data = self.reader.readline().strip().decode("ascii")
        except:
            logger.exception(f"Reading data from serial port failed. device={self.serial_port}")
            return
        logger.info(f"Decoded data: {data}")

        try:
            message_in = pynmea2.parse(data)
        except pynmea2.ParseError:
            logger.exception(f"Decoding NMEA-0183 sentence from serial port failed. device={self.serial_port}")
            return
        logger.info(f"Parsed message: {message_in}")

        message_out = message_in.render().encode()
        logger.info(f"Outbound message: {message_out}")

        # TODO: Use designated target address, parsed from options.
        try:
            self.send_udp("255.255.255.255", 10110, message_out)
        except:
            logger.exception(f"Submitting message to UDP failed. message={message_out}")
            return

        return message_out

    def send_udp(self, ip, port, message):
        if isinstance(message, str):
            message = message.encode()
        message += b"\n"
        self.writer.sendto(message, (ip, port))
