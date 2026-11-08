"""Operaciones sobre objetos de Live por duck typing. Sin import Live:
las constantes de cuantizacion llegan por parametro."""
import time

try:
    from . import consts
    from . import ClipGain
    from . import Diag
except (ImportError, ValueError):
    import consts
    import ClipGain
    import Diag


class ClipActions(object):

    def __init__(self, song, no_quantization, log=None):
        self._song = song
        self._no_q = no_quantization
        self._log = log or (lambda message: None)

    # -- helpers ----------------------------------------------------------

    def _diag(self, text):
        """Linea de diagnostico (ver consts.DIAG_LOG). Nunca lanza."""
        if not consts.DIAG_LOG:
            return
        try:
            self._log('LaunchpadLooper diag: %s' % text)
        except Exception:
            pass

    def _song_state(self):
        return Diag.song_state(self._song)

    def _undo_step(self, func):
        self._song.begin_undo_step()
        try:
            return func()
        finally:
            self._song.end_undo_step()

    def _guard(self, label, func):
        try:
            return func()
        except RuntimeError as error:
            self._log('LaunchpadLooper %s: %s' % (label, error))
            return False

    def record_length_beats(self, bars):
        song = self._song
        return 4.0 / song.signature_denominator * song.signature_numerator * bars

    # -- pads -------------------------------------------------------------

    def stop_immediately(self, slot):
        song = self._song
        saved = song.clip_trigger_quantization
        self._diag('stop_immediately: %s | %s | q %s -> %s' % (
            Diag.track_state(slot.canonical_parent), Diag.slot_state(slot),
            Diag.quant(saved), Diag.quant(self._no_q)))
        song.clip_trigger_quantization = self._no_q
        try:
            self._guard('stop_immediately', slot.stop)
        finally:
            song.clip_trigger_quantization = saved
        self._diag('stop_immediately: q repuesta a %s' % Diag.quant(song.clip_trigger_quantization))

    def record(self, slot, fixed_length_bars):
        """Arma la pista del slot (sin tocar otras) y dispara la grabacion.
        Devuelve True si la pista fue armada por esta llamada."""
        track = slot.canonical_parent
        self._diag('record: fixed=%s | %s | %s | %s' % (
            fixed_length_bars, self._song_state(), Diag.track_state(track), Diag.slot_state(slot)))
        if not track.can_be_armed:
            self._diag('record: la pista no se puede armar, no se dispara')
            return False
        armed_by_us = False
        if not track.arm:
            self._diag('record: armando la pista')
            track.arm = True
            armed_by_us = True
            self._diag('record: arm leido=%s' % Diag.attr(track, 'arm'))
        if fixed_length_bars:
            length = self.record_length_beats(fixed_length_bars)
            quant = self._song.clip_trigger_quantization
            self._diag('record: fire(record_length=%s, launch_quantization=%s)' % (length, Diag.quant(quant)))
            self._guard('record', lambda: slot.fire(record_length=length, launch_quantization=quant))
        else:
            self._diag('record: fire() sin largo')
            self._guard('record', slot.fire)
        self._diag('record: fire volvio | %s | %s' % (Diag.slot_state(slot), Diag.track_state(track)))
        return armed_by_us

    def launch(self, slot):
        self._diag('launch: %s | %s' % (self._song_state(), Diag.slot_state(slot)))
        self._guard('launch', slot.fire)

    def close_recording(self, slot):
        self._diag('close_recording: %s | %s' % (self._song_state(), Diag.slot_state(slot)))
        self._guard('close_recording', slot.fire)

    def delete_clip(self, slot):
        if not slot.has_clip:
            return False
        self._diag('delete_clip: %s' % Diag.slot_state(slot))
        return self._guard('delete_clip', lambda: (slot.delete_clip(), True)[1])

    def copy_clip(self, source, target):
        if not source.has_clip or target.has_clip:
            return False
        self._diag('copy_clip: origen %s -> destino %s' % (Diag.slot_state(source), Diag.slot_state(target)))
        return self._guard('copy_clip', lambda: (source.duplicate_clip_to(target), True)[1])

    def quantize_clip(self, slot, grid, amount):
        if not slot.has_clip:
            return False
        self._diag('quantize_clip: grid=%s amount=%s | %s' % (grid, amount, Diag.slot_state(slot)))
        return self._guard('quantize_clip', lambda: (slot.clip.quantize(grid, amount), True)[1])

    # -- pistas y filas ---------------------------------------------------

    def stop_track(self, track):
        self._diag('stop_track: %s | %s' % (self._song_state(), Diag.track_state(track)))
        self._guard('stop_track', track.stop_all_clips)

    def stop_row(self, tracks, row):
        for track in tracks:
            if track.playing_slot_index == row:
                self.stop_track(track)

    def delete_row(self, scene, snap_name):
        def work():
            self._diag('delete_row: escena %r' % str(Diag.attr(scene, 'name')))
            for slot in scene.clip_slots:
                if slot.has_clip:
                    self._guard('delete_row', slot.delete_clip)
            if scene.name == snap_name:
                scene.name = ''
            return True
        return self._undo_step(work)

    # -- snapshot e INIT --------------------------------------------------

    def take_snapshot(self, scenes, target_row, copies, snap_name):
        def work():
            self._diag('take_snapshot: fila %s, copias %s' % (target_row, copies))
            target_scene = scenes[target_row]
            for track_index, source_row in copies:
                source = scenes[source_row].clip_slots[track_index]
                target = target_scene.clip_slots[track_index]
                self.copy_clip(source, target)
            target_scene.name = snap_name
            return True
        return self._undo_step(work)

    def init_grid(self, scenes, num_tracks, snap_name):
        def work():
            self._diag('init_grid: %s' % self._song_state())
            for scene in scenes:
                for slot in list(scene.clip_slots)[:num_tracks]:
                    if slot.has_clip:
                        self._guard('init_grid', slot.delete_clip)
                if scene.name == snap_name:
                    scene.name = ''
            return True
        return self._undo_step(work)

    # -- bounce -----------------------------------------------------------

    def bounce_start(self, origin_slots, target_slot, length_beats, send_index, input_routing):
        """Sube los sends de los origenes, rutea y arma el destino y dispara
        la grabacion. Devuelve lo guardado para bounce_restore, o None si
        Live rechazo algo (en ese caso ya quedo todo repuesto)."""
        target_track = target_slot.canonical_parent
        saved = {
            'sends': [],
            'target_track': target_track,
            'input': target_track.current_input_routing,
            'monitor': target_track.current_monitoring_state,
            'arm': bool(target_track.arm),
        }
        self._diag('bounce_start: guardado input=%r monitor=%s arm=%s | %s | destino %s | %s' % (
            str(saved['input']), saved['monitor'], saved['arm'], self._song_state(),
            Diag.track_state(target_track), Diag.slot_state(target_slot)))
        try:
            for slot in origin_slots:
                track = slot.canonical_parent
                send = track.mixer_device.sends[send_index]
                saved['sends'].append((send, send.value))
                self._diag('bounce_start: send %s de %r: %s -> %s' % (
                    send_index, str(Diag.attr(track, 'name')), Diag.send_value(send), consts.BOUNCE_SEND_LEVEL))
                send.value = consts.BOUNCE_SEND_LEVEL
                self._diag('bounce_start: send leido=%s' % Diag.send_value(send))
            self._diag('bounce_start: entrada destino %r -> %r' % (str(saved['input']), input_routing))
            target_track.current_input_routing = input_routing
            self._diag('bounce_start: entrada leida=%r' % str(Diag.attr(target_track, 'current_input_routing')))
            self._diag('bounce_start: monitor %s -> %s' % (saved['monitor'], consts.MONITOR_OFF))
            target_track.current_monitoring_state = consts.MONITOR_OFF
            self._diag('bounce_start: arm %s -> True' % saved['arm'])
            target_track.arm = True
            quant = self._song.clip_trigger_quantization
            self._diag('bounce_start: fire(record_length=%s, launch_quantization=%s) | %s' % (
                float(length_beats), Diag.quant(quant), self._song_state()))
            target_slot.fire(record_length=float(length_beats), launch_quantization=quant)
            self._diag('bounce_start: fire volvio | %s | %s' % (
                Diag.slot_state(target_slot), Diag.track_state(target_track)))
        except RuntimeError as error:
            self._log('LaunchpadLooper bounce_start: %s' % error)
            self._diag('bounce_start: Live rechazo, reponiendo')
            self.bounce_restore(saved)
            return None
        return saved

    def bounce_restore(self, saved):
        if not saved:
            self._diag('bounce_restore: nada guardado')
            return
        self._diag('bounce_restore: %s | sends guardados %s' % (self._song_state(), Diag.saved_sends(saved)))
        for send, value in saved.get('sends', []):
            before = Diag.send_value(send)
            self._guard('bounce_restore send', lambda s=send, v=value: setattr(s, 'value', v))
            self._diag('bounce_restore: send %s -> %s, leido=%s' % (before, Diag.num(value), Diag.send_value(send)))
        track = saved.get('target_track')
        if track is not None:
            self._diag('bounce_restore: destino antes | %s' % Diag.track_state(track))
            self._guard('bounce_restore input',
                        lambda: setattr(track, 'current_input_routing', saved['input']))
            self._diag('bounce_restore: entrada -> %r, leida=%r' % (
                str(saved['input']), str(Diag.attr(track, 'current_input_routing'))))
            self._guard('bounce_restore monitor',
                        lambda: setattr(track, 'current_monitoring_state', saved['monitor']))
            self._diag('bounce_restore: monitor -> %s, leido=%s' % (
                saved['monitor'], Diag.attr(track, 'current_monitoring_state')))
            self._guard('bounce_restore arm', lambda: setattr(track, 'arm', saved['arm']))
            self._diag('bounce_restore: arm -> %s, leido=%s' % (saved['arm'], Diag.attr(track, 'arm')))
        self._diag('bounce_restore: fin, sends %s' % Diag.saved_sends(saved))

    def bounce_cancel(self, target_slot):
        """Tira lo grabado si hay clip; si solo esta disparado, quita el disparo."""
        self._diag('bounce_cancel: %s' % Diag.slot_state(target_slot))
        if target_slot.has_clip:
            self._guard('bounce_cancel', target_slot.delete_clip)
        else:
            self._guard('bounce_cancel', target_slot.stop)

    def stop_tracks(self, tracks):
        for track in tracks:
            self.stop_track(track)

    # -- gain de clip -----------------------------------------------------

    def set_gain_level(self, clip, calibration, index):
        """Fija el gain del clip en el nivel `index` de ClipGain.LEVELS_DB.
        Si la tabla no esta calibrada, calibra primero sobre este clip
        (biseccion leyendo gain_display_string). Todo en un solo paso de
        Undo. Devuelve True si pudo escribir."""
        def run():
            original = clip.gain
            started = time.time()
            self._diag('gain: nivel %s (%s dB), gain actual=%s (%s), calibrada=%s | %s' % (
                index, ClipGain.LEVELS_DB[index], Diag.num(original),
                Diag.attr(clip, 'gain_display_string'), calibration.is_done(), self._song_state()))
            try:
                if not calibration.is_done():
                    approx = calibration.calibrate(lambda v: setattr(clip, 'gain', v),
                                                   lambda: clip.gain_display_string)
                    self._diag('gain: calibracion en %.0f ms, aproximados=%s' % (
                        (time.time() - started) * 1000.0, approx))
                    if approx is None:
                        self._log('LaunchpadLooper gain: texto en dB ilegible, tabla aproximada')
                    elif approx:
                        self._log('LaunchpadLooper gain: niveles aproximados %s' % approx)
                clip.gain = float(calibration.value_for(index))
                self._diag('gain: escrito %s, leido %s (%s) en %.0f ms' % (
                    Diag.num(calibration.value_for(index)), Diag.num(Diag.attr(clip, 'gain')),
                    Diag.attr(clip, 'gain_display_string'), (time.time() - started) * 1000.0))
                return True
            except RuntimeError as error:
                self._log('LaunchpadLooper set_gain_level: %s' % error)
                try:
                    clip.gain = original
                except RuntimeError:
                    pass
                return False
        return self._undo_step(run)

    # -- globales ---------------------------------------------------------

    def undo(self):
        can_undo = getattr(self._song, 'can_undo', True)
        self._diag('undo: can_undo=%s | %s' % (can_undo, self._song_state()))
        if can_undo:
            self._guard('undo', self._song.undo)
            self._diag('undo: volvio, can_undo=%s can_redo=%s' % (
                getattr(self._song, 'can_undo', '?'), getattr(self._song, 'can_redo', '?')))

    def redo(self):
        can_redo = getattr(self._song, 'can_redo', True)
        self._diag('redo: can_redo=%s | %s' % (can_redo, self._song_state()))
        if can_redo:
            self._guard('redo', self._song.redo)
            self._diag('redo: volvio, can_undo=%s can_redo=%s' % (
                getattr(self._song, 'can_undo', '?'), getattr(self._song, 'can_redo', '?')))

    def set_tempo(self, tempo):
        self._song.tempo = max(consts.TEMPO_MIN, min(consts.TEMPO_MAX, float(tempo)))

    def toggle_metronome(self):
        self._song.metronome = not self._song.metronome
        return self._song.metronome
