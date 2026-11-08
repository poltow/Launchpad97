"""Dobles minimos de la API de Live para los tests de ClipActions y Routing."""


class FakeClip(object):
    def __init__(self, is_playing=False, is_recording=False, length=4.0, gain=0.85):
        self.is_playing = is_playing
        self.is_recording = is_recording
        self.is_triggered = False
        self.length = length
        self.looping = True
        self.quantize_calls = []
        self._gain = float(gain)
        self.raise_on_gain = None
        self.gain_writes = 0

    def quantize(self, grid, amount):
        self.quantize_calls.append((grid, amount))

    # gain con curva simulada: dB = 40 * (gain - 0.85), -inf en 0
    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        if self.raise_on_gain:
            raise self.raise_on_gain
        self.gain_writes += 1
        self._gain = float(value)

    @property
    def gain_display_string(self):
        if self._gain <= 0.0:
            return '-inf dB'
        return '%+.1f dB' % (40.0 * (self._gain - 0.85))


class FakeSlot(object):
    def __init__(self, track, clip=None):
        self.canonical_parent = track
        self.clip = clip
        self.fire_calls = []
        self.stop_calls = 0
        self.deleted = False
        self.is_triggered = False
        self.will_record_on_start = False
        self.has_stop_button = True
        self.raise_on_duplicate = None
        self.raise_on_fire = None

    @property
    def has_clip(self):
        return self.clip is not None

    @property
    def is_playing(self):
        return self.clip is not None and self.clip.is_playing

    @property
    def is_recording(self):
        return self.clip is not None and self.clip.is_recording

    def fire(self, **kwargs):
        if self.raise_on_fire:
            raise self.raise_on_fire
        self.fire_calls.append(kwargs)

    def stop(self):
        self.stop_calls += 1

    def delete_clip(self):
        if self.clip is None:
            raise RuntimeError('no clip')
        self.deleted = True
        self.clip = None

    def duplicate_clip_to(self, target):
        if self.raise_on_duplicate:
            raise self.raise_on_duplicate
        if self.clip is None:
            raise RuntimeError('no clip')
        target.clip = FakeClip()


class FakeSend(object):
    def __init__(self, value=0.0):
        self.value = value


class FakeMixer(object):
    def __init__(self, num_sends):
        self.sends = [FakeSend() for _ in range(num_sends)]


class FakeTrack(object):
    def __init__(self, name='t', can_be_armed=True, has_audio_input=True, num_sends=1):
        self.name = name
        self.can_be_armed = can_be_armed
        self.has_audio_input = has_audio_input
        self.arm = False
        self.playing_slot_index = -1
        self.fired_slot_index = -1
        self.stop_all_calls = 0
        self.clip_slots = []
        self.mixer_device = FakeMixer(num_sends)
        self.input_routings = ['Ext. In', 'Resampling', 'A-Return', 'No Input']
        self.current_input_routing = 'Ext. In'
        self.current_monitoring_state = 1
        self.input_history = []

    def __setattr__(self, name, value):
        if name == 'current_input_routing' and hasattr(self, 'input_history'):
            self.input_history.append(value)
        object.__setattr__(self, name, value)

    def stop_all_clips(self):
        self.stop_all_calls += 1


class FakeReturnTrack(object):
    def __init__(self, name='A Return'):
        self.name = name
        self.output_routings = ['Master', 'Ext. Out', 'Sends Only']
        self.current_output_routing = 'Master'


class FakeScene(object):
    def __init__(self, name=''):
        self.name = name
        self.fire_calls = 0
        self.is_triggered = False
        self.clip_slots = []

    def fire(self):
        self.fire_calls += 1


class FakeSong(object):
    def __init__(self, num_tracks=8, num_scenes=8, num_returns=1):
        self.clip_trigger_quantization = 'q_bar'
        self.quantization_history = []
        self.undo_begin = 0
        self.undo_end = 0
        self.tempo = 120.0
        self.metronome = False
        self.signature_numerator = 4
        self.signature_denominator = 4
        self.return_tracks = [FakeReturnTrack('%s Return' % chr(65 + i)) for i in range(num_returns)]
        self.create_return_calls = 0
        self.raise_on_create_return = None
        self.tracks = [FakeTrack('t%d' % i, num_sends=num_returns) for i in range(num_tracks)]
        self.scenes = [FakeScene() for _ in range(num_scenes)]
        for scene in self.scenes:
            for track in self.tracks:
                slot = FakeSlot(track)
                scene.clip_slots.append(slot)
                track.clip_slots.append(slot)

    def __setattr__(self, name, value):
        if name == 'clip_trigger_quantization' and hasattr(self, 'quantization_history'):
            self.quantization_history.append(value)
        object.__setattr__(self, name, value)

    def begin_undo_step(self):
        self.undo_begin += 1

    def end_undo_step(self):
        self.undo_end += 1

    def create_return_track(self):
        if self.raise_on_create_return:
            raise self.raise_on_create_return
        self.create_return_calls += 1
        self.return_tracks.append(FakeReturnTrack('%s Return' % chr(65 + len(self.return_tracks))))
        for track in self.tracks:
            track.mixer_device.sends.append(FakeSend())

    def slot(self, track, scene):
        return self.scenes[scene].clip_slots[track]
