"""Host-only scalar logging contract. No native code, loader, or pointer access."""
from project_console import console_session
import unittest

U32_MAX = (1 << 32) - 1

def word(value):
    if type(value) is not int or not 0 <= value <= U32_MAX:
        raise ValueError('expected captured ARM uint32 word')
    return value

class DiagnosticLog:
    """Bounded synthetic events; the caller supplies already captured scalars."""
    def __init__(self, limit=64):
        if type(limit) is not int or limit < 0:
            raise ValueError('invalid event limit')
        self.limit, self.events, self.dropped = limit, [], 0

    def record(self, event):
        if len(self.events) < self.limit:
            self.events.append(dict(event))
        else:
            self.dropped += 1


def observe_registration(native, log, receiver_word, endpoint_word, caller_word):
    """Synthetic register ABI model: call original exactly once, preserve raw r0.

    Not an implementation of exception/unwind/register preservation on ARM.
    No decoding or dereferencing of captured pointer words is performed.
    """
    receiver, endpoint, caller = map(word, (receiver_word, endpoint_word, caller_word))
    def emit(event):
        try:
            log.record(event)
        except Exception:
            pass  # Diagnostic failure must not suppress the native call.
    emit({'event': 'register.enter', 'receiver': receiver,
          'endpoint': endpoint, 'caller': caller})
    result = native(receiver, endpoint)
    emit({'event': 'register.leave', 'return_r0': word(result)})
    return result


class DiagnosticTests(unittest.TestCase):
    def test_preserves_words_and_exactly_one_call(self):
        calls = []
        def native(*args):
            calls.append(args)
            return 0x80000001
        log = DiagnosticLog()
        self.assertEqual(observe_registration(native, log, 0x1000, 0x2000, 0x124e54), 0x80000001)
        self.assertEqual(calls, [(0x1000, 0x2000)])
        self.assertEqual(log.events[0]['caller'], 0x124e54)
        self.assertEqual(log.events[1]['return_r0'], 0x80000001)

    def test_logging_failure_does_not_change_call(self):
        class Failing:
            def record(self, event):
                raise OSError('synthetic log full')
        calls = []
        def native(*args):
            calls.append(args)
            return 0
        self.assertEqual(observe_registration(native, Failing(), 1, 2, 3), 0)
        self.assertEqual(calls, [(1, 2)])

    def test_bounded_storage(self):
        log = DiagnosticLog(1)
        observe_registration(lambda *args: 1, log, 0, 0, 0)
        self.assertEqual(len(log.events), 1)
        self.assertEqual(log.dropped, 1)

    def test_native_exception_propagates_without_retry(self):
        calls = []
        def native(*args):
            calls.append(args)
            raise RuntimeError('synthetic native failure')
        log = DiagnosticLog()
        with self.assertRaises(RuntimeError):
            observe_registration(native, log, 1, 2, 3)
        self.assertEqual(calls, [(1, 2)])
        self.assertEqual(len(log.events), 1)

    def test_invalid_capture_rejected_before_model_call(self):
        for value in (-1, 1 << 32, True, 'pointer'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                observe_registration(lambda *args: self.fail('invalid capture'), DiagnosticLog(), value, 0, 0)

if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
