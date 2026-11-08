"""SessionComponent 8x8 fija: pads, laterales, LEDs, desarme al cerrar."""
import time
import Live
from _Framework.SessionComponent import SessionComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SubjectSlot import subject_slot
from _Framework import Task

try:
    from . import consts
    from . import Dispatch
    from . import SlotColors
    from . import Pulse
    from . import Messages
    from . import BounceGuard
    from . import Routing
    from . import ClipGain
    from . import Diag
    from .SnapshotPlanner import plan_snapshot
    from .BouncePlanner import plan_bounce
    from .BounceState import BounceSelection, BounceJob
    from .FixedLengthTracker import FixedLengthTracker
except (ImportError, ValueError):
    import consts
    import Dispatch
    import SlotColors
    import Pulse
    import Messages
    import BounceGuard
    import Routing
    import ClipGain
    import Diag
    from SnapshotPlanner import plan_snapshot
    from BouncePlanner import plan_bounce
    from BounceState import BounceSelection, BounceJob
    from FixedLengthTracker import FixedLengthTracker

_Q = Live.Song.Quantization
_Rec_Q = Live.Song.RecordingQuantization

QUANTIZE_GRIDS = {
    '1/4': _Rec_Q.rec_q_quarter,
    '1/8': _Rec_Q.rec_q_eight,
    '1/8t': _Rec_Q.rec_q_eight_triplet,
    '1/16': _Rec_Q.rec_q_sixtenth,
    '1/16t': _Rec_Q.rec_q_sixtenth_triplet,
}


class LooperClipSlot(ClipSlotComponent):

    def __init__(self, *a, **k):
        super(LooperClipSlot, self).__init__(*a, **k)
        self._parent = None
        self.track_index = -1
        self.scene_index = -1

    def set_parent(self, parent, track_index, scene_index):
        self._parent = parent
        self.track_index = track_index
        self.scene_index = scene_index

    def live_slot(self):
        return self._clip_slot

    def key(self):
        return (self.track_index, self.scene_index)

    def launch_button(self):
        return self._launch_button_value.subject

    def state(self):
        try:
            return self._state()
        except Exception:
            # el ClipSlot de Live puede haber dejado de existir (pista borrada,
            # Undo de una creacion): se ve como vacio hasta que Live reasigne
            return SlotColors.EMPTY

    def _state(self):
        slot = self._clip_slot
        if slot is None:
            return SlotColors.EMPTY
        track = slot.canonical_parent
        has_clip = slot.has_clip
        clip = slot.clip if has_clip else None
        is_playing = bool(clip is not None and clip.is_playing)
        is_recording = bool(clip is not None and clip.is_recording)
        if clip is not None:
            is_triggered = bool(clip.is_triggered)
        else:
            is_triggered = bool(slot.is_triggered)
        will_record = bool(slot.will_record_on_start) if not has_clip else False
        stop_pending = bool(track.fired_slot_index == -2) and (is_playing or is_recording)
        ending_soon = self._parent is not None and self._parent.ending_soon(self.key())
        return SlotColors.slot_state(has_clip, is_triggered, will_record,
                                     is_playing, is_recording, stop_pending,
                                     ending_soon=ending_soon)

    def recording_flags(self):
        """(is_recording, is_triggered) del slot de Live, para el tracker."""
        slot = self._clip_slot
        if slot is None:
            return (False, False)
        try:
            if slot.has_clip:
                clip = slot.clip
                return (bool(clip.is_recording), bool(clip.is_triggered))
            return (False, bool(slot.is_triggered))
        except Exception:
            return (False, False)

    def _feedback_value(self):
        if self._parent is None or self._clip_slot is None:
            return 'Looper.Slot.Empty'
        return self._parent.slot_color_for(self)

    @subject_slot('value')
    def _launch_button_value(self, value):
        if self.is_enabled() and self._parent is not None and self._clip_slot is not None:
            if value:
                self._parent.on_pad(self)

    @subject_slot('is_recording')
    def _on_recording_state_changed(self):
        self.update()
        if self._parent is not None:
            self._parent.on_recording_changed(self)

    @subject_slot('has_clip')
    def _on_clip_state_changed(self):
        self._update_clip_property_slots()
        self.update()
        if self._parent is not None:
            self._parent.on_recording_changed(self)


class LooperScene(SceneComponent):
    clip_slot_component_type = LooperClipSlot

    def __init__(self, *a, **k):
        super(LooperScene, self).__init__(*a, **k)
        self._parent = None
        self.scene_index = -1

    def set_parent(self, parent, scene_index):
        self._parent = parent
        self.scene_index = scene_index
        for track_index, slot in enumerate(self._clip_slots):
            slot.set_parent(parent, track_index, scene_index)

    def live_scene(self):
        return self._scene

    @subject_slot('value')
    def _launch_value(self, value):
        if self.is_enabled() and self._parent is not None and self._scene is not None:
            if value:
                self._parent.on_lateral(self)

    def launch_button(self):
        return self._launch_button

    def _update_launch_button(self):
        if self.is_enabled() and self._launch_button is not None:
            if self._parent is None or self._scene is None:
                self._launch_button.set_light('Looper.Scene.Off')
            else:
                self._launch_button.set_light(self._parent.scene_color_for(self))


class LooperSession(SessionComponent):
    scene_component_type = LooperScene

    def __init__(self, settings, actions, modifiers, control_surface):
        self._settings = settings
        self._actions = actions
        self._modifiers = modifiers
        self._control_surface = control_surface
        self._copy_origin = None
        self._armed_by_script = []
        self._init_pending = False
        self._blink_on = True
        self._pulse_phase = Pulse.PULSE_BEAT
        self._fixed_tracker = FixedLengthTracker()
        self._pulse_listeners = []
        self._chord_break_listeners = []
        self._bounce_sel = BounceSelection(consts.LONG_PRESS)
        self._bounce_job = None
        self._last_bounce = None  # (hora, job, indice del send) del ultimo bounce terminado, para Undo
        self._gain_calibration = ClipGain.Calibration()  # tabla float->dB, una por sesion
        super(LooperSession, self).__init__(num_tracks=consts.GRID_SIZE,
                                            num_scenes=consts.GRID_SIZE,
                                            enable_skinning=False,
                                            name='Looper_Session',
                                            is_root=True)
        for scene_index in range(consts.GRID_SIZE):
            self.scene(scene_index).set_parent(self, scene_index)
        self._register_timer_callback(self._on_tick)
        self.song().add_current_song_time_listener(self._on_song_time)

    def disconnect(self):
        try:
            self._unregister_timer_callback(self._on_tick)
        except Exception:
            pass
        try:
            if self.song().current_song_time_has_listener(self._on_song_time):
                self.song().remove_current_song_time_listener(self._on_song_time)
        except Exception:
            pass
        self.diag('disconnect | %s | %s | armadas_por_script=%s' % (
            self._song_state(), self._bounce_state(), self._armed_names()))
        self._pulse_listeners = []
        self._chord_break_listeners = []
        self._copy_origin = None
        self._armed_by_script = []
        if self._bounce_job is not None:
            self._abort_bounce()
        super(LooperSession, self).disconnect()

    def update(self):
        """SessionComponent.update() no baja a escenas ni slots: lo hacemos aca
        para que modificadores y pulso se reflejen en toda la grilla."""
        super(LooperSession, self).update()
        if not self.is_enabled() or not getattr(self, '_scenes', None):
            return
        for scene in self._scenes:
            scene._update_launch_button()
            for slot in scene._clip_slots:
                slot.update()

    def show(self, event, **kw):
        text = Messages.text(event, **kw)
        if text:
            try:
                self._control_surface.show_message(text)
            except Exception:
                pass
            if (event.startswith('bounce') or event.startswith('gain')
                    or event in ('press_snapshot', 'undo', 'redo', 'init_done', 'delete_row')):
                self.log('%s' % text)

    def log(self, text):
        try:
            self._control_surface.log_message('LaunchpadLooper: %s' % text)
        except Exception:
            pass

    def diag(self, text):
        """Linea de diagnostico (ver consts.DIAG_LOG). Nunca lanza."""
        if not consts.DIAG_LOG:
            return
        try:
            self._control_surface.log_message('LaunchpadLooper diag: %s' % text)
        except Exception:
            pass

    def _song_state(self):
        return Diag.song_state(self.song())

    def _bounce_state(self):
        """Resumen del bounce en curso para el log, o 'sin bounce'."""
        if self._bounce_job is None:
            return 'sin bounce'
        return self._bounce_state_of(self._bounce_job)

    def _bounce_state_of(self, job):
        return 'bounce destino=%s origenes=%s started=%s closing=%s origins_stopped=%s' % (
            job.target, job.origins, job.started, job.closing, job.origins_stopped)

    def _slot_state_of(self, key):
        try:
            return Diag.slot_state(self.scene(key[1]).clip_slot(key[0]).live_slot())
        except Exception:
            return 'slot=?'

    def _track_state_of(self, index):
        try:
            return Diag.track_state(self.tracks()[index], index)
        except Exception:
            return 'pista=?'

    def _armed_names(self):
        return [str(Diag.attr(track, 'name')) for track in self._armed_by_script]

    # -- acceso -----------------------------------------------------------

    def tracks(self):
        return list(self.song().tracks)[:consts.GRID_SIZE]

    def scenes(self):
        return list(self.song().scenes)[:consts.GRID_SIZE]

    def blink_on(self):
        return self._blink_on

    def pulse_phase(self):
        return self._pulse_phase

    def modifier(self):
        return self._modifiers.active()

    # -- gestos -----------------------------------------------------------

    def on_pad(self, slot_component):
        track, scene = slot_component.key()
        if self._modifiers.chord_held():
            # un pad con acorde abajo (INIT) no es un acorde: el MK1
            # manda Stop y Copy fantasma con Delete abajo. Se rompe el
            # acorde y el pad sigue con el modificador que bajo primero
            self._break_chord('pad %s' % ((track, scene),))
        slot = slot_component.live_slot()
        state = slot_component.state()
        modifier = self.modifier()
        if modifier is not None:
            self._modifiers.note_pad_touch()
        decision = BounceGuard.pad_decision(self._bounce_job, modifier, (track, scene), state)
        if decision != BounceGuard.ALLOW:
            if decision == BounceGuard.REJECT:
                self.flash_reject(slot_component.launch_button())
                self.show('bounce_busy')
            elif decision == BounceGuard.CANCEL:
                self.cancel_bounce()
            elif decision == BounceGuard.CLOSE:
                self.close_bounce()
            self.update()
            return
        action = Dispatch.pad_action(modifier, state, self._copy_origin is not None)
        if modifier == 'snapshot':
            self.log('pad %s con Snapshot abajo: estado %s, accion %s, seleccion activa %s'
                     % ((track, scene), state, action, self._bounce_sel.is_active()))
        self.diag('pad %s estado=%s mod=%s accion=%s | %s | %s | %s' % (
            (track, scene), state, modifier, action, self._song_state(),
            self._bounce_state(), Diag.slot_state(slot)))
        if action in (Dispatch.BOUNCE_MARK, Dispatch.BOUNCE_TARGET) and not self._bounce_sel.is_active():
            pass  # Snapshot sigue abajo pero el bounce ya arranco: nada
        elif action == Dispatch.BOUNCE_MARK:
            self._bounce_sel.mark((track, scene))
            self.show('bounce_marked', count=len(self._bounce_sel.marked()))
        elif action == Dispatch.BOUNCE_TARGET:
            self._bounce_sel.note_touch()
            self._start_bounce(slot_component)
        elif action == Dispatch.RECORD:
            bars = None
            if self._settings.get('fixed_length_on'):
                bars = self._settings.get('fixed_length_bars')
            if self._actions.record(slot, bars):
                self._armed_by_script.append(slot.canonical_parent)
            if bars:
                self._fixed_tracker.fired(slot_component.key(), bars)
                self.show('record_fixed', track=track, scene=scene, bars=bars)
            else:
                self.show('record', track=track, scene=scene)
        elif action == Dispatch.LAUNCH:
            self._actions.launch(slot)
            self.show('launch', track=track, scene=scene)
        elif action == Dispatch.STOP_IMMEDIATE:
            self._actions.stop_immediately(slot)
            self.show('stop_immediate', track=track)
        elif action == Dispatch.CLOSE_RECORDING:
            self._actions.close_recording(slot)
            self.show('close_recording', track=track, scene=scene)
        elif action == Dispatch.DELETE_CLIP:
            self._actions.delete_clip(slot)
            self._fixed_tracker.forget(slot_component.key())
            self.show('delete_clip', track=track, scene=scene)
        elif action == Dispatch.COPY_SET_ORIGIN:
            self._copy_origin = slot
            self.show('copy_origin', track=track, scene=scene)
        elif action == Dispatch.COPY_PASTE:
            if self._actions.copy_clip(self._copy_origin, slot):
                self.show('copy_paste', track=track, scene=scene)
            else:
                self.flash_reject(slot_component.launch_button())
                self.show('copy_reject')
        elif action == Dispatch.QUANTIZE_CLIP:
            grid_name = self._settings.get('quantize_grid')
            amount = self._settings.get('quantize_amount')
            self._actions.quantize_clip(slot, QUANTIZE_GRIDS[grid_name], amount)
            self.show('quantize_clip', track=track, scene=scene, grid=grid_name, amount=amount)
        elif action == Dispatch.STOP_TRACK:
            self._actions.stop_track(slot.canonical_parent)
            self.show('stop_track', track=track)
        self.update()

    def on_lateral(self, scene_component):
        index = scene_component.scene_index
        if self._modifiers.chord_held():
            self._break_chord('lateral %s' % index)
        modifier = self.modifier()
        if self._bounce_job is not None:
            row_tracks = [i for i, track in enumerate(self.tracks()) if track.playing_slot_index == index]
            if BounceGuard.lateral_decision(self._bounce_job, modifier, index, row_tracks) == BounceGuard.REJECT:
                self.flash_reject(scene_component.launch_button())
                self.show('bounce_busy')
                self.update()
                return
        action, value = Dispatch.lateral_action(modifier, index)
        self.diag('lateral %s mod=%s accion=%s valor=%s | %s | %s' % (
            index, modifier, action, value, self._song_state(), self._bounce_state()))
        if action == Dispatch.FIRE_SCENE:
            live_scene = scene_component.live_scene()
            live_scene.fire()
            self.show('scene', scene=index, name=live_scene.name)
        elif action == Dispatch.SET_FIXED_LENGTH:
            self._settings.set_fixed_length_index(value)
            self._modifiers.note_lateral_touch()
            self.show('fixed_length_bars', bars=self._settings.get('fixed_length_bars'))
        elif action == Dispatch.SET_QUANTIZE_GRID:
            self._settings.set_quantize_grid_index(value)
            self._modifiers.note_lateral_touch()
            self._show_quantize_setting()
        elif action == Dispatch.SET_QUANTIZE_AMOUNT:
            self._settings.set_quantize_amount_index(value)
            self._modifiers.note_lateral_touch()
            self._show_quantize_setting()
        elif action == Dispatch.SET_GAIN:
            self._set_gain_level(value)
        elif action == Dispatch.DELETE_ROW:
            self._actions.delete_row(scene_component.live_scene(), consts.SNAP_NAME)
            self.show('delete_row', scene=index)
        elif action == Dispatch.STOP_ROW:
            self._actions.stop_row(self.tracks(), value)
            self.show('stop_row', scene=index)
        self.update()

    def _show_quantize_setting(self):
        self.show('quantize_setting', grid=self._settings.get('quantize_grid'),
                  amount=self._settings.get('quantize_amount'))

    # -- gain de clip (Snapshot abajo + lateral) ---------------------------

    def _focused_clip(self):
        """Clip del ultimo pad tocado con Snapshot abajo, o None."""
        key = self._bounce_sel.focused()
        if key is None:
            return None
        try:
            slot = self.scene(key[1]).clip_slot(key[0]).live_slot()
            if slot is None or not slot.has_clip:
                return None
            return slot.clip
        except Exception:
            return None

    def _focused_gain_index(self):
        clip = self._focused_clip()
        if clip is None:
            return None
        try:
            return ClipGain.nearest_level(ClipGain.parse_db(clip.gain_display_string))
        except Exception:
            return None

    def _set_gain_level(self, index):
        self._bounce_sel.note_touch()  # tocar un lateral tampoco saca foto al soltar
        clip = self._focused_clip()
        if clip is None:
            self.show('gain_no_focus')
            return
        track, scene = self._bounce_sel.focused()
        if self._actions.set_gain_level(clip, self._gain_calibration, index):
            self.show('gain', track=track, scene=scene, db=clip.gain_display_string)
        else:
            self.show('gain_failed')

    def clear_copy_origin(self):
        self._copy_origin = None

    def set_init_pending(self, pending):
        pending = bool(pending)
        if pending and not self._init_pending:
            self.show('init_pending')
        self._init_pending = pending
        self.update()

    # -- snapshot e INIT --------------------------------------------------

    def take_snapshot(self):
        """Devuelve None si se hizo, o el motivo del rechazo."""
        row, reason, copies = plan_snapshot(_GridView(self))
        if reason is not None:
            self.show('snapshot_reject', reason=reason)
            return reason
        self._actions.take_snapshot(self.scenes(), row, copies, consts.SNAP_NAME)
        self.show('snapshot', scene=row)
        self.update()
        return None

    def init_grid(self):
        """INIT: asegura el retorno BOUNCE y vacia la grilla. El retorno va
        primero, en sus propios pasos de Undo, asi un Undo recupera la grilla
        y el retorno queda."""
        self.diag('INIT | %s | %s' % (self._song_state(), self._bounce_state()))
        try:
            bounce = self.setup_bounce_return()
        except Exception as exc:
            self.log('bounce setup fallo: %r' % (exc,))
            bounce = 'failed'
        self._actions.init_grid(self.scenes(), consts.GRID_SIZE, consts.SNAP_NAME)
        self._copy_origin = None
        self._fixed_tracker = FixedLengthTracker()
        self.set_init_pending(False)
        self.show(Messages.INIT_DONE_BY_BOUNCE[bounce])

    # -- bounce -----------------------------------------------------------

    def bounce_in_progress(self):
        return self._bounce_job is not None

    def top_decision(self, name):
        return BounceGuard.top_decision(self._bounce_job, name)

    def chord_allowed(self):
        return BounceGuard.chord_decision(self._bounce_job) == BounceGuard.ALLOW

    def begin_bounce_select(self, now):
        """Snapshot bajo. Con bounce en curso: cancela o cierra. Si no, abre
        la seleccion."""
        decision = BounceGuard.top_decision(self._bounce_job, 'snapshot')
        if decision == BounceGuard.CANCEL:
            self.cancel_bounce()
        elif decision == BounceGuard.CLOSE:
            self.close_bounce()
        elif decision == BounceGuard.ALLOW:
            self._bounce_sel.press(now)
            self.show('press_snapshot')
        self.update()

    def end_bounce_select(self, now):
        """Snapshot soltado. Devuelve True si se intento la foto y se rechazo."""
        if not self._bounce_sel.is_active():
            return False
        rejected = False
        if self._bounce_sel.release(now) == 'snapshot':
            rejected = self.take_snapshot() is not None
        self.update()
        return rejected

    def _bounce_target_component(self):
        track, scene = self._bounce_job.target
        return self.scene(scene).clip_slot(track)

    def _start_bounce(self, target_component):
        key = target_component.key()
        button = target_component.launch_button()
        grid = _GridView(self)
        fixed = None
        if self._settings.get('fixed_length_on'):
            fixed = self._settings.get('fixed_length_bars')
        marked = self._bounce_sel.marked()
        self.log('bounce: destino %s, marcados %s, fixed %s' % (key, marked, fixed))
        origins, length, reason = plan_bounce(grid, marked, key, fixed, self._bounce_job is not None)
        if reason is not None:
            return self._reject_bounce(button, reason)
        self.log('bounce: origenes %s, largo %s beats' % (origins, length))
        index, return_track = Routing.find_return(self.song(), consts.BOUNCE_RETURN_NAME)
        if return_track is None:
            self.log('sin retorno %s; retornos del set: %s'
                     % (consts.BOUNCE_RETURN_NAME, Routing.return_names(self.song())))
            return self._reject_bounce(button, 'no_return')
        self.log('bounce: retorno %s en indice %s, salida=%s'
                 % (consts.BOUNCE_RETURN_NAME, index, return_track.current_output_routing))
        target_slot = target_component.live_slot()
        target_track = target_slot.canonical_parent
        routing = Routing.input_routing_for(target_track, index, consts.BOUNCE_RETURN_NAME)
        if routing is None:
            self.log('sin entrada desde el retorno; input_routings = %s' % list(target_track.input_routings))
            return self._reject_bounce(button, 'no_return_input')
        self.log('bounce: entrada del destino = %r' % routing)
        origin_slots = [grid.slot(track, scene) for track, scene in origins]
        self.diag('bounce: antes de arrancar | %s | sends %s | %s' % (
            self._song_state(), Diag.send_values(self.tracks(), index),
            Diag.track_state(target_track, key[0])))
        saved = self._actions.bounce_start(origin_slots, target_slot, length, index, routing)
        if saved is None:
            return self._reject_bounce(button, 'live_error')
        bars = int(length // grid.beats_per_bar)
        self._bounce_job = BounceJob(key, origins, saved, bars)
        self._bounce_job.send_index = index
        self.diag('bounce: job creado, %s compases | %s | sends %s' % (
            bars, self._bounce_state(), Diag.send_values(self.tracks(), index)))
        self._fixed_tracker.fired(key, bars)
        self._bounce_sel.clear()
        self.show('bounce_start', count=len(origins), track=key[0], scene=key[1], bars=bars)
        return True

    def setup_bounce_return(self):
        """Parte de INIT: busca el retorno BOUNCE; si no esta lo crea, si esta
        lo toma; en los dos casos salida Sends Only. Devuelve 'created',
        'taken' o 'failed'. No muestra mensaje: lo muestra INIT."""
        index, track, created = Routing.ensure_return(self.song(), consts.BOUNCE_RETURN_NAME, consts.SENDS_ONLY)
        if track is None:
            self.log('bounce setup: no se pudo crear el retorno; retornos: %s' % Routing.return_names(self.song()))
            return 'failed'
        self.log('bounce setup: retorno en indice %s, nombre real %r, creado=%s, salida=%s; retornos: %s'
                 % (index, track.name, created, track.current_output_routing, Routing.return_names(self.song())))
        return 'created' if created else 'taken'

    def cancel_bounce_select(self):
        self._bounce_sel.clear()
        self.update()

    def _reject_bounce(self, button, reason):
        self.flash_reject(button)
        self.show('bounce_reject', reason=reason)
        return False

    def close_bounce(self):
        """Cierra la grabacion en el proximo compas y para los origenes con ella."""
        job = self._bounce_job
        if job is None or job.closing:
            return
        job.closing = True
        self.diag('bounce: cierre pedido | %s | %s' % (self._song_state(), self._bounce_state()))
        self._actions.close_recording(self._bounce_target_component().live_slot())
        self._stop_bounce_origins()
        self.show('bounce_closing')

    def cancel_bounce(self):
        """Tira lo grabado, repone el ruteo, los origenes siguen sonando."""
        job = self._bounce_job
        if job is None:
            return
        self.diag('bounce: cancelacion pedida | %s | %s' % (self._song_state(), self._bounce_state()))
        self._actions.bounce_cancel(self._bounce_target_component().live_slot())
        self._finish_bounce('bounce_cancelled')

    def _abort_bounce(self):
        """Desconexion o transporte parado: detiene el destino y repone."""
        job = self._bounce_job
        if job is None:
            return
        self.diag('bounce: abort (desconexion, transporte parado o disparo perdido) | %s | %s'
                  % (self._song_state(), self._bounce_state()))
        try:
            self._bounce_target_component().live_slot().stop()
        except Exception as error:
            self.diag('bounce: abort, stop del destino fallo: %s' % error)
        self._finish_bounce('bounce_cut')

    def _finish_bounce(self, message):
        job = self._bounce_job
        self._bounce_job = None
        send_index = getattr(job, 'send_index', None)
        self.diag('bounce: fin (%s) | %s | %s | destino %s' % (
            message, self._song_state(), self._bounce_state_of(job),
            self._slot_state_of(job.target)))
        self._actions.bounce_restore(job.saved)
        if send_index is not None:
            self.diag('bounce: tras restore, sends %s' % Diag.send_values(self.tracks(), send_index))
        self._last_bounce = (time.time(), job, send_index)
        self._fixed_tracker.forget(job.target)
        self.show(message)

    def _stop_bounce_origins(self):
        job = self._bounce_job
        if job is None or job.origins_stopped:
            return
        job.origins_stopped = True
        tracks = self.tracks()
        self.diag('bounce: parando origenes %s | %s' % (job.origin_tracks(), self._song_state()))
        self._actions.stop_tracks([tracks[i] for i in job.origin_tracks() if i < len(tracks)])

    def _bounce_tick(self):
        """Sigue el bounce en curso desde el tic. Devuelve True si cambio algo."""
        job = self._bounce_job
        if job is None:
            return False
        is_recording, is_triggered = self._bounce_target_component().recording_flags()
        if not job.started:
            if is_recording:
                job.started = True
                self.diag('bounce: el destino empezo a grabar | %s | %s' % (
                    self._song_state(), self._slot_state_of(job.target)))
                return True
            if not is_triggered:
                self.diag('bounce: el destino no esta disparado ni grabando | %s | %s' % (
                    self._song_state(), self._slot_state_of(job.target)))
                self._abort_bounce()
                return True
            return False
        if not is_recording:
            self.diag('bounce: el destino dejo de grabar | %s' % self._song_state())
            self._finish_bounce('bounce_done' if self.song().is_playing else 'bounce_cut')
            return True
        if not job.origins_stopped and self._fixed_tracker.ending_soon(job.target):
            self._stop_bounce_origins()
            return True
        return False

    # -- desarme al cerrar la grabacion -----------------------------------

    def on_recording_changed(self, slot_component):
        """Llamado desde notificaciones de Live: no se puede cambiar el set
        aca, asi que el desarme se difiere a una tarea."""
        slot = slot_component.live_slot()
        self.diag('recording_changed %s | %s | %s | armadas_por_script=%s' % (
            slot_component.key(), self._song_state(), Diag.slot_state(slot), self._armed_names()))
        if slot is None or not self._armed_by_script:
            return
        if slot.canonical_parent not in self._armed_by_script:
            return
        self.diag('recording_changed: desarme diferido a la proxima tarea')
        self._tasks.add(Task.run(self._disarm_idle_tracks))

    def _disarm_idle_tracks(self):
        self.diag('disarm: revisando %s | %s | %s' % (
            self._armed_names(), self._song_state(), self._bounce_state()))
        for track in list(self._armed_by_script):
            recording = False
            for slot in track.clip_slots:
                if slot.has_clip and slot.clip.is_recording:
                    recording = True
                    break
            if not recording:
                self.diag('disarm: arm=False en %s' % Diag.track_state(track))
                try:
                    track.arm = False
                except RuntimeError as error:
                    self._control_surface.log_message('LaunchpadLooper disarm: %s' % error)
                self._armed_by_script.remove(track)
            else:
                self.diag('disarm: %r sigue grabando, se deja armada' % str(Diag.attr(track, 'name')))

    # -- undo / redo con contexto del ultimo bounce ------------------------

    def _last_bounce_context(self):
        """Que hay para deshacer respecto del ultimo bounce: hace cuanto
        termino y como estan hoy los sends y el destino que toco."""
        if self._last_bounce is None:
            return 'sin bounce previo'
        when, job, send_index = self._last_bounce
        text = 'ultimo bounce hace %.1f s (destino %s, origenes %s)' % (
            time.time() - when, job.target, job.origin_tracks())
        if send_index is not None:
            text += ', sends %s' % Diag.send_values(self.tracks(), send_index)
        text += ', %s' % self._track_state_of(job.target[0])
        return text

    def undo(self):
        self.diag('UNDO pedido | %s | %s | %s' % (
            self._song_state(), self._bounce_state(), self._last_bounce_context()))
        self._actions.undo()
        self.diag('UNDO hecho | %s' % self._last_bounce_context())

    def redo(self):
        self.diag('REDO pedido | %s | %s | %s' % (
            self._song_state(), self._bounce_state(), self._last_bounce_context()))
        self._actions.redo()
        self.diag('REDO hecho | %s' % self._last_bounce_context())

    # -- LEDs -------------------------------------------------------------

    def ending_soon(self, key):
        return self._fixed_tracker.ending_soon(key)

    def _update_fixed_tracker(self, beat_time):
        """Devuelve True si cambio el aviso de ultimo compas de algun slot."""
        changed = False
        current_bar = beat_time.bars if beat_time is not None else 0
        for key in self._fixed_tracker.tracked_keys():
            track_index, scene_index = key
            slot_component = self.scene(scene_index).clip_slot(track_index)
            was_ending = self._fixed_tracker.ending_soon(key)
            is_recording, is_triggered = slot_component.recording_flags()
            now_ending = self._fixed_tracker.update(key, is_recording, is_triggered, current_bar)
            if now_ending != was_ending:
                changed = True
        return changed

    def slot_color_for(self, slot_component):
        state = slot_component.state()
        is_origin = self._copy_origin is not None and slot_component.live_slot() == self._copy_origin
        return SlotColors.slot_color(state, self.modifier(), self._blink_on,
                                     is_copy_origin=is_origin, init_pending=self._init_pending,
                                     is_bounce_mark=self._bounce_sel.is_marked(slot_component.key()))

    def bounce_marked_count(self):
        return len(self._bounce_sel.marked())

    def scene_color_for(self, scene_component):
        modifier = self.modifier()
        index = scene_component.scene_index
        if modifier == 'fixed_length':
            return SlotColors.fixed_length_row(self._settings.fixed_length_index())[index]
        if modifier == 'quantize':
            return SlotColors.quantize_row(self._settings.quantize_grid_index(),
                                           self._settings.quantize_amount_index())[index]
        if modifier == 'snapshot':
            return ClipGain.lateral_color(index, self._focused_gain_index())
        scene = scene_component.live_scene()
        has_playing = False
        has_clips = False
        for slot in list(scene.clip_slots)[:consts.GRID_SIZE]:
            if slot.has_clip:
                has_clips = True
                if slot.clip.is_playing:
                    has_playing = True
        return SlotColors.scene_color(has_playing, has_clips,
                                      bool(scene.is_triggered), modifier, self._blink_on)

    def flash_reject(self, button):
        if button is None:
            return
        button.set_light('Looper.Top.Reject')
        self._tasks.add(Task.sequence(Task.wait(consts.REJECT_FLASH), Task.run(self.update)))

    # -- pulso ------------------------------------------------------------

    def add_pulse_listener(self, callback):
        self._pulse_listeners.append(callback)

    def add_chord_break_listener(self, callback):
        """callback(nombre_del_acorde) cuando un pad o lateral rompe un acorde."""
        self._chord_break_listeners.append(callback)

    def _break_chord(self, source):
        chord = self._modifiers.break_chord()
        if chord is None:
            return
        self.diag('%s rompe acorde %s (pulsacion fantasma o pad con acorde abajo) | %s'
                  % (source, chord, self._song_state()))
        for callback in list(self._chord_break_listeners):
            try:
                callback(chord)
            except Exception as exc:
                self.log('chord break listener fallo: %r' % (exc,))

    def _beat_time(self):
        try:
            return self.song().get_current_beats_song_time()
        except Exception:
            return None

    def _refresh_pulse(self, beat_time):
        """Recalcula la fase del pulso. Devuelve True si cambio el parpadeo."""
        phase = Pulse.pulse_phase(beat_time, self.song().is_playing)
        if phase != self._pulse_phase:
            self._pulse_phase = phase
            for callback in self._pulse_listeners:
                callback()
        on = Pulse.blink_on(phase)
        if on != self._blink_on:
            self._blink_on = on
            return True
        return False

    def _on_song_time(self):
        """Listener de current_song_time: llega muchas veces por segundo
        mientras corre el transporte, mucho mas fino que el tic de 100 ms.
        Solo manda MIDI, nunca cambia el set."""
        if not self.is_enabled():
            return
        if self._refresh_pulse(self._beat_time()):
            self.update()

    def _on_tick(self):
        beat_time = self._beat_time()
        changed = self._update_fixed_tracker(beat_time)
        if self._bounce_tick():
            changed = True
        if self._refresh_pulse(beat_time):
            changed = True
        if changed:
            self.update()


class _GridView(object):
    """Adaptador de la ventana 8x8 para SnapshotPlanner y BouncePlanner."""

    def __init__(self, session):
        self.num_tracks = consts.GRID_SIZE
        self.num_scenes = consts.GRID_SIZE
        self._scenes = session.scenes()
        self._tracks = session.tracks()
        song = session.song()
        self.beats_per_bar = 4.0 / song.signature_denominator * song.signature_numerator

    def _slot(self, track, scene):
        if scene >= len(self._scenes):
            return None
        slots = self._scenes[scene].clip_slots
        return slots[track] if track < len(slots) else None

    def slot(self, track, scene):
        return self._slot(track, scene)

    def clip_length(self, track, scene):
        slot = self._slot(track, scene)
        if slot is None or not slot.has_clip:
            return 0.0
        return float(slot.clip.length)

    def is_audio_track(self, track):
        if track >= len(self._tracks):
            return False
        return bool(getattr(self._tracks[track], 'has_audio_input', False))

    def has_clip(self, track, scene):
        slot = self._slot(track, scene)
        return bool(slot is not None and slot.has_clip)

    def is_playing(self, track, scene):
        slot = self._slot(track, scene)
        return bool(slot is not None and slot.has_clip and slot.clip.is_playing and not slot.clip.is_recording)

    def is_recording(self, track, scene):
        slot = self._slot(track, scene)
        return bool(slot is not None and slot.has_clip and slot.clip.is_recording)
