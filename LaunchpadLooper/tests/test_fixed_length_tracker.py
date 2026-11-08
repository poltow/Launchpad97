import unittest

from LaunchpadLooper.FixedLengthTracker import FixedLengthTracker


class FixedLengthTrackerTest(unittest.TestCase):

    def setUp(self):
        self.t = FixedLengthTracker()

    def test_untracked_key_is_never_ending(self):
        self.assertFalse(self.t.update('a', is_recording=True, is_triggered=False, current_bar=5))
        self.assertFalse(self.t.ending_soon('a'))

    def test_pending_waits_for_recording_to_start(self):
        self.t.fired('a', bars=2)
        self.assertFalse(self.t.update('a', is_recording=False, is_triggered=True, current_bar=3))
        self.assertTrue(self.t.is_tracked('a'))

    def test_pending_dropped_when_trigger_vanishes_without_recording(self):
        self.t.fired('a', bars=2)
        self.t.update('a', is_recording=False, is_triggered=False, current_bar=3)
        self.assertFalse(self.t.is_tracked('a'))

    def test_last_bar_is_ending_soon(self):
        self.t.fired('a', bars=2)
        self.t.update('a', is_recording=False, is_triggered=True, current_bar=3)
        self.assertFalse(self.t.update('a', is_recording=True, is_triggered=False, current_bar=4))
        self.assertFalse(self.t.ending_soon('a'))
        self.assertTrue(self.t.update('a', is_recording=True, is_triggered=False, current_bar=5))
        self.assertTrue(self.t.ending_soon('a'))

    def test_one_bar_recording_is_ending_from_its_start(self):
        self.t.fired('a', bars=1)
        self.assertTrue(self.t.update('a', is_recording=True, is_triggered=False, current_bar=4))

    def test_recording_end_forgets_key(self):
        self.t.fired('a', bars=1)
        self.t.update('a', is_recording=True, is_triggered=False, current_bar=4)
        self.assertFalse(self.t.update('a', is_recording=False, is_triggered=False, current_bar=5))
        self.assertFalse(self.t.is_tracked('a'))
        self.assertFalse(self.t.ending_soon('a'))

    def test_forget_clears_key(self):
        self.t.fired('a', bars=4)
        self.t.update('a', is_recording=True, is_triggered=False, current_bar=1)
        self.t.forget('a')
        self.assertFalse(self.t.is_tracked('a'))

    def test_tracked_keys_lists_pending_and_active(self):
        self.t.fired('a', bars=4)
        self.t.fired('b', bars=4)
        self.t.update('b', is_recording=True, is_triggered=False, current_bar=1)
        self.assertEqual(set(['a', 'b']), set(self.t.tracked_keys()))

    def test_refire_resets_pending(self):
        self.t.fired('a', bars=4)
        self.t.update('a', is_recording=True, is_triggered=False, current_bar=1)
        self.t.fired('a', bars=1)
        self.assertTrue(self.t.update('a', is_recording=True, is_triggered=False, current_bar=2))


if __name__ == '__main__':
    unittest.main()
