# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@panodata.org>
# License: GNU Affero General Public License, Version 3
import logging
import socket
from enum import Enum

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

        self.reader: serial.Serial = None
        self.writer: socket.socket = None

    def verify(self):
        if not self.source.startswith(Prefixes.SERIAL.value):
            raise ValueError(f"source={self.source} not supported")

        if not self.target.startswith(Prefixes.FILE.value) and not self.target.startswith(
            Prefixes.UDP_BROADCAST_NMEA0183.value
        ):
            raise ValueError(f"target={self.target} not supported")

    def run(self):
        serial_port = self.source.replace(Prefixes.SERIAL.value, "")
        serial_baud = 9600
        serial_timeout = 3.0
        self.reader = serial.Serial(port=serial_port, baudrate=serial_baud, timeout=serial_timeout)
        self.writer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

        running = True
        while running:
            try:
                data = self.reader.readline().strip().decode("ascii")
            except:
                logger.exception(f"Reading data from serial port failed. device={serial_port}")
                continue
            logger.info(f"Decoded data: {data}")

            message_in = pynmea2.parse(data)
            logger.info(f"Parsed message: {message_in}")

            message_out = message_in.render().encode()
            logger.info(f"Outbound message: {message_out}")

            try:
                self.send_udp("255.255.255.255", 10110, message_out)
            except:
                logger.exception(f"Submitting message to UDP failed. message={message_out}")
                continue

    def send_udp(self, ip, port, message):
        self.writer.sendto(message.encode(), (ip, port))
