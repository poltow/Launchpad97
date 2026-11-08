import unittest

from LaunchpadLooper.Settings import Settings, DEFAULTS


class SettingsTest(unittest.TestCase):

    def test_defaults(self):
        s = Settings()
        self.assertEqual(False, s.get('fixed_length_on'))
        self.assertEqual(1, s.get('fixed_length_bars'))
        self.assertEqual('1/16', s.get('quantize_grid'))
        self.assertEqual(1.0, s.get('quantize_amount'))

    def test_each_instance_starts_from_defaults(self):
        s = Settings()
        s.set('fixed_length_on', True)
        s.set('fixed_length_bars', 8)
        s.set('quantize_grid', '1/8t')
        s.set('quantize_amount', 0.5)
        again = Settings()
        for key in DEFAULTS:
            self.assertEqual(DEFAULTS[key], again.get(key), key)

    def test_set_keeps_value_within_the_instance(self):
        s = Settings()
        self.assertTrue(s.set('quantize_grid', '1/8'))
        self.assertEqual('1/8', s.get('quantize_grid'))

    def test_set_rejects_invalid_value(self):
        s = Settings()
        self.assertFalse(s.set('fixed_length_bars', 3))
        self.assertEqual(1, s.get('fixed_length_bars'))
        self.assertFalse(s.set('quantize_amount', 0.75))
        self.assertFalse(s.set('fixed_length_on', 'yes'))
        self.assertFalse(s.set('unknown_key', 1))

    def test_index_helpers(self):
        s = Settings()
        s.set('fixed_length_bars', 16)
        self.assertEqual(4, s.fixed_length_index())
        s.set('quantize_grid', '1/4')
        self.assertEqual(0, s.quantize_grid_index())
        s.set('quantize_amount', 0.5)
        self.assertEqual(0, s.quantize_amount_index())

    def test_set_by_index(self):
        s = Settings()
        s.set_fixed_length_index(1)
        self.assertEqual(2, s.get('fixed_length_bars'))
        s.set_quantize_grid_index(2)
        self.assertEqual('1/8t', s.get('quantize_grid'))
        s.set_quantize_amount_index(0)
        self.assertEqual(0.5, s.get('quantize_amount'))

    def test_toggle_fixed_length(self):
        s = Settings()
        self.assertTrue(s.toggle_fixed_length())
        self.assertTrue(s.get('fixed_length_on'))
        self.assertFalse(s.toggle_fixed_length())


if __name__ == '__main__':
    unittest.main()
