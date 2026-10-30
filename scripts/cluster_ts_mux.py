"""Offline native-format cluster TS mux; timestamps are explicit synthetic milliseconds."""
from __future__ import annotations
from native_transport_packet_reference import PAT_SECTION, PMT_SECTION

class MuxError(RuntimeError):
    pass

class ClusterTSMux:
    MAX_AU = 1024 * 1024

    def __init__(self, write):
        self.write = write
        self.failed = False
        self.started = False
        self.last_ms = self.psi_ms = self.pcr_ms = None
        self.cc = {}

    def _fail(self, message):
        self.failed = True
        raise MuxError(message)

    def _time(self, ms):
        if self.failed:
            raise MuxError("Mux is failed")
        if type(ms) is not int or ms < 0:
            self._fail("Milliseconds must be a nonnegative integer")
        if self.last_ms is not None and ms < self.last_ms:
            self._fail("Timestamp moved backwards")
        self.last_ms = ms

    def _emit(self, packet):
        try:
            count = self.write(packet)
        except Exception as exc:
            self.failed = True
            raise MuxError("Output failed") from exc
        if type(count) is not int or count != len(packet):
            self._fail("Output must consume exactly one complete packet; no retry")

    def _payload(self, pid, payload, start=False):
        cc = self.cc.get(pid, 0)
        self.cc[pid] = (cc + 1) & 15
        header = bytes((0x47, (pid >> 8) | (0x40 if start else 0), pid & 255))
        spare = 184 - len(payload)
        if spare:
            adaptation = bytes((spare - 1,)) + (b"\0" + b"\xff" * (spare - 2) if spare > 1 else b"")
            self._emit(header + bytes((0x30 | cc,)) + adaptation + payload)
        else:
            self._emit(header + bytes((0x10 | cc,)) + payload)

    @staticmethod
    def _stamp(value, prefix):
        value &= (1 << 33) - 1
        return bytes((prefix | ((value >> 29) & 14) | 1,
                      (value >> 22) & 255, ((value >> 14) & 254) | 1,
                      (value >> 7) & 255, ((value << 1) & 254) | 1))

    def tick(self, ms):
        """Emit due metadata. Caller must tick at least every 32 synthetic ms."""
        self._time(ms)
        if self.psi_ms is None or ms - self.psi_ms >= 332:
            for pid, section in ((0, PAT_SECTION), (0x10, PMT_SECTION)):
                self._payload(pid, b"\0" + section, True)
            self.psi_ms = ms
        if self.pcr_ms is None or ms - self.pcr_ms >= 32:
            base = (90 * ms) & 0xffffffff
            pcr = bytes(((base >> 25) & 255, (base >> 17) & 255,
                         (base >> 9) & 255, (base >> 1) & 255,
                         ((base & 1) << 7) | 0x7e, 0))
            self._emit(bytes.fromhex("47100020") + bytes((183, 0x10)) + pcr + b"\xff" * 176)
            self.pcr_ms = ms

    def push(self, au, ms):
        """Supply one complete Annex B access unit. Return False before first IDR."""
        self._time(ms)
        if not isinstance(au, bytes) or not 0 < len(au) <= self.MAX_AU:
            self._fail("Invalid access unit size/type")
        # Caller owns AU boundaries; this checks Annex B framing and IDR presence.
        import re
        starts = list(re.finditer(b"\x00\x00(?:\x00)?\x01", au))
        if not starts or starts[0].start() != 0 or any(m.end() == len(au) for m in starts):
            self._fail("Expected Annex B access unit")
        types = [au[m.end()] & 31 for m in starts]
        if any(au[m.end()] & 128 for m in starts) or not any(t in (1, 5) for t in types):
            self._fail("Invalid or missing AVC slice")
        if not self.started and 5 not in types:
            return False
        self.started = True
        self.tick(ms)
        dts = (90 * ms) & 0xffffffff
        length = len(au) + 13
        pes = (b"\x00\x00\x01\xe0" + (length if length <= 65535 else 0).to_bytes(2, "big")
               + b"\x80\xc0\x0a" + self._stamp(dts + 1, 0x30) + self._stamp(dts, 0x10) + au)
        for offset in range(0, len(pes), 184):
            self._payload(0x11, pes[offset:offset + 184], offset == 0)
        return True
