import unittest

from LaunchpadLooper.BounceState import BounceSelection, BounceJob


class BounceSelectionTest(unittest.TestCase):

    def setUp(self):
        self.sel = BounceSelection(long_press=0.5)

    def test_short_release_without_touch_is_snapshot(self):
        self.sel.press(10.0)
        self.assertEqual('snapshot', self.sel.release(10.2))

    def test_long_release_without_touch_is_nothing(self):
        self.sel.press(10.0)
        self.assertIsNone(self.sel.release(10.6))

    def test_release_after_marking_is_nothing_whatever_the_duration(self):
        self.sel.press(10.0)
        self.sel.mark((0, 0))
        self.assertIsNone(self.sel.release(10.1))
        self.sel.press(20.0)
        self.sel.mark((0, 0))
        self.assertIsNone(self.sel.release(21.0))

    def test_mark_twice_keeps_mark_and_order(self):
        self.sel.press(0.0)
        self.assertTrue(self.sel.mark((2, 1)))
        self.assertTrue(self.sel.mark((0, 0)))
        self.assertTrue(self.sel.mark((2, 1)))
        self.assertEqual([(2, 1), (0, 0)], self.sel.marked())
        self.assertTrue(self.sel.is_marked((2, 1)))
        self.assertTrue(self.sel.touched())

    def test_focus_follows_last_touch(self):
        self.sel.press(0.0)
        self.assertIsNone(self.sel.focused())
        self.sel.mark((2, 1))
        self.sel.mark((0, 0))
        self.assertEqual((0, 0), self.sel.focused())
        self.sel.mark((2, 1))
        self.assertEqual((2, 1), self.sel.focused())

    def test_focus_is_cleared_on_release_and_ignored_when_inactive(self):
        self.sel.press(0.0)
        self.sel.mark((1, 1))
        self.sel.release(0.1)
        self.assertIsNone(self.sel.focused())
        self.sel.mark((1, 1))
        self.assertIsNone(self.sel.focused())

    def test_release_clears_and_deactivates(self):
        self.sel.press(0.0)
        self.sel.mark((0, 0))
        self.assertTrue(self.sel.is_active())
        self.sel.release(0.1)
        self.assertFalse(self.sel.is_active())
        self.assertEqual([], self.sel.marked())
        self.assertFalse(self.sel.touched())

    def test_mark_while_inactive_is_ignored(self):
        self.assertFalse(self.sel.mark((0, 0)))
        self.assertEqual([], self.sel.marked())

    def test_note_touch_without_mark(self):
        self.sel.press(0.0)
        self.sel.note_touch()
        self.assertIsNone(self.sel.release(0.1))


class BounceJobTest(unittest.TestCase):

    def setUp(self):
        self.job = BounceJob(target=(5, 2), origins=[(0, 0), (1, 3)], saved={'x': 1}, bars=4)

    def test_tracks_and_rows(self):
        self.assertTrue(self.job.is_origin_track(0))
        self.assertTrue(self.job.is_origin_track(1))
        self.assertFalse(self.job.is_origin_track(5))
        self.assertTrue(self.job.is_target_track(5))
        self.assertTrue(self.job.involves_track(0))
        self.assertTrue(self.job.involves_track(5))
        self.assertFalse(self.job.involves_track(7))
        self.assertTrue(self.job.involves_row(0))
        self.assertTrue(self.job.involves_row(2))
        self.assertTrue(self.job.involves_row(3))
        self.assertFalse(self.job.involves_row(1))
        self.assertTrue(self.job.origin_rows_include(3))
        self.assertFalse(self.job.origin_rows_include(2))

    def test_is_target(self):
        self.assertTrue(self.job.is_target((5, 2)))
        self.assertFalse(self.job.is_target((5, 1)))

    def test_origin_tracks(self):
        self.assertEqual([0, 1], self.job.origin_tracks())

    def test_flags_start_false(self):
        self.assertFalse(self.job.started)
        self.assertFalse(self.job.closing)
        self.assertFalse(self.job.origins_stopped)


if __name__ == '__main__':
    unittest.main()
