import unittest

from LaunchpadLooper import Dispatch as D
from LaunchpadLooper import SlotColors as C


class PadActionTest(unittest.TestCase):

    def test_no_modifier(self):
        self.assertEqual(D.RECORD, D.pad_action(None, C.EMPTY, False))
        self.assertEqual(D.LAUNCH, D.pad_action(None, C.STOPPED, False))
        self.assertEqual(D.STOP_IMMEDIATE, D.pad_action(None, C.PLAYING, False))
        self.assertEqual(D.STOP_IMMEDIATE, D.pad_action(None, C.STOP_PENDING_PLAYING, False))
        self.assertEqual(D.CLOSE_RECORDING, D.pad_action(None, C.RECORDING, False))
        self.assertEqual(D.CLOSE_RECORDING, D.pad_action(None, C.STOP_PENDING_RECORDING, False))
        self.assertEqual(D.CLOSE_RECORDING, D.pad_action(None, C.RECORDING_ENDING, False))
        self.assertEqual(D.LAUNCH, D.pad_action(None, C.TRIGGERED_PLAY, False))
        self.assertEqual(D.NONE, D.pad_action(None, C.TRIGGERED_RECORD, False))

    def test_delete(self):
        self.assertEqual(D.DELETE_CLIP, D.pad_action('delete', C.STOPPED, False))
        self.assertEqual(D.DELETE_CLIP, D.pad_action('delete', C.RECORDING, False))
        self.assertEqual(D.DELETE_CLIP, D.pad_action('delete', C.RECORDING_ENDING, False))
        self.assertEqual(D.NONE, D.pad_action('delete', C.EMPTY, False))

    def test_copy(self):
        self.assertEqual(D.COPY_SET_ORIGIN, D.pad_action('copy', C.STOPPED, False))
        self.assertEqual(D.COPY_SET_ORIGIN, D.pad_action('copy', C.PLAYING, True))
        self.assertEqual(D.COPY_PASTE, D.pad_action('copy', C.EMPTY, True))
        self.assertEqual(D.NONE, D.pad_action('copy', C.EMPTY, False))
        self.assertEqual(D.NONE, D.pad_action('copy', C.RECORDING, False))
        self.assertEqual(D.NONE, D.pad_action('copy', C.RECORDING_ENDING, False))

    def test_quantize(self):
        self.assertEqual(D.QUANTIZE_CLIP, D.pad_action('quantize', C.STOPPED, False))
        self.assertEqual(D.QUANTIZE_CLIP, D.pad_action('quantize', C.PLAYING, False))
        self.assertEqual(D.NONE, D.pad_action('quantize', C.EMPTY, False))
        self.assertEqual(D.NONE, D.pad_action('quantize', C.RECORDING, False))

    def test_stop(self):
        for state in (C.EMPTY, C.PLAYING, C.RECORDING, C.TRIGGERED_PLAY,
                      C.STOP_PENDING_PLAYING, C.RECORDING_ENDING):
            self.assertEqual(D.STOP_TRACK, D.pad_action('stop', state, False))

    def test_stop_launches_a_stopped_clip_in_sync(self):
        self.assertEqual(D.LAUNCH, D.pad_action('stop', C.STOPPED, False))

    def test_fixed_length_held_behaves_like_no_modifier(self):
        self.assertEqual(D.RECORD, D.pad_action('fixed_length', C.EMPTY, False))
        self.assertEqual(D.STOP_IMMEDIATE, D.pad_action('fixed_length', C.PLAYING, False))

    def test_snapshot_held_marks_playing_and_targets_empty(self):
        self.assertEqual(D.BOUNCE_MARK, D.pad_action('snapshot', C.PLAYING, False))
        self.assertEqual(D.BOUNCE_TARGET, D.pad_action('snapshot', C.EMPTY, False))
        for state in (C.STOPPED, C.RECORDING, C.RECORDING_ENDING, C.TRIGGERED_PLAY,
                      C.TRIGGERED_RECORD, C.STOP_PENDING_PLAYING, C.STOP_PENDING_RECORDING):
            self.assertEqual(D.NONE, D.pad_action('snapshot', state, False), state)


class LateralActionTest(unittest.TestCase):

    def test_no_modifier_fires_scene(self):
        self.assertEqual((D.FIRE_SCENE, 3), D.lateral_action(None, 3))

    def test_fixed_length_values(self):
        self.assertEqual((D.SET_FIXED_LENGTH, 0), D.lateral_action('fixed_length', 0))
        self.assertEqual((D.SET_FIXED_LENGTH, 4), D.lateral_action('fixed_length', 4))
        self.assertEqual((D.NONE, 5), D.lateral_action('fixed_length', 5))
        self.assertEqual((D.NONE, 7), D.lateral_action('fixed_length', 7))

    def test_quantize_values(self):
        self.assertEqual((D.SET_QUANTIZE_GRID, 0), D.lateral_action('quantize', 0))
        self.assertEqual((D.SET_QUANTIZE_GRID, 4), D.lateral_action('quantize', 4))
        self.assertEqual((D.NONE, 5), D.lateral_action('quantize', 5))
        self.assertEqual((D.SET_QUANTIZE_AMOUNT, 0), D.lateral_action('quantize', 6))
        self.assertEqual((D.SET_QUANTIZE_AMOUNT, 1), D.lateral_action('quantize', 7))

    def test_delete_row(self):
        self.assertEqual((D.DELETE_ROW, 2), D.lateral_action('delete', 2))

    def test_stop_row(self):
        self.assertEqual((D.STOP_ROW, 6), D.lateral_action('stop', 6))

    def test_snapshot_lateral_sets_gain(self):
        self.assertEqual((D.SET_GAIN, 3), D.lateral_action('snapshot', 3))

    def test_copy_does_nothing(self):
        self.assertEqual((D.NONE, 1), D.lateral_action('copy', 1))


if __name__ == '__main__':
    unittest.main()
