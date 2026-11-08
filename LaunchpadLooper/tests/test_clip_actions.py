import unittest

from LaunchpadLooper import ClipGain
from LaunchpadLooper.ClipActions import ClipActions
from LaunchpadLooper.tests.fakes import FakeSong, FakeClip

NO_Q = 'q_no_q'


class ClipActionsTest(unittest.TestCase):

    def setUp(self):
        self.song = FakeSong()
        self.logged = []
        self.actions = ClipActions(self.song, NO_Q, log=self.logged.append)

    def errors(self):
        """Lineas de error (sin las de diagnostico)."""
        return [line for line in self.logged if 'diag:' not in line]

    # --- stop inmediato -------------------------------------------------

    def test_stop_immediately_overrides_and_restores_quantization(self):
        slot = self.song.slot(0, 0)
        slot.clip = FakeClip(is_playing=True)
        self.actions.stop_immediately(slot)
        self.assertEqual(1, slot.stop_calls)
        self.assertEqual([NO_Q, 'q_bar'], self.song.quantization_history)
        self.assertEqual('q_bar', self.song.clip_trigger_quantization)

    def test_stop_immediately_restores_even_if_stop_raises(self):
        slot = self.song.slot(0, 0)
        slot.clip = FakeClip(is_playing=True)

        def boom():
            raise RuntimeError('x')
        slot.stop = boom
        self.actions.stop_immediately(slot)
        self.assertEqual('q_bar', self.song.clip_trigger_quantization)
        self.assertEqual(1, len(self.errors()))

    # --- grabar / lanzar ------------------------------------------------

    def test_record_arms_track_and_fires_with_fixed_length(self):
        slot = self.song.slot(2, 0)
        track = self.song.tracks[2]
        armed = self.actions.record(slot, fixed_length_bars=4)
        self.assertTrue(armed)
        self.assertTrue(track.arm)
        self.assertEqual([{'record_length': 16.0, 'launch_quantization': 'q_bar'}], slot.fire_calls)

    def test_record_without_fixed_length_fires_plain(self):
        slot = self.song.slot(2, 0)
        self.actions.record(slot, fixed_length_bars=None)
        self.assertEqual([{}], slot.fire_calls)

    def test_record_length_follows_signature(self):
        self.song.signature_numerator = 3
        self.song.signature_denominator = 8
        slot = self.song.slot(0, 0)
        self.actions.record(slot, fixed_length_bars=2)
        self.assertAlmostEqual(3.0, slot.fire_calls[0]['record_length'])

    def test_record_does_not_disarm_other_tracks(self):
        self.song.tracks[0].arm = True
        self.actions.record(self.song.slot(1, 0), None)
        self.assertTrue(self.song.tracks[0].arm)
        self.assertTrue(self.song.tracks[1].arm)

    def test_record_on_already_armed_track_reports_not_armed_by_us(self):
        self.song.tracks[1].arm = True
        self.assertFalse(self.actions.record(self.song.slot(1, 0), None))

    def test_record_on_track_that_cannot_be_armed_does_not_fire(self):
        self.song.tracks[1].can_be_armed = False
        slot = self.song.slot(1, 0)
        self.assertFalse(self.actions.record(slot, None))
        self.assertEqual([], slot.fire_calls)

    def test_launch_fires_slot(self):
        slot = self.song.slot(0, 0)
        slot.clip = FakeClip()
        self.actions.launch(slot)
        self.assertEqual([{}], slot.fire_calls)

    # --- borrar ---------------------------------------------------------

    def test_delete_clip(self):
        slot = self.song.slot(0, 0)
        slot.clip = FakeClip()
        self.assertTrue(self.actions.delete_clip(slot))
        self.assertTrue(slot.deleted)

    def test_delete_clip_on_empty_slot_is_noop(self):
        self.assertFalse(self.actions.delete_clip(self.song.slot(0, 0)))

    def test_delete_row_clears_clips_and_snap_name_in_one_undo_step(self):
        scene = self.song.scenes[3]
        scene.name = 'SNAP'
        for t in (0, 5):
            self.song.slot(t, 3).clip = FakeClip()
        self.actions.delete_row(scene, 'SNAP')
        self.assertFalse(any(s.has_clip for s in scene.clip_slots))
        self.assertEqual('', scene.name)
        self.assertEqual(1, self.song.undo_begin)
        self.assertEqual(1, self.song.undo_end)

    def test_delete_row_keeps_other_names(self):
        scene = self.song.scenes[3]
        scene.name = 'Intro'
        self.actions.delete_row(scene, 'SNAP')
        self.assertEqual('Intro', scene.name)

    # --- copiar ---------------------------------------------------------

    def test_copy_to_empty_slot(self):
        src = self.song.slot(0, 0)
        dst = self.song.slot(1, 2)
        src.clip = FakeClip()
        self.assertTrue(self.actions.copy_clip(src, dst))
        self.assertTrue(dst.has_clip)

    def test_copy_refuses_occupied_destination(self):
        src = self.song.slot(0, 0)
        dst = self.song.slot(1, 2)
        src.clip = FakeClip()
        dst.clip = FakeClip()
        self.assertFalse(self.actions.copy_clip(src, dst))

    def test_copy_logs_runtime_error(self):
        src = self.song.slot(0, 0)
        dst = self.song.slot(1, 2)
        src.clip = FakeClip()
        src.raise_on_duplicate = RuntimeError('limit')
        self.assertFalse(self.actions.copy_clip(src, dst))
        self.assertEqual(1, len(self.errors()))

    # --- cuantizar ------------------------------------------------------

    def test_quantize_clip(self):
        slot = self.song.slot(0, 0)
        slot.clip = FakeClip()
        self.assertTrue(self.actions.quantize_clip(slot, 'grid16', 0.5))
        self.assertEqual([('grid16', 0.5)], slot.clip.quantize_calls)

    def test_quantize_empty_slot_is_noop(self):
        self.assertFalse(self.actions.quantize_clip(self.song.slot(0, 0), 'g', 1.0))

    # --- stop en sync ---------------------------------------------------

    def test_stop_track(self):
        self.actions.stop_track(self.song.tracks[3])
        self.assertEqual(1, self.song.tracks[3].stop_all_calls)

    def test_stop_row_stops_only_tracks_playing_that_row(self):
        self.song.tracks[0].playing_slot_index = 2
        self.song.tracks[1].playing_slot_index = 5
        self.song.tracks[2].playing_slot_index = 2
        self.actions.stop_row(self.song.tracks, 2)
        self.assertEqual(1, self.song.tracks[0].stop_all_calls)
        self.assertEqual(0, self.song.tracks[1].stop_all_calls)
        self.assertEqual(1, self.song.tracks[2].stop_all_calls)
        self.assertEqual(0, self.song.tracks[3].stop_all_calls)

    # --- snapshot -------------------------------------------------------

    def test_take_snapshot_copies_and_names(self):
        self.song.slot(0, 0).clip = FakeClip(is_playing=True)
        self.song.slot(3, 1).clip = FakeClip(is_playing=True)
        self.actions.take_snapshot(self.song.scenes, target_row=7,
                                   copies=[(0, 0), (3, 1)], snap_name='SNAP')
        self.assertTrue(self.song.slot(0, 7).has_clip)
        self.assertTrue(self.song.slot(3, 7).has_clip)
        self.assertFalse(self.song.slot(1, 7).has_clip)
        self.assertEqual('SNAP', self.song.scenes[7].name)
        self.assertEqual(1, self.song.undo_begin)
        self.assertEqual(1, self.song.undo_end)

    # --- INIT -----------------------------------------------------------

    def test_init_grid_clears_everything_in_one_undo_step(self):
        for s in range(8):
            self.song.slot(s, s).clip = FakeClip()
        self.song.scenes[7].name = 'SNAP'
        self.song.scenes[2].name = 'Verse'
        self.actions.init_grid(self.song.scenes, 8, 'SNAP')
        for s in range(8):
            self.assertFalse(self.song.slot(s, s).has_clip)
        self.assertEqual('', self.song.scenes[7].name)
        self.assertEqual('Verse', self.song.scenes[2].name)
        self.assertEqual(1, self.song.undo_begin)
        self.assertEqual(1, self.song.undo_end)

    def test_init_grid_only_touches_window(self):
        extra = FakeSong(num_tracks=10, num_scenes=10)
        actions = ClipActions(extra, NO_Q)
        extra.slot(9, 9).clip = FakeClip()
        extra.slot(9, 0).clip = FakeClip()
        extra.slot(0, 9).clip = FakeClip()
        actions.init_grid(extra.scenes[:8], 8, 'SNAP')
        self.assertTrue(extra.slot(9, 9).has_clip)
        self.assertTrue(extra.slot(9, 0).has_clip)
        self.assertTrue(extra.slot(0, 9).has_clip)

    # --- undo / redo / metronomo / tempo --------------------------------

    def test_set_tempo_clamps(self):
        self.actions.set_tempo(5.0)
        self.assertEqual(20.0, self.song.tempo)
        self.actions.set_tempo(5000.0)
        self.assertEqual(999.0, self.song.tempo)

    def test_toggle_metronome(self):
        self.assertTrue(self.actions.toggle_metronome())
        self.assertTrue(self.song.metronome)
        self.assertFalse(self.actions.toggle_metronome())

    # --- bounce ---------------------------------------------------------

    def bounce_setup(self):
        self.song.slot(0, 0).clip = FakeClip(is_playing=True)
        self.song.slot(1, 2).clip = FakeClip(is_playing=True)
        self.song.tracks[0].mixer_device.sends[0].value = 0.3
        target = self.song.slot(5, 1)
        target_track = self.song.tracks[5]
        target_track.current_monitoring_state = 1
        return [self.song.slot(0, 0), self.song.slot(1, 2)], target, target_track

    def test_bounce_start_routes_arms_and_fires(self):
        origins, target, target_track = self.bounce_setup()
        saved = self.actions.bounce_start(origins, target, 16.0, 0, 'A-BOUNCE')
        self.assertIsNotNone(saved)
        self.assertEqual(1.0, self.song.tracks[0].mixer_device.sends[0].value)
        self.assertEqual(1.0, self.song.tracks[1].mixer_device.sends[0].value)
        self.assertEqual(0.0, self.song.tracks[2].mixer_device.sends[0].value, 'otras pistas no se tocan')
        self.assertEqual('A-BOUNCE', target_track.current_input_routing)
        self.assertEqual(2, target_track.current_monitoring_state)
        self.assertTrue(target_track.arm)
        self.assertEqual([{'record_length': 16.0, 'launch_quantization': 'q_bar'}], target.fire_calls)

    def test_bounce_restore_puts_everything_back(self):
        origins, target, target_track = self.bounce_setup()
        saved = self.actions.bounce_start(origins, target, 16.0, 0, 'A-BOUNCE')
        self.actions.bounce_restore(saved)
        self.assertEqual(0.3, self.song.tracks[0].mixer_device.sends[0].value)
        self.assertEqual(0.0, self.song.tracks[1].mixer_device.sends[0].value)
        self.assertEqual('Ext. In', target_track.current_input_routing)
        self.assertEqual(1, target_track.current_monitoring_state)
        self.assertFalse(target_track.arm)

    def test_bounce_restore_keeps_arm_if_it_was_armed_before(self):
        origins, target, target_track = self.bounce_setup()
        target_track.arm = True
        saved = self.actions.bounce_start(origins, target, 16.0, 0, 'A-BOUNCE')
        self.actions.bounce_restore(saved)
        self.assertTrue(target_track.arm)

    def test_bounce_start_restores_and_returns_none_if_fire_raises(self):
        origins, target, target_track = self.bounce_setup()
        target.raise_on_fire = RuntimeError('boom')
        saved = self.actions.bounce_start(origins, target, 16.0, 0, 'A-BOUNCE')
        self.assertIsNone(saved)
        self.assertEqual(0.3, self.song.tracks[0].mixer_device.sends[0].value)
        self.assertEqual('Ext. In', target_track.current_input_routing)
        self.assertFalse(target_track.arm)
        self.assertEqual(1, len(self.errors()))
        self.assertIn('boom', self.errors()[0])

    def test_bounce_cancel_deletes_clip_or_stops_trigger(self):
        target = self.song.slot(5, 1)
        target.clip = FakeClip(is_recording=True)
        self.actions.bounce_cancel(target)
        self.assertTrue(target.deleted)
        empty = self.song.slot(6, 1)
        empty.is_triggered = True
        self.actions.bounce_cancel(empty)
        self.assertEqual(1, empty.stop_calls)

    def test_stop_tracks(self):
        tracks = [self.song.tracks[0], self.song.tracks[3]]
        self.actions.stop_tracks(tracks)
        self.assertEqual(1, self.song.tracks[0].stop_all_calls)
        self.assertEqual(1, self.song.tracks[3].stop_all_calls)
        self.assertEqual(0, self.song.tracks[1].stop_all_calls)

    # --- gain de clip ---------------------------------------------------

    def test_first_gain_use_calibrates_and_sets_in_one_undo_step(self):
        clip = FakeClip(is_playing=True)
        cal = ClipGain.Calibration()
        self.assertTrue(self.actions.set_gain_level(clip, cal, 3))
        self.assertTrue(cal.is_done())
        self.assertEqual('-3.0 dB', clip.gain_display_string)
        self.assertEqual((1, 1), (self.song.undo_begin, self.song.undo_end))

    def test_next_gain_use_only_writes_once(self):
        clip = FakeClip(is_playing=True)
        cal = ClipGain.Calibration()
        self.actions.set_gain_level(clip, cal, 3)
        clip.gain_writes = 0
        self.assertTrue(self.actions.set_gain_level(clip, cal, 0))
        self.assertEqual(1, clip.gain_writes)
        self.assertEqual('+6.0 dB', clip.gain_display_string)

    def test_gain_live_error_restores_and_returns_false(self):
        clip = FakeClip(is_playing=True)
        clip.raise_on_gain = RuntimeError('no')
        cal = ClipGain.Calibration()
        self.assertFalse(self.actions.set_gain_level(clip, cal, 3))
        self.assertFalse(cal.is_done())
        self.assertEqual(0.85, clip.gain)
        self.assertEqual((1, 1), (self.song.undo_begin, self.song.undo_end))
        self.assertTrue(any('set_gain_level' in line for line in self.logged))


if __name__ == '__main__':
    unittest.main()
