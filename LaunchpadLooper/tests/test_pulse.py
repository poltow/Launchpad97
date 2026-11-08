import unittest

from LaunchpadLooper.Pulse import pulse_phase, PULSE_OFF, PULSE_BEAT, PULSE_DOWNBEAT


class BeatTime(object):
    def __init__(self, bars, beats, sub_division, ticks=1):
        self.bars = bars
        self.beats = beats
        self.sub_division = sub_division
        self.ticks = ticks


class PulseTest(unittest.TestCase):

    def test_first_half_of_downbeat_is_downbeat(self):
        self.assertEqual(PULSE_DOWNBEAT, pulse_phase(BeatTime(1, 1, 1), True))
        self.assertEqual(PULSE_DOWNBEAT, pulse_phase(BeatTime(1, 1, 2), True))

    def test_second_half_of_beat_is_off(self):
        self.assertEqual(PULSE_OFF, pulse_phase(BeatTime(1, 1, 3), True))
        self.assertEqual(PULSE_OFF, pulse_phase(BeatTime(1, 2, 4), True))

    def test_first_half_of_other_beats_is_beat(self):
        self.assertEqual(PULSE_BEAT, pulse_phase(BeatTime(1, 2, 1), True))
        self.assertEqual(PULSE_BEAT, pulse_phase(BeatTime(3, 4, 2), True))

    def test_stopped_song_is_steady_beat(self):
        self.assertEqual(PULSE_BEAT, pulse_phase(BeatTime(1, 1, 4), False))

    def test_none_beat_time_is_steady_beat(self):
        self.assertEqual(PULSE_BEAT, pulse_phase(None, True))


if __name__ == '__main__':
    unittest.main()
