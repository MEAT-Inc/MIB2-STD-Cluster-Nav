"""Independent packet/PES checks for the offline native-format mux."""
from project_console import console_session
import unittest
from cluster_ts_mux import ClusterTSMux, MuxError

def packets(blob):
    assert len(blob) % 188 == 0
    for offset in range(0, len(blob), 188):
        p = blob[offset:offset + 188]
        assert p[0] == 0x47 and not p[1] & 0x80
        pid = ((p[1] & 31) << 8) | p[2]
        afc = (p[3] >> 4) & 3
        assert afc
        start = 4
        if afc & 2:
            start = 5 + p[4]
            assert start <= 188
        yield pid, bool(p[1] & 64), p[3] & 15, p[start:] if afc & 1 else b"", p

def pes_units(blob):
    units = []
    for pid, start, cc, payload, p in packets(blob):
        if pid == 0x11:
            if start:
                units.append(bytearray())
            assert units
            units[-1].extend(payload)
    return [bytes(u) for u in units]

def stamp(b):
    assert b[0] & 1 and b[2] & 1 and b[4] & 1
    return ((b[0] & 14) << 29) | (b[1] << 22) | ((b[2] & 254) << 14) | (b[3] << 7) | (b[4] >> 1)

def crc(data):
    value = 0xffffffff
    for byte in data:
        value ^= byte << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value

def au(n=40, idr=True):
    return b"\0\0\0\1" + bytes((0x65 if idr else 0x41,)) + b"\x88" * (n - 5)

class MuxTests(unittest.TestCase):
    def make(self):
        chunks = []
        def write(b):
            chunks.append(b)
            return len(b)
        return ClusterTSMux(write), chunks

    def test_exact_pes_and_au_sizes(self):
        mux, chunks = self.make()
        inputs = [au(n) for n in (5, 164, 165, 166, 349, 65522, 65523, 1024 * 1024)]
        for index, raw in enumerate(inputs):
            self.assertTrue(mux.push(raw, index * 40))
        units = pes_units(b"".join(chunks))
        self.assertEqual(len(units), len(inputs))
        for index, (pes, raw) in enumerate(zip(units, inputs)):
            self.assertEqual(pes[:4], b"\0\0\1\xe0")
            self.assertEqual(int.from_bytes(pes[4:6], "big"), len(raw) + 13 if len(raw) + 13 <= 65535 else 0)
            self.assertEqual(pes[6:9], b"\x80\xc0\x0a")
            self.assertEqual(pes[9] >> 4, 3)
            self.assertEqual(pes[14] >> 4, 1)
            self.assertEqual(stamp(pes[9:14]), index * 3600 + 1)
            self.assertEqual(stamp(pes[14:19]), index * 3600)
            self.assertEqual(pes[19:], raw)
        previous = {}
        for pid, start, cc, payload, p in packets(b"".join(chunks)):
            if payload:
                if pid in previous:
                    self.assertEqual(cc, (previous[pid] + 1) & 15)
                previous[pid] = cc

    def test_native_psi_pcr_and_cadence(self):
        mux, chunks = self.make()
        pcr_times, psi_times = [], {0: [], 0x10: []}
        for ms in range(0, 665, 4):
            before = len(chunks)
            mux.tick(ms)
            for pid, start, cc, payload, p in packets(b"".join(chunks[before:])):
                if pid == 0x1000:
                    self.assertEqual(p[3], 0x20)
                    self.assertEqual(p[4:6], bytes((183, 0x10)))
                    b = p[6:12]
                    base = (b[0] << 25) | (b[1] << 17) | (b[2] << 9) | (b[3] << 1) | (b[4] >> 7)
                    self.assertEqual(base, ms * 90)
                    self.assertEqual(b[4] & 0x7f, 0x7e)
                    self.assertEqual(b[5], 0)
                    pcr_times.append(ms)
                else:
                    self.assertIn(pid, psi_times)
                    self.assertTrue(start)
                    self.assertEqual(payload[0], 0)
                    section = payload[1:]
                    length = 3 + ((section[1] & 15) << 8) + section[2]
                    section = section[:length]
                    self.assertEqual(crc(section), 0)
                    if pid == 0:
                        self.assertEqual(section[:12].hex(), "00b00d0000c100000001e010")
                    else:
                        self.assertEqual(section[8:17].hex(), "f000f0001be011f00f")
                    psi_times[pid].append(ms)
        self.assertEqual(pcr_times, list(range(0, 665, 32)))
        self.assertEqual(psi_times, {0: [0, 332, 664], 0x10: [0, 332, 664]})

    def test_native_32_bit_time_wrap(self):
        mux, chunks = self.make()
        for ms in (47721858, 47721859, 47721860):
            mux.push(au(), ms)
        for ms, pes in zip((47721858, 47721859, 47721860), pes_units(b"".join(chunks))):
            self.assertEqual(stamp(pes[14:19]), (ms * 90) % (2 ** 32))
            self.assertEqual(stamp(pes[9:14]), (ms * 90) % (2 ** 32) + 1)

    def test_idr_gate_and_backward_time(self):
        mux, chunks = self.make()
        self.assertFalse(mux.push(au(idr=False), 0))
        self.assertEqual(chunks, [])
        self.assertTrue(mux.push(au(), 1))
        before = len(chunks)
        with self.assertRaises(MuxError):
            mux.tick(0)
        with self.assertRaises(MuxError):
            mux.push(au(), 2)
        self.assertEqual(len(chunks), before)

    def test_invalid_inputs_fail_closed(self):
        for raw, ms in ((b"", 0), (au(1024 * 1024 + 1), 0), (b"bad", 0),
                        (b"\0\0\1", 0), (b"\0\0\1\x67\x42", 0),
                        (au(), -1), (au(), 0.5)):
            mux, chunks = self.make()
            with self.assertRaises(MuxError):
                mux.push(raw, ms)
            with self.assertRaises(MuxError):
                mux.tick(1)
            self.assertEqual(chunks, [])

    def test_output_failure_never_retries_prefix(self):
        for result in (0, 17, -1, None, "raise"):
            calls = []
            def write(b):
                calls.append(b)
                if len(calls) == 5:
                    if result == "raise":
                        raise OSError("synthetic")
                    return result
                return len(b)
            mux = ClusterTSMux(write)
            with self.assertRaises(MuxError):
                mux.push(au(1000), 0)
            self.assertEqual(len(calls), 5)
            with self.assertRaises(MuxError):
                mux.push(au(), 1)
            self.assertEqual(len(calls), 5)

if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
