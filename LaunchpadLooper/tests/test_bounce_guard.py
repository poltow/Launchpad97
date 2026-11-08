import unittest

from LaunchpadLooper import BounceGuard as G
from LaunchpadLooper import SlotColors as C
from LaunchpadLooper.BounceState import BounceJob


def job(started):
    j = BounceJob(target=(5, 2), origins=[(0, 0), (1, 3)], saved={}, bars=4)
    j.started = started
    return j


TARGET = (5, 2)
ORIGIN = (0, 0)
ORIGIN_TRACK_EMPTY = (0, 4)
TARGET_TRACK_OTHER = (5, 6)
FREE = (7, 7)


class NoJobTest(unittest.TestCase):

    def test_everything_allowed_without_job(self):
        for modifier in (None, 'delete', 'stop', 'copy', 'quantize', 'fixed_length'):
            self.assertEqual(G.ALLOW, G.pad_decision(None, modifier, ORIGIN, C.PLAYING))
            self.assertEqual(G.ALLOW, G.lateral_decision(None, modifier, 0, []))
        for name in ('undo', 'snapshot', 'delete', 'pulse'):
            self.assertEqual(G.ALLOW, G.top_decision(None, name))
        self.assertEqual(G.ALLOW, G.chord_decision(None))


class PadTest(unittest.TestCase):

    def test_target_pad_cancels_while_waiting_and_closes_while_recording(self):
        self.assertEqual(G.CANCEL, G.pad_decision(job(False), None, TARGET, C.TRIGGERED_RECORD))
        self.assertEqual(G.CLOSE, G.pad_decision(job(True), None, TARGET, C.RECORDING))
        self.assertEqual(G.IGNORE, G.pad_decision(job(True), None, TARGET, C.RECORDING_ENDING))

    def test_delete_on_target_always_cancels(self):
        self.assertEqual(G.CANCEL, G.pad_decision(job(False), 'delete', TARGET, C.TRIGGERED_RECORD))
        self.assertEqual(G.CANCEL, G.pad_decision(job(True), 'delete', TARGET, C.RECORDING))
        self.assertEqual(G.CANCEL, G.pad_decision(job(True), 'delete', TARGET, C.RECORDING_ENDING))

    def test_stop_on_target_cancels_then_closes(self):
        self.assertEqual(G.CANCEL, G.pad_decision(job(False), 'stop', TARGET, C.TRIGGERED_RECORD))
        self.assertEqual(G.CLOSE, G.pad_decision(job(True), 'stop', TARGET, C.RECORDING))
        self.assertEqual(G.IGNORE, G.pad_decision(job(True), 'stop', TARGET, C.RECORDING_ENDING))

    def test_other_modifiers_on_target_are_ignored(self):
        for modifier in ('quantize', 'copy', 'fixed_length'):
            self.assertEqual(G.IGNORE, G.pad_decision(job(True), modifier, TARGET, C.RECORDING))

    def test_origin_track_pads_are_rejected_except_copy(self):
        for started in (False, True):
            for key, state in ((ORIGIN, C.PLAYING), (ORIGIN_TRACK_EMPTY, C.EMPTY), ((0, 5), C.STOPPED)):
                for modifier in (None, 'delete', 'stop', 'quantize', 'fixed_length'):
                    self.assertEqual(G.REJECT, G.pad_decision(job(started), modifier, key, state),
                                     '%s %s %s' % (started, key, modifier))
                self.assertEqual(G.ALLOW, G.pad_decision(job(started), 'copy', key, state))

    def test_target_track_other_pads_are_rejected_except_copy(self):
        for modifier in (None, 'delete', 'stop', 'quantize', 'fixed_length'):
            self.assertEqual(G.REJECT, G.pad_decision(job(True), modifier, TARGET_TRACK_OTHER, C.EMPTY))
        self.assertEqual(G.ALLOW, G.pad_decision(job(True), 'copy', TARGET_TRACK_OTHER, C.EMPTY))

    def test_free_track_pads_are_allowed(self):
        for modifier in (None, 'delete', 'stop', 'quantize', 'copy', 'fixed_length'):
            self.assertEqual(G.ALLOW, G.pad_decision(job(True), modifier, FREE, C.EMPTY))
            self.assertEqual(G.ALLOW, G.pad_decision(job(False), modifier, FREE, C.PLAYING))


class LateralTest(unittest.TestCase):

    def test_plain_lateral_rejected(self):
        self.assertEqual(G.REJECT, G.lateral_decision(job(False), None, 7, []))
        self.assertEqual(G.REJECT, G.lateral_decision(job(True), None, 1, []))

    def test_value_modifiers_allowed(self):
        self.assertEqual(G.ALLOW, G.lateral_decision(job(True), 'fixed_length', 0, []))
        self.assertEqual(G.ALLOW, G.lateral_decision(job(True), 'quantize', 0, []))

    def test_delete_lateral_rejected_only_on_involved_rows(self):
        self.assertEqual(G.REJECT, G.lateral_decision(job(True), 'delete', 0, []), 'fila con origen')
        self.assertEqual(G.REJECT, G.lateral_decision(job(True), 'delete', 2, []), 'fila del destino')
        self.assertEqual(G.ALLOW, G.lateral_decision(job(True), 'delete', 1, []))

    def test_stop_lateral_rejected_when_an_origin_track_plays_that_row(self):
        # row_tracks: pistas cuyo clip sonando esta en esa fila
        self.assertEqual(G.REJECT, G.lateral_decision(job(True), 'stop', 3, [1, 7]))
        self.assertEqual(G.ALLOW, G.lateral_decision(job(True), 'stop', 5, [7]))
        self.assertEqual(G.ALLOW, G.lateral_decision(job(True), 'stop', 2, []))

    def test_copy_lateral_allowed(self):
        self.assertEqual(G.ALLOW, G.lateral_decision(job(True), 'copy', 0, []))


class TopTest(unittest.TestCase):

    def test_snapshot_cancels_then_closes(self):
        self.assertEqual(G.CANCEL, G.top_decision(job(False), 'snapshot'))
        self.assertEqual(G.CLOSE, G.top_decision(job(True), 'snapshot'))
        closing = job(True)
        closing.closing = True
        self.assertEqual(G.IGNORE, G.top_decision(closing, 'snapshot'))

    def test_undo_rejected(self):
        self.assertEqual(G.REJECT, G.top_decision(job(False), 'undo'))
        self.assertEqual(G.REJECT, G.top_decision(job(True), 'undo'))

    def test_other_tops_allowed(self):
        for name in ('fixed_length', 'quantize', 'delete', 'stop', 'copy', 'pulse'):
            self.assertEqual(G.ALLOW, G.top_decision(job(True), name))

    def test_chord_rejected(self):
        self.assertEqual(G.REJECT, G.chord_decision(job(False)))


if __name__ == '__main__':
    unittest.main()
