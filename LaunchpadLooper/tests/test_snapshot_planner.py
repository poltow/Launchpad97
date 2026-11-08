import unittest

from LaunchpadLooper.SnapshotPlanner import plan_snapshot, find_free_row, REJECT_RECORDING, REJECT_NO_ROW


class Grid(object):
    """'c' clip detenido, 'p' sonando, 'r' grabando, '.' vacio.
    rows[s][t]."""

    def __init__(self, rows):
        self.rows = rows
        self.num_scenes = len(rows)
        self.num_tracks = len(rows[0])

    def has_clip(self, t, s):
        return self.rows[s][t] != '.'

    def is_playing(self, t, s):
        return self.rows[s][t] == 'p'

    def is_recording(self, t, s):
        return self.rows[s][t] == 'r'


EMPTY = ['........'] * 8


class FindFreeRowTest(unittest.TestCase):

    def test_all_empty_returns_last_row(self):
        self.assertEqual(7, find_free_row(Grid(EMPTY)))

    def test_skips_rows_with_any_clip(self):
        rows = list(EMPTY)
        rows[7] = '.......c'
        rows[6] = 'c.......'
        self.assertEqual(5, find_free_row(Grid(rows)))

    def test_no_free_row(self):
        rows = ['c.......'] * 8
        self.assertIsNone(find_free_row(Grid(rows)))


class PlanSnapshotTest(unittest.TestCase):

    def test_copies_only_playing_clips(self):
        rows = list(EMPTY)
        rows[0] = 'p.c.p...'
        rows[1] = '...p....'
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertEqual(7, row)
        self.assertIsNone(reason)
        self.assertEqual([(0, 0), (3, 1), (4, 0)], sorted(copies))

    def test_rejects_when_any_track_is_recording(self):
        rows = list(EMPTY)
        rows[0] = 'p.r.....'
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertIsNone(row)
        self.assertEqual(REJECT_RECORDING, reason)
        self.assertEqual([], copies)

    def test_rejects_when_no_free_row(self):
        rows = ['p.......'] * 8
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertIsNone(row)
        self.assertEqual(REJECT_NO_ROW, reason)

    def test_nothing_playing_still_makes_empty_snapshot(self):
        rows = list(EMPTY)
        rows[0] = 'c.c.....'
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertEqual(7, row)
        self.assertIsNone(reason)
        self.assertEqual([], copies)


if __name__ == '__main__':
    unittest.main()
