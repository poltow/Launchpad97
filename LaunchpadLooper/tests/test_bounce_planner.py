import unittest

from LaunchpadLooper import BouncePlanner as P


class GridStub(object):
    """Grilla 8x8 de prueba: celdas 'p' sonando, 'r' grabando, 's' detenido, '.' vacio."""

    def __init__(self, rows, lengths=None, audio_tracks=None, beats_per_bar=4):
        self.num_tracks = 8
        self.num_scenes = 8
        self._rows = rows
        self._lengths = lengths or {}
        self._audio = audio_tracks if audio_tracks is not None else [True] * 8
        self.beats_per_bar = beats_per_bar

    def _cell(self, track, scene):
        if scene < len(self._rows) and track < len(self._rows[scene]):
            return self._rows[scene][track]
        return '.'

    def has_clip(self, track, scene):
        return self._cell(track, scene) != '.'

    def is_playing(self, track, scene):
        return self._cell(track, scene) == 'p'

    def is_recording(self, track, scene):
        return self._cell(track, scene) == 'r'

    def clip_length(self, track, scene):
        return self._lengths.get((track, scene), 4.0)

    def is_audio_track(self, track):
        return self._audio[track]


class LengthTest(unittest.TestCase):

    def test_lcm(self):
        self.assertEqual(16, P.lcm(8, 16))
        self.assertEqual(24, P.lcm(8, 12))
        self.assertEqual(6, P.lcm(2, 3))

    def test_length_is_lcm_in_whole_bars(self):
        self.assertEqual(16, P.length_beats([8, 16], 4))
        self.assertEqual(24, P.length_beats([8, 12], 4))
        self.assertEqual(24, P.length_beats([6, 8], 4), '1,5 y 2 compases -> 6 compases')
        self.assertEqual(32, P.length_beats([4, 8, 32], 4))

    def test_short_loop_rounds_up_to_one_bar(self):
        self.assertEqual(4, P.length_beats([2], 4))
        self.assertEqual(3, P.length_beats([1], 3), 'compas de 3/4')

    def test_non_integer_lengths_round_to_nearest_beat(self):
        self.assertEqual(8, P.length_beats([7.98, 4.02], 4))

    def test_fixed_length_only_shortens(self):
        self.assertEqual(8, P.length_beats([16, 8], 4, fixed_length_bars=2))
        self.assertEqual(4, P.length_beats([4], 4, fixed_length_bars=8))

    def test_empty_list_is_zero(self):
        self.assertEqual(0, P.length_beats([], 4))


class PlanTest(unittest.TestCase):

    def plan(self, grid, marked=(), target=(3, 0), fixed=None, in_progress=False):
        return P.plan_bounce(grid, list(marked), target, fixed, in_progress)

    def test_in_progress_is_rejected_first(self):
        grid = GridStub(['pp......'])
        origins, length, reason = self.plan(grid, in_progress=True)
        self.assertEqual(P.REJECT_IN_PROGRESS, reason)

    def test_any_recording_rejects(self):
        grid = GridStub(['pp......', '.....r..'])
        self.assertEqual(P.REJECT_RECORDING, self.plan(grid)[2])

    def test_nothing_marked_takes_every_playing_clip(self):
        grid = GridStub(['p.p.....', '.p......'])
        origins, length, reason = self.plan(grid, target=(5, 0))
        self.assertIsNone(reason)
        self.assertEqual([(0, 0), (1, 1), (2, 0)], sorted(origins))
        self.assertEqual(4, length)

    def test_nothing_marked_and_nothing_playing_rejects(self):
        grid = GridStub(['s.......'])
        self.assertEqual(P.REJECT_NOTHING_PLAYING, self.plan(grid)[2])

    def test_marked_clips_that_stopped_are_dropped(self):
        grid = GridStub(['p.s.....'])
        origins, length, reason = self.plan(grid, marked=[(0, 0), (2, 0)], target=(5, 0))
        self.assertIsNone(reason)
        self.assertEqual([(0, 0)], origins)

    def test_marked_clips_all_stopped_rejects(self):
        grid = GridStub(['p.s.....'])
        self.assertEqual(P.REJECT_NOTHING_PLAYING, self.plan(grid, marked=[(2, 0)], target=(5, 0))[2])

    def test_target_occupied_rejects(self):
        grid = GridStub(['p.s.....'])
        self.assertEqual(P.REJECT_TARGET_OCCUPIED, self.plan(grid, target=(2, 0))[2])

    def test_target_on_origin_track_rejects(self):
        grid = GridStub(['p.......'])
        self.assertEqual(P.REJECT_TARGET_ON_ORIGIN_TRACK, self.plan(grid, target=(0, 3))[2])

    def test_target_on_non_audio_track_rejects(self):
        grid = GridStub(['p.......'], audio_tracks=[True, True, False] + [True] * 5)
        self.assertEqual(P.REJECT_TARGET_NOT_AUDIO, self.plan(grid, target=(2, 0))[2])

    def test_too_long_rejects_unless_fixed_length_shortens(self):
        grid = GridStub(['pp......'], lengths={(0, 0): 4 * 64, (1, 0): 4 * 3})
        self.assertEqual(P.REJECT_TOO_LONG, self.plan(grid, target=(5, 0))[2])
        origins, length, reason = self.plan(grid, target=(5, 0), fixed=8)
        self.assertIsNone(reason)
        self.assertEqual(32, length)

    def test_length_uses_grid_signature(self):
        grid = GridStub(['pp......'], lengths={(0, 0): 3, (1, 0): 6}, beats_per_bar=3)
        origins, length, reason = self.plan(grid, target=(5, 0))
        self.assertEqual(6, length)


if __name__ == '__main__':
    unittest.main()
