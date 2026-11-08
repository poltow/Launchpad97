"""Los 8 botones superiores: modificadores, Undo/Redo, Fixed Length,
Snapshot, Pulso/Tap/metronomo, acorde INIT y sus LEDs."""
import time
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework import Task

try:
    from . import consts
    from . import Pulse
    from . import BounceGuard
    from .Colors import SNAPSHOT_CYCLE
except (ImportError, ValueError):
    import consts
    import Pulse
    import BounceGuard
    from Colors import SNAPSHOT_CYCLE


class TopControls(ControlSurfaceComponent):

    def __init__(self, buttons, session, settings, actions, modifiers, tap_tempo):
        super(TopControls, self).__init__(name='Looper_Top', is_root=True)
        self._buttons = list(buttons)
        self._session = session
        self._settings = settings
        self._actions = actions
        self._modifiers = modifiers
        self._tap = tap_tempo
        self._snapshot_index = 0
        self._rainbow_ticks = 0
        self._redo_task = self._tasks.add(Task.sequence(Task.wait(consts.LONG_PRESS), Task.run(self._do_redo)))
        self._redo_task.kill()
        self._metro_task = self._tasks.add(Task.sequence(Task.wait(consts.LONG_PRESS), Task.run(self._do_metronome)))
        self._metro_task.kill()
        self._init_task = self._tasks.add(Task.sequence(Task.wait(consts.INIT_HOLD), Task.run(self._do_init)))
        self._init_task.kill()
        for button in self._buttons:
            button.add_value_listener(self._button_value, identify_sender=True)
        self._register_timer_callback(self._on_tick)
        self._session.add_pulse_listener(self._on_pulse)
        self._session.add_chord_break_listener(self._on_chord_broken)
        self.update()

    def disconnect(self):
        try:
            self._unregister_timer_callback(self._on_tick)
        except Exception:
            pass
        for button in self._buttons:
            button.remove_value_listener(self._button_value)
        for task in (self._redo_task, self._metro_task, self._init_task):
            task.kill()
        self._buttons = []
        super(TopControls, self).disconnect()

    # -- entrada ----------------------------------------------------------

    def _button_value(self, value, sender):
        if not self.is_enabled():
            return
        name = consts.TOP_NAMES[self._buttons.index(sender)]
        if value:
            self._on_press(name)
        else:
            self._on_release(name)
        self._session.update()
        self.update()

    def _on_press(self, name):
        snapshot_was_held = self._modifiers.is_held('snapshot')
        self._session.diag('top press %s' % name)
        self._modifiers.press(name)
        chord = self._modifiers.held_chord()
        if chord is not None:
            self._on_chord(chord, name)
            return
        if name != 'snapshot' and snapshot_was_held:
            # con Snapshot abajo los demas superiores se ignoran (salvo acordes)
            self._modifiers.consume(name)
            return
        if self._session.top_decision(name) == BounceGuard.REJECT:
            self._modifiers.consume(name)
            self._session.flash_reject(self._buttons[consts.TOP_NAMES.index(name)])
            self._session.show('bounce_busy')
            return
        if name == 'snapshot':
            self._session.begin_bounce_select(time.time())
            return
        if name == 'pulse':
            self._metro_task.restart()
            tempo = self._tap.tap(time.time())
            if tempo is not None:
                self._actions.set_tempo(tempo)
                self._session.show('tap_tempo', tempo=self.song().tempo)
            else:
                self._session.show('press_pulse', count=self._tap.count(), needed=consts.TAP_MIN)
        else:
            self._session.show('press_' + name)
        if name == 'undo':
            self._redo_task.restart()

    def _on_chord(self, chord, last_name):
        """Se completo un acorde. Los botones ya quedaron consumidos."""
        self._redo_task.kill()
        self._metro_task.kill()
        self._tap.reset()
        self._session.cancel_bounce_select()
        if not self._session.chord_allowed():
            self._session.flash_reject(self._buttons[consts.TOP_NAMES.index(last_name)])
            self._session.show('bounce_busy')
            return
        if chord == 'init':
            self._init_task.restart()
            self._session.set_init_pending(True)

    def _on_release(self, name):
        chord_was_held = self._modifiers.held_chord()
        event = self._modifiers.release(name)
        self._session.diag('top release %s evento=%s acorde=%s' % (name, event, chord_was_held))
        if name == 'undo':
            self._redo_task.kill()
        elif name == 'pulse':
            self._metro_task.kill()
        elif name == 'copy':
            self._session.clear_copy_origin()
        elif name == 'snapshot':
            if self._session.end_bounce_select(time.time()):
                self._session.flash_reject(self._buttons[consts.TOP_SNAPSHOT])
        if chord_was_held == 'init' and self._modifiers.held_chord() is None:
            self._init_task.kill()
            self._session.set_init_pending(False)
        if event == 'undo':
            self._session.undo()
            self._session.show('undo')
        elif event == 'toggle_fixed_length':
            self._settings.toggle_fixed_length()
            self._session.show('fixed_length', on=self._settings.get('fixed_length_on'),
                               bars=self._settings.get('fixed_length_bars'))

    # -- pulsaciones largas y acorde --------------------------------------

    def _do_redo(self):
        self._modifiers.consume('undo')
        self._session.redo()
        self._session.show('redo')
        self.update()

    def _do_metronome(self):
        self._modifiers.consume('pulse')
        self._tap.reset()
        on = self._actions.toggle_metronome()
        self._session.show('metronome', on=on)
        self.update()

    def _on_chord_broken(self, chord):
        """Un pad o lateral llego con el acorde abajo: no era un acorde."""
        if chord == 'init':
            self._init_task.kill()
            self._session.set_init_pending(False)
        self.update()

    def _do_init(self):
        self._session.init_grid()
        self.update()

    # -- LEDs -------------------------------------------------------------

    def update(self):
        super(TopControls, self).update()
        if not self.is_enabled() or not self._buttons:
            return
        self._update_undo_led()
        self._update_fixed_length_led()
        self._buttons[consts.TOP_QUANTIZE].set_light('Looper.Top.Quantize')
        self._buttons[consts.TOP_DELETE].set_light('Looper.Top.Delete')
        self._buttons[consts.TOP_STOP].set_light('Looper.Top.Stop')
        self._buttons[consts.TOP_COPY].set_light('Looper.Top.Copy')
        self._update_snapshot_led()
        self._update_pulse_led()

    def _update_snapshot_led(self):
        if self._modifiers.is_held('snapshot'):
            if self._session.bounce_marked_count() > 0:
                self._buttons[consts.TOP_SNAPSHOT].set_light('Looper.Top.SnapshotMarked')
            else:
                self._buttons[consts.TOP_SNAPSHOT].set_light('Looper.Top.SnapshotHeld')
        else:
            self._buttons[consts.TOP_SNAPSHOT].set_light(SNAPSHOT_CYCLE[self._snapshot_index])

    def _update_undo_led(self):
        """Verde tenue sin nada que deshacer, verde fuerte si hay Undo,
        verde/lima al pulso si ademas hay Redo. Ambar mientras se mantiene."""
        if self._modifiers.is_held('undo'):
            name = 'Looper.Top.UndoHeld'
        else:
            song = self.song()
            can_undo = bool(getattr(song, 'can_undo', True))
            can_redo = bool(getattr(song, 'can_redo', False))
            if can_undo and can_redo:
                name = 'Looper.Top.Undo' if self._session.blink_on() else 'Looper.Top.UndoRedo'
            elif can_undo:
                name = 'Looper.Top.Undo'
            elif can_redo:
                name = 'Looper.Top.UndoRedo'
            else:
                name = 'Looper.Top.UndoNone'
        self._buttons[consts.TOP_UNDO].set_light(name)

    def _update_fixed_length_led(self):
        """Prendido: naranja parpadeando por hardware del Launchpad (sigue aunque
        el transporte este parado). Apagado: naranja tenue fijo."""
        if self._settings.get('fixed_length_on'):
            name = 'Looper.Top.FixedLengthOn'
        else:
            name = 'Looper.Top.FixedLengthOff'
        self._buttons[consts.TOP_FIXED_LENGTH].set_light(name)

    def _update_pulse_led(self):
        phase = self._session.pulse_phase()
        metro = self.song().metronome
        if self._tap.is_counting(time.time()) and self._modifiers.is_held('pulse'):
            name = 'Looper.Top.PulseStrong'
        elif phase == Pulse.PULSE_OFF:
            name = 'Looper.Top.PulseOff'
        elif phase == Pulse.PULSE_DOWNBEAT:
            name = 'Looper.Top.PulseMetroStrong' if metro else 'Looper.Top.PulseStrong'
        else:
            name = 'Looper.Top.PulseMetroWeak' if metro else 'Looper.Top.PulseWeak'
        self._buttons[consts.TOP_PULSE].set_light(name)

    def _advance_rainbow(self):
        self._snapshot_index = (self._snapshot_index + 1) % len(SNAPSHOT_CYCLE)
        self._update_snapshot_led()

    def _on_pulse(self):
        """Cambio de fase del pulso, avisado por la sesion (fino, al tempo)."""
        if self.is_enabled() and self._buttons:
            self._update_pulse_led()
            self._update_undo_led()

    def _on_tick(self):
        if not self.is_enabled() or not self._buttons:
            return
        self._rainbow_ticks += 1
        if self._rainbow_ticks >= consts.RAINBOW_TICKS:
            self._rainbow_ticks = 0
            self._advance_rainbow()
        self._update_pulse_led()
        self._update_undo_led()
