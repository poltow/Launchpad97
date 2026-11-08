"""ControlSurface de LaunchpadLooper: elementos MIDI y cableado."""
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement

try:
    from . import consts
    from .ConfigurableButtonElement import ConfigurableButtonElement
    from .Colors import make_skin
    from .Settings import Settings
    from .ClipActions import ClipActions
    from .ModifierState import ModifierState
    from .TapTempo import TapTempo
    from .LooperSession import LooperSession
    from .TopControls import TopControls
except (ImportError, ValueError):
    import consts
    from ConfigurableButtonElement import ConfigurableButtonElement
    from Colors import make_skin
    from Settings import Settings
    from ClipActions import ClipActions
    from ModifierState import ModifierState
    from TapTempo import TapTempo
    from LooperSession import LooperSession
    from TopControls import TopControls


class LaunchpadLooper(ControlSurface):

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._suppress_send_midi = True
        self._session = None
        self._top = None
        self._config_button = None
        with self.component_guard():
            self._skin = make_skin()
            self._config_button = ButtonElement(True, MIDI_CC_TYPE, 0, consts.CONFIG_CC, optimized_send_midi=False)
            self._build_controls()
            self._build_components()
            self.set_highlighting_session_component(self._session)
            self.request_rebuild_midi_map()
        self.log_message('LaunchpadLooper loaded (Live %s, diag=%s)' % (self._live_version(), consts.DIAG_LOG))

    def _live_version(self):
        try:
            app = Live.Application.get_application()
            return '%s.%s.%s' % (app.get_major_version(), app.get_minor_version(), app.get_bugfix_version())
        except Exception:
            return '?'

    def _build_controls(self):
        self._matrix = ButtonMatrixElement()
        self._matrix.name = 'Looper_Matrix'
        for row in range(consts.GRID_SIZE):
            buttons = []
            for column in range(consts.GRID_SIZE):
                note = consts.MATRIX_NOTE(row, column)
                button = ConfigurableButtonElement(True, MIDI_NOTE_TYPE, 0, note, skin=self._skin, control_surface=self)
                button.name = 'Pad_%d_%d' % (column, row)
                buttons.append(button)
            self._matrix.add_row(tuple(buttons))
        self._side_buttons = []
        for index in range(consts.GRID_SIZE):
            button = ConfigurableButtonElement(True, MIDI_NOTE_TYPE, 0, consts.SIDE_NOTES[index], skin=self._skin)
            button.name = 'Scene_%d' % index
            self._side_buttons.append(button)
        self._scene_matrix = ButtonMatrixElement()
        self._scene_matrix.name = 'Looper_Scenes'
        self._scene_matrix.add_row(tuple(self._side_buttons))
        self._top_buttons = []
        for index in range(consts.GRID_SIZE):
            button = ConfigurableButtonElement(True, MIDI_CC_TYPE, 0, consts.TOP_CC_BASE + index, skin=self._skin)
            button.name = 'Top_%s' % consts.TOP_NAMES[index]
            self._top_buttons.append(button)

    def _build_components(self):
        self._settings = Settings(log=self.log_message)
        self._actions = ClipActions(self.song(), Live.Song.Quantization.q_no_q, log=self.log_message)
        self._modifiers = ModifierState(consts.MODIFIER_NAMES, consts.CHORDS,
                                        grace=consts.MODIFIER_GRACE,
                                        grace_names=consts.GRACE_MODIFIERS)
        self._tap = TapTempo(window=consts.TAP_WINDOW, min_taps=consts.TAP_MIN,
                             tempo_min=consts.TEMPO_MIN, tempo_max=consts.TEMPO_MAX)
        self._session = LooperSession(self._settings, self._actions, self._modifiers, self)
        self._session.set_clip_launch_buttons(self._matrix)
        self._session.set_scene_launch_buttons(self._scene_matrix)
        self._top = TopControls(self._top_buttons, self._session, self._settings,
                                self._actions, self._modifiers, self._tap)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self.schedule_message(5, self._update_hardware)

    def _update_hardware(self):
        self._suppress_send_midi = False
        if self._config_button is not None:
            # Misma secuencia que Launchpad95 (MainSelectorComponent.update):
            # parpadeo automatico y mapeo X-Y, sin RESET previo (el RESET
            # inmediato antes del flash dejaba el parpadeo apagado) y
            # forzados para que no los filtre el cache de envio.
            self._config_button.send_value(consts.CONFIG_FLASH_AUTO, force=True)
            self._config_button.send_value(consts.CONFIG_LAYOUT_XY, force=True)
        for control in self.controls:
            if isinstance(control, ConfigurableButtonElement):
                control.force_next_send()
        self.set_enabled(True)
        self.update()
        self._session.show('ready')

    def _send_midi(self, midi_bytes, optimized=None):
        if self._suppress_send_midi:
            return False
        return ControlSurface._send_midi(self, midi_bytes, optimized=optimized)

    def disconnect(self):
        """Apaga cada LED de forma explicita antes de que el framework
        desarme los controles, y al final resetea el Launchpad."""
        self._suppress_send_midi = False
        self._blackout()
        self._suppress_send_midi = True
        ControlSurface.disconnect(self)
        self._suppress_send_midi = False
        if self._config_button is not None:
            self._config_button.send_value(consts.CONFIG_FLASH_OFF)
            self._config_button.send_value(consts.CONFIG_RESET)
            self._config_button = None
        self.log_message('LaunchpadLooper disconnected, LEDs off')

    def _blackout(self):
        try:
            for control in self.controls:
                if isinstance(control, ConfigurableButtonElement):
                    control.send_value(consts.LED_OFF, force=True)
        except Exception as error:
            self.log_message('LaunchpadLooper blackout: %s' % error)
