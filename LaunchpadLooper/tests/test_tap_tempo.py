import unittest

from LaunchpadLooper.TapTempo import TapTempo


class TapTempoTest(unittest.TestCase):

    def setUp(self):
        self.tap = TapTempo(window=2.0, min_taps=4, tempo_min=20.0, tempo_max=999.0)

    def test_count_follows_the_series_and_reset(self):
        t = TapTempo()
        self.assertEqual(0, t.count())
        t.tap(0.0)
        t.tap(0.5)
        self.assertEqual(2, t.count())
        t.tap(10.0)
        self.assertEqual(1, t.count())
        t.reset()
        self.assertEqual(0, t.count())

    def test_fewer_than_four_taps_return_none(self):
        self.assertIsNone(self.tap.tap(0.0))
        self.assertIsNone(self.tap.tap(0.5))
        self.assertIsNone(self.tap.tap(1.0))

    def test_fourth_tap_returns_tempo(self):
        for t in (0.0, 0.5, 1.0):
            self.tap.tap(t)
        self.assertAlmostEqual(120.0, self.tap.tap(1.5))

    def test_following_taps_keep_adjusting(self):
        for t in (0.0, 0.5, 1.0, 1.5):
            self.tap.tap(t)
        tempo = self.tap.tap(2.1)
        self.assertTrue(tempo < 120.0)
        self.assertTrue(tempo > 100.0)

    def test_gap_longer_than_window_resets(self):
        for t in (0.0, 0.5, 1.0):
            self.tap.tap(t)
        self.assertIsNone(self.tap.tap(3.5))
        self.assertIsNone(self.tap.tap(4.0))
        self.assertIsNone(self.tap.tap(4.5))
        self.assertAlmostEqual(120.0, self.tap.tap(5.0))

    def test_slow_tempo_inside_window(self):
        for t in (0.0, 1.5, 3.0):
            self.tap.tap(t)
        self.assertAlmostEqual(40.0, self.tap.tap(4.5))

    def test_tempo_is_clamped(self):
        for t in (0.0, 0.01, 0.02):
            self.tap.tap(t)
        self.assertEqual(999.0, self.tap.tap(0.03))

    def test_reset_clears_count(self):
        for t in (0.0, 0.5, 1.0):
            self.tap.tap(t)
        self.tap.reset()
        self.assertIsNone(self.tap.tap(1.5))

    def test_is_counting(self):
        self.assertFalse(self.tap.is_counting(0.0))
        self.tap.tap(0.0)
        self.assertTrue(self.tap.is_counting(1.0))
        self.assertFalse(self.tap.is_counting(2.5))

    def test_only_last_eight_taps_are_averaged(self):
        for i in range(8):
            self.tap.tap(i * 1.0)
        tempo = None
        for i in range(8):
            tempo = self.tap.tap(8.0 + (i + 1) * 0.5)
        self.assertAlmostEqual(120.0, tempo)


if __name__ == '__main__':
    unittest.main()
