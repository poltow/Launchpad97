import unittest

from LaunchpadLooper import SlotColors as C


class SlotStateTest(unittest.TestCase):

    def state(self, **kw):
        args = dict(has_clip=False, is_triggered=False, will_record=False,
                    is_playing=False, is_recording=False, stop_pending=False,
                    ending_soon=False)
        args.update(kw)
        return C.slot_state(**args)

    def test_empty(self):
        self.assertEqual(C.EMPTY, self.state())

    def test_stopped(self):
        self.assertEqual(C.STOPPED, self.state(has_clip=True))

    def test_playing(self):
        self.assertEqual(C.PLAYING, self.state(has_clip=True, is_playing=True))

    def test_recording(self):
        self.assertEqual(C.RECORDING, self.state(has_clip=True, is_playing=True, is_recording=True))

    def test_triggered_play(self):
        self.assertEqual(C.TRIGGERED_PLAY, self.state(has_clip=True, is_triggered=True))

    def test_triggered_record(self):
        self.assertEqual(C.TRIGGERED_RECORD, self.state(is_triggered=True, will_record=True))

    def test_stop_pending_playing(self):
        self.assertEqual(C.STOP_PENDING_PLAYING,
                         self.state(has_clip=True, is_playing=True, stop_pending=True))

    def test_stop_pending_recording(self):
        self.assertEqual(C.STOP_PENDING_RECORDING,
                         self.state(has_clip=True, is_playing=True, is_recording=True, stop_pending=True))

    def test_recording_triggered_to_play_is_recording_ending(self):
        self.assertEqual(C.RECORDING_ENDING,
                         self.state(has_clip=True, is_playing=True, is_recording=True, is_triggered=True))

    def test_fixed_length_last_bar_is_recording_ending(self):
        self.assertEqual(C.RECORDING_ENDING,
                         self.state(has_clip=True, is_playing=True, is_recording=True, ending_soon=True))

    def test_stop_pending_wins_over_recording_ending(self):
        self.assertEqual(C.STOP_PENDING_RECORDING,
                         self.state(has_clip=True, is_playing=True, is_recording=True,
                                    is_triggered=True, stop_pending=True))

    def test_ending_soon_without_recording_is_ignored(self):
        self.assertEqual(C.PLAYING, self.state(has_clip=True, is_playing=True, ending_soon=True))

    def test_stop_pending_on_stopped_clip_is_just_stopped(self):
        self.assertEqual(C.STOPPED, self.state(has_clip=True, stop_pending=True))


class SlotColorTest(unittest.TestCase):

    def test_static_states_without_modifier(self):
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.EMPTY, None, True))
        self.assertEqual('Looper.Slot.Stopped', C.slot_color(C.STOPPED, None, True))
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, None, False))
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.RECORDING, None, False))

    def test_triggered_states_blink_at_pulse(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.TRIGGERED_PLAY, None, True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.TRIGGERED_PLAY, None, False))
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.TRIGGERED_RECORD, None, True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.TRIGGERED_RECORD, None, False))

    def test_stop_pending_alternates_amber_with_state_color(self):
        self.assertEqual('Looper.Slot.StopPending', C.slot_color(C.STOP_PENDING_PLAYING, None, True))
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.STOP_PENDING_PLAYING, None, False))
        self.assertEqual('Looper.Slot.StopPending', C.slot_color(C.STOP_PENDING_RECORDING, None, True))
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.STOP_PENDING_RECORDING, None, False))

    def test_recording_ending_alternates_red_and_green(self):
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.RECORDING_ENDING, None, True))
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.RECORDING_ENDING, None, False))

    def test_recording_ending_is_visible_under_stop_and_delete(self):
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.RECORDING_ENDING, 'stop', True))
        self.assertEqual('Looper.Slot.Delete', C.slot_color(C.RECORDING_ENDING, 'delete', True))

    def test_delete_modifier_shows_every_clip_red(self):
        for state in (C.STOPPED, C.PLAYING, C.RECORDING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            self.assertEqual('Looper.Slot.Delete', C.slot_color(state, 'delete', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.EMPTY, 'delete', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.TRIGGERED_RECORD, 'delete', True))

    def test_stop_modifier_shows_the_grid_as_usual(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, 'stop', True))
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.RECORDING, 'stop', True))
        self.assertEqual('Looper.Slot.StopPending', C.slot_color(C.STOP_PENDING_PLAYING, 'stop', True))
        self.assertEqual('Looper.Slot.Stopped', C.slot_color(C.STOPPED, 'stop', True))
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.TRIGGERED_PLAY, 'stop', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.TRIGGERED_PLAY, 'stop', False))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.EMPTY, 'stop', True))

    def test_copy_origin_blinks(self):
        self.assertEqual('Looper.Slot.CopyOrigin', C.slot_color(C.STOPPED, 'copy', True, is_copy_origin=True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.STOPPED, 'copy', False, is_copy_origin=True))
        self.assertEqual('Looper.Slot.Stopped', C.slot_color(C.STOPPED, 'copy', False))

    def test_snapshot_modifier_shows_playing_and_marks(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, 'snapshot', True))
        self.assertEqual('Looper.Slot.CopyOrigin', C.slot_color(C.PLAYING, 'snapshot', True, is_bounce_mark=True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.PLAYING, 'snapshot', False, is_bounce_mark=True))
        for state in (C.EMPTY, C.STOPPED, C.RECORDING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            self.assertEqual('Looper.Slot.Empty', C.slot_color(state, 'snapshot', True), state)

    def test_bounce_mark_without_snapshot_modifier_is_ignored(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, None, True, is_bounce_mark=True))

    def test_init_pending_overrides_everything(self):
        self.assertEqual('Looper.Slot.InitPending', C.slot_color(C.PLAYING, 'delete', True, init_pending=True))
        self.assertEqual('Looper.Slot.InitPending', C.slot_color(C.EMPTY, None, True, init_pending=True))

    def test_init_pending_blinks_at_pulse(self):
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.PLAYING, None, False, init_pending=True))

    def test_quantize_and_fixed_length_modifiers_keep_normal_colors(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, 'quantize', True))
        self.assertEqual('Looper.Slot.Stopped', C.slot_color(C.STOPPED, 'fixed_length', True))


class SceneColorTest(unittest.TestCase):

    def color(self, **kw):
        args = dict(has_playing=False, has_clips=False,
                    is_triggered=False, modifier=None, blink_on=True)
        args.update(kw)
        return C.scene_color(**args)

    def test_plain_states(self):
        self.assertEqual('Looper.Scene.Off', self.color())
        self.assertEqual('Looper.Scene.Stopped', self.color(has_clips=True))
        self.assertEqual('Looper.Scene.Playing', self.color(has_playing=True, has_clips=True))

    def test_triggered_blinks(self):
        self.assertEqual('Looper.Scene.Playing', self.color(is_triggered=True, has_clips=True, blink_on=True))
        self.assertEqual('Looper.Scene.Off', self.color(is_triggered=True, has_clips=True, blink_on=False))

    def test_delete_modifier(self):
        self.assertEqual('Looper.Scene.Delete', self.color(has_clips=True, modifier='delete'))
        self.assertEqual('Looper.Scene.Off', self.color(modifier='delete'))

    def test_stop_modifier(self):
        self.assertEqual('Looper.Scene.Playing', self.color(has_playing=True, has_clips=True, modifier='stop'))
        self.assertEqual('Looper.Scene.Off', self.color(has_clips=True, modifier='stop'))

    def test_snapshot_modifier_turns_scenes_off(self):
        self.assertEqual('Looper.Scene.Off', self.color(has_playing=True, has_clips=True, modifier='snapshot'))

    def test_copy_modifier_is_like_none(self):
        self.assertEqual('Looper.Scene.Stopped', self.color(has_clips=True, modifier='copy'))


class ValueRowTest(unittest.TestCase):

    def test_fixed_length_row(self):
        row = C.fixed_length_row(2)
        self.assertEqual(['Looper.Value.Idle', 'Looper.Value.Idle', 'Looper.Value.Selected',
                          'Looper.Value.Idle', 'Looper.Value.Idle',
                          'Looper.Value.Off', 'Looper.Value.Off', 'Looper.Value.Off'], row)

    def test_quantize_row(self):
        row = C.quantize_row(grid_index=3, amount_index=1)
        self.assertEqual(['Looper.Value.Idle', 'Looper.Value.Idle', 'Looper.Value.Idle',
                          'Looper.Value.Selected', 'Looper.Value.Idle',
                          'Looper.Value.Off', 'Looper.Value.Idle', 'Looper.Value.Selected'], row)

    def test_quantize_row_amount_half(self):
        row = C.quantize_row(grid_index=0, amount_index=0)
        self.assertEqual('Looper.Value.Selected', row[6])
        self.assertEqual('Looper.Value.Idle', row[7])


if __name__ == '__main__':
    unittest.main()
