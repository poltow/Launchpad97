import unittest

from LaunchpadLooper import Diag
from LaunchpadLooper.tests.fakes import FakeSong, FakeClip, FakeTrack, FakeSlot


class Broken(object):
    """Objeto cuyas propiedades lanzan, como un ClipSlot de Live ya borrado."""

    def __getattr__(self, name):
        raise RuntimeError('gone')


class DiagTest(unittest.TestCase):

    def test_song_state(self):
        song = FakeSong()
        song.is_playing = True
        text = Diag.song_state(song)
        self.assertIn('play=True', text)
        self.assertIn('q=q_bar', text)
        self.assertIn('tempo=120.000', text)
        self.assertIn('t=?', text, 'FakeSong no tiene current_song_time')

    def test_quantization_enum_is_shortened(self):
        song = FakeSong()
        song.clip_trigger_quantization = 'Quantization.q_bar'
        self.assertIn('q=q_bar', Diag.song_state(song))

    def test_track_state(self):
        track = FakeTrack('Nord')
        track.arm = True
        text = Diag.track_state(track, 7)
        self.assertTrue(text.startswith('pista 7 '), text)
        self.assertIn("'Nord'", text)
        self.assertIn('arm=True', text)
        self.assertIn("in='Ext. In'", text)
        self.assertIn('mon=1', text)

    def test_slot_state_with_and_without_clip(self):
        slot = FakeSlot(FakeTrack())
        self.assertIn('clip=False', Diag.slot_state(slot))
        self.assertNotIn('| clip', Diag.slot_state(slot))
        slot.clip = FakeClip(is_recording=True, length=16.0)
        text = Diag.slot_state(slot)
        self.assertIn('clip=True', text)
        self.assertIn('rec=True', text)
        self.assertIn('len=16.000', text)

    def test_send_values(self):
        song = FakeSong(num_tracks=3)
        song.tracks[1].mixer_device.sends[0].value = 1.0
        self.assertEqual('t0=0.000 t1=1.000 t2=0.000', Diag.send_values(song.tracks, 0))

    def test_send_values_out_of_range_index(self):
        song = FakeSong(num_tracks=2)
        self.assertEqual('t0=? t1=?', Diag.send_values(song.tracks, 5))

    def test_saved_sends(self):
        song = FakeSong(num_tracks=2)
        send = song.tracks[0].mixer_device.sends[0]
        saved = {'sends': [(send, 0.3)]}
        send.value = 1.0
        self.assertEqual('0.300->1.000', Diag.saved_sends(saved))
        self.assertEqual('(ninguno)', Diag.saved_sends({'sends': []}))
        self.assertEqual('(ninguno)', Diag.saved_sends({}))

    def test_never_raises_on_broken_objects(self):
        broken = Broken()
        for func in (Diag.song_state, Diag.track_state, Diag.slot_state, Diag.send_value):
            text = func(broken)
            self.assertTrue(isinstance(text, str), func)
            self.assertIn('?', text)
        self.assertEqual('t0=?', Diag.send_values([broken], 0))
        self.assertEqual('?', Diag.saved_sends(broken))


if __name__ == '__main__':
    unittest.main()
