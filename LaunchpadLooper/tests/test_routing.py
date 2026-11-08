import unittest

from LaunchpadLooper import Routing as R
from LaunchpadLooper.tests.fakes import FakeSong, FakeTrack


class FindReturnTest(unittest.TestCase):

    def test_finds_by_exact_name(self):
        song = FakeSong(num_returns=2)
        song.return_tracks[1].name = 'BOUNCE'
        index, track = R.find_return(song, 'BOUNCE')
        self.assertEqual(1, index)
        self.assertIs(song.return_tracks[1], track)

    def test_missing_return(self):
        song = FakeSong(num_returns=1)
        self.assertEqual((None, None), R.find_return(song, 'BOUNCE'))

    def test_finds_ignoring_case_spaces_and_letter_prefix(self):
        for shown in ('bounce', 'A BOUNCE', 'B-Bounce', ' Bounce ', 'a_bounce'):
            song = FakeSong(num_returns=1)
            song.return_tracks[0].name = shown
            index, track = R.find_return(song, 'BOUNCE')
            self.assertEqual(0, index, shown)
            self.assertIs(song.return_tracks[0], track)

    def test_does_not_match_other_names(self):
        for shown in ('REBOUNCE', 'BOUNCE 2', 'Return', ''):
            song = FakeSong(num_returns=1)
            song.return_tracks[0].name = shown
            self.assertEqual((None, None), R.find_return(song, 'BOUNCE'), shown)

    def test_return_names(self):
        song = FakeSong(num_returns=2)
        song.return_tracks[1].name = 'BOUNCE'
        self.assertEqual(['A Return', 'BOUNCE'], R.return_names(song))


class EnsureReturnTest(unittest.TestCase):

    def test_creates_names_and_sets_sends_only_when_missing(self):
        song = FakeSong(num_returns=1)
        index, track, created = R.ensure_return(song, 'BOUNCE', 'Sends Only')
        self.assertTrue(created)
        self.assertEqual(1, index)
        self.assertEqual('BOUNCE', track.name)
        self.assertEqual('Sends Only', track.current_output_routing)
        self.assertEqual(1, song.create_return_calls)

    def test_takes_existing_and_forces_sends_only(self):
        song = FakeSong(num_returns=1)
        song.return_tracks[0].name = 'BOUNCE'
        song.return_tracks[0].current_output_routing = 'Master'
        index, track, created = R.ensure_return(song, 'BOUNCE', 'Sends Only')
        self.assertFalse(created)
        self.assertEqual(0, index)
        self.assertEqual('Sends Only', track.current_output_routing)
        self.assertEqual(0, song.create_return_calls)

    def test_create_failure_returns_none(self):
        song = FakeSong(num_returns=1)
        song.raise_on_create_return = RuntimeError('max returns')
        self.assertEqual((None, None, False), R.ensure_return(song, 'BOUNCE', 'Sends Only'))


class InputRoutingTest(unittest.TestCase):

    def routing(self, candidates, index=0, name='BOUNCE'):
        track = FakeTrack()
        track.input_routings = ['Ext. In'] + candidates + ['No Input']
        return R.input_routing_for(track, index, name)

    def test_accepts_name_with_or_without_letter(self):
        self.assertEqual('BOUNCE', self.routing(['BOUNCE']))
        self.assertEqual('A-BOUNCE', self.routing(['A-BOUNCE']))
        self.assertEqual('A BOUNCE', self.routing(['A BOUNCE']))
        self.assertEqual('B-BOUNCE', self.routing(['B-BOUNCE'], index=1))

    def test_rejects_other_tracks_and_wrong_letter(self):
        self.assertIsNone(self.routing(['DEBOUNCE']))
        self.assertIsNone(self.routing(['B-BOUNCE'], index=0))
        self.assertIsNone(self.routing(['3-Audio', 'Resampling']))

    def test_default_return_name_matches_live_display(self):
        self.assertEqual('A-Return', self.routing(['A-Return'], index=0, name='A Return'))

    def test_case_insensitive(self):
        self.assertEqual('a-bounce', self.routing(['a-bounce']))


if __name__ == '__main__':
    unittest.main()
