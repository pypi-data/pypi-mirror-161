# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@panodata.org>
# License: GNU Affero General Public License, Version 3
"""
About
=====

NMEA-0183 over TCP or UDP.


Network transport
=================

The default port for UDP is 10110. Port 10110 is
designated by IANA for "NMEA-0183 Navigational Data".


Message format
==============

The NMEA-0183 sentence information for "relative wind"
``VWR - Relative Wind Speed and Angle``::

             1  2  3  4  5  6  7  8 9
             |  |  |  |  |  |  |  | |
     $--VWR,x.x,a,x.x,N,x.x,M,x.x,K*hh<CR><LF>

     Field Number:
      1) Wind direction magnitude in degrees
      2) Wind direction Left/Right of bow
      3) Speed
      4) N = Knots
      5) Speed
      6) M = Meters Per Second
      7) Speed
      8) K = Kilometers Per Hour
      9) Checksum

-- http://www.nmea.de/nmea0183datensaetze.html


CLI sender / receiver
=====================

Submit and receive NMEA-0183 over UDP broadcast on the command line.

::

    # Submit
    echo '$IIVWR,045.0,L,12.6,N,6.5,M,23.3,K*52' | socat -u - udp-datagram:255.255.255.255:10110,bind=:56123,broadcast

    # Receive
    # Note: To stop this process, hit CTRL+C two times in quick succession.
    # Note: If you receive error messages like `E bind(6, {LEN=0 AF=2 0.0.0.0:10110}, 16): Address already in use`,
    #       make sure no other process is listening on that port. For example, OpenCPN.
    while true; do socat -u udp-recvfrom:10110,reuseaddr,reuseport system:cat; sleep 0.3; done
"""
import dataclasses
import logging
import struct
import typing as t
from binascii import hexlify

from calypso_anemometer.model import CalypsoReading
from calypso_anemometer.telemetry import NetworkProtocol, NetworkProtocolMode, NetworkTelemetry

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Nmea0183GenericMessage:
    """
    Represent and serialize generic NMEA-0183 message.
    """

    identifier: str
    fields: t.List[t.Union[t.AnyStr, t.SupportsInt, t.SupportsFloat, None]]

    def render(self):
        parts = [self.identifier] + self.fields
        parts = [part is not None and str(part) or "" for part in parts]
        message = ",".join(parts)
        checksum = self.checksum_hexlified(message)
        message += f"*{checksum}"
        return message

    @classmethod
    def checksum(cls, message) -> int:
        """
        Calculating the checksum is very easy. It is the representation of two hexadecimal characters of
        an XOR of all characters in the sentence between – but not including – the $ and the * character.

        https://rietman.wordpress.com/2008/09/25/how-to-calculate-the-nmea-checksum/
        """
        checksum: int = 0
        for char in message[1:]:
            checksum ^= ord(char)
        return checksum

    @classmethod
    def checksum_hexlified(cls, message) -> str:
        checksum = cls.checksum(message)
        return hexlify(struct.pack("B", checksum)).decode().upper()


@dataclasses.dataclass
class Nmea0183MessageIIVWR:
    """
    Represent and serialize NMEA-0183 IIVWR message.

    VWR - Relative Wind Speed and Angle
    """

    IDENTIFIER = "$IIVWR"
    direction_degrees: float
    speed_meters_per_second: float

    @property
    def direction_magnitude_in_degrees(self) -> float:
        return abs(self.wind_direction_180)

    @property
    def wind_direction_180(self) -> int:
        angle = self.direction_degrees
        return (angle > 180) and angle - 360 or angle

    @property
    def direction_left_right_of_bow(self) -> str:
        if -180 < self.wind_direction_180 < 0:
            indicator = "L"
        elif 0 < self.wind_direction_180 < 180:
            indicator = "R"
        else:
            indicator = ""
        return indicator

    @property
    def speed_knots(self) -> float:
        return round(self.speed_meters_per_second * 1.943844, 2)

    @property
    def speed_kilometers_per_hour(self) -> float:
        return round(self.speed_meters_per_second * 3.6, 2)

    def to_message(self):
        """
        Factory for generic `Nmea0183Message`.

        TODO: Derive individual values from others.
              - Compute `direction_left_right_of_bow` from `direction_magnitude_in_degrees`.
              - Compute missing `speed_` from other `speed_` values.
        """
        return Nmea0183GenericMessage(
            identifier=self.IDENTIFIER,
            fields=[
                self.convert_value(self.direction_magnitude_in_degrees),
                self.direction_left_right_of_bow,
                self.convert_value(self.speed_knots),
                "N",
                self.convert_value(self.speed_meters_per_second),
                "M",
                self.convert_value(self.speed_kilometers_per_hour),
                "K",
            ],
        )

    @staticmethod
    def convert_value(value, converter=float, default=""):
        if value is None:
            value = default
        else:
            value = converter(value)
        return value


@dataclasses.dataclass
class Nmea0183Messages:
    """
    Represent and render a list of NMEA-0183 messages.
    """

    items: t.Optional[t.List[Nmea0183GenericMessage]] = None

    def set_reading(self, reading: CalypsoReading):
        """
        Derive NMEA-0183 IIVWR message from measurement reading.
        """
        reading = reading.adjusted()
        iivwr = Nmea0183MessageIIVWR(
            direction_degrees=reading.wind_direction,
            speed_meters_per_second=reading.wind_speed,
        )
        self.items = [iivwr.to_message()]

    def aslist(self):
        """
        Render measurement items to multiple NMEA-0183 sentences.
        """
        messages = [item.render() for item in self.items]
        return messages

    def render(self):
        return "\n".join(self.aslist())


def nmea0183_telemetry_demo():
    """
    Demonstrate submitting telemetry data in NMEA-0183 sentence format
    over UDP broadcast to `255.255.255.255:10110`.

    Synopsis::

        python -m calypso_anemometer.telemetry.nmea0183
    """

    # Setup logging.
    from calypso_anemometer.util import setup_logging

    setup_logging(level=logging.DEBUG)

    # Define example reading.
    reading = CalypsoReading(
        wind_speed=5.69,
        wind_direction=206,
        battery_level=90,
        temperature=33,
        roll=30,
        pitch=-60,
        compass=235,
    )

    # Broadcast telemetry message, e.g. to OpenCPN.
    target_host = "255.255.255.255"
    # target_host = "localhost"
    telemetry = NetworkTelemetry(
        host=target_host, port=10110, protocol=NetworkProtocol.UDP, mode=NetworkProtocolMode.BROADCAST
    )
    msg = Nmea0183Messages()
    msg.set_reading(reading)
    telemetry.send(msg.render())


if __name__ == "__main__":
    nmea0183_telemetry_demo()
