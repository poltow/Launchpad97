import unittest

from LaunchpadLooper import ClipGain as G


class LevelsTest(unittest.TestCase):

    def test_eight_levels_descending_with_zero_at_index_2(self):
        self.assertEqual((6.0, 3.0, 0.0, -3.0, -6.0, -12.0, -15.0, -18.0), G.LEVELS_DB)
        self.assertEqual(2, G.ZERO_INDEX)
        self.assertEqual(8, len(G.FALLBACK))


class ParseDbTest(unittest.TestCase):

    def test_plain_values(self):
        self.assertEqual(6.0, G.parse_db('+6.0 dB'))
        self.assertEqual(-3.0, G.parse_db('-3.0 dB'))
        self.assertEqual(0.0, G.parse_db('0.0 dB'))
        self.assertEqual(-3.5, G.parse_db('-3,5 dB'))

    def test_infinity_and_garbage(self):
        self.assertEqual(float('-inf'), G.parse_db('-inf dB'))
        self.assertIsNone(G.parse_db(''))
        self.assertIsNone(G.parse_db(None))
        self.assertIsNone(G.parse_db('dB'))


class NearestLevelTest(unittest.TestCase):

    def test_exact_and_between(self):
        self.assertEqual(0, G.nearest_level(6.0))
        self.assertEqual(3, G.nearest_level(-3.0))
        self.assertEqual(5, G.nearest_level(-10.0))
        self.assertEqual(7, G.nearest_level(-40.0))
        self.assertEqual(7, G.nearest_level(float('-inf')))
        self.assertEqual(0, G.nearest_level(20.0))
        self.assertIsNone(G.nearest_level(None))


class LateralColorTest(unittest.TestCase):

    def test_no_focus_is_off(self):
        for i in range(8):
            self.assertEqual('Looper.Scene.Off', G.lateral_color(i, None))

    def test_current_zero_and_rest(self):
        self.assertEqual('Looper.Scene.Playing', G.lateral_color(4, 4))
        self.assertEqual('Looper.Scene.Stopped', G.lateral_color(2, 4))
        self.assertEqual('Looper.Scene.Off', G.lateral_color(0, 4))
        self.assertEqual('Looper.Scene.Playing', G.lateral_color(2, 2))


class FakeGainClip(object):
    """Curva simulada de Live: dB = 40 * (gain - 0.85), -inf en 0."""

    def __init__(self):
        self.gain = 0.85

    def display(self):
        if self.gain <= 0.0:
            return '-inf dB'
        return '%+.1f dB' % (40.0 * (self.gain - 0.85))


class CalibrationTest(unittest.TestCase):

    def test_starts_with_fallback(self):
        cal = G.Calibration()
        self.assertFalse(cal.is_done())
        self.assertEqual(G.FALLBACK[3], cal.value_for(3))

    def test_calibrates_all_levels_on_a_monotonic_curve(self):
        clip = FakeGainClip()
        cal = G.Calibration()
        approx = cal.calibrate(lambda v: setattr(clip, 'gain', v), clip.display)
        self.assertEqual([], approx)
        self.assertTrue(cal.is_done())
        for index, target in enumerate(G.LEVELS_DB):
            clip.gain = cal.value_for(index)
            self.assertEqual(target, G.parse_db(clip.display()), index)

    def test_two_decimal_display_converges_to_the_exact_value(self):
        # Live 11 muestra dos decimales: '-2.99 dB' no sirve, tiene que dar '-3.00 dB'
        clip = FakeGainClip()
        display = lambda: '-inf dB' if clip.gain <= 0.0 else '%+.2f dB' % (40.0 * (clip.gain - 0.85))
        cal = G.Calibration()
        self.assertEqual([], cal.calibrate(lambda v: setattr(clip, 'gain', v), display))
        for index, target in enumerate(G.LEVELS_DB):
            clip.gain = cal.value_for(index)
            self.assertEqual(target, G.parse_db(display()), index)

    def test_unreachable_level_is_reported_as_approximate(self):
        clip = FakeGainClip()
        cal = G.Calibration()
        # curva que tope en +3 dB: +6 no se alcanza
        approx = cal.calibrate(lambda v: setattr(clip, 'gain', min(v, 0.925)), clip.display)
        self.assertEqual([0], approx)
        self.assertTrue(cal.is_done())

    def test_unreadable_text_keeps_fallback(self):
        cal = G.Calibration()
        self.assertIsNone(cal.calibrate(lambda v: None, lambda: 'nada'))
        self.assertFalse(cal.is_done())
        self.assertEqual(G.FALLBACK[0], cal.value_for(0))


if __name__ == '__main__':
    unittest.main()
