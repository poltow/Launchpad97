# LaunchpadLooper — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el script `LaunchpadLooper` descrito en `docs/specs/2026-10-18-launchpad-looper-design.md`: Launchpad MK1 como controlador de live looping de audio, 8×8 fijo, sin modos.

**Architecture:** Toda la lógica decidible (modificadores, tap tempo, pulso, planificación de snapshot, colores, settings, despacho de gestos) vive en módulos puros sin `import Live` ni `_Framework`, probados con `unittest`. Los módulos que tocan Live (`LooperSession`, `TopControls`, `LaunchpadLooper`, `Colors`, `ConfigurableButtonElement`) son capas delgadas que traducen esas decisiones a llamadas de la API y se verifican con la lista manual del final. `ClipActions` recibe objetos de Live por parámetro (duck typing) y se prueba con fakes.

**Tech Stack:** Python 2.7 (Live 9/10) escrito en el subconjunto compatible con Python 3, `_Framework` de Live 9, `unittest`. Los tests corren localmente con Python 3.11 (`C:\Python311\python.exe`); no hay Python 2 en la máquina, por eso un test verifica que el código no use sintaxis exclusiva de Python 3.

**Sin git:** el proyecto no tiene repositorio y el usuario prohíbe commits automáticos. Los pasos "Commit" del formato estándar se omiten. Al terminar cada tarea, correr la suite completa.

**Comando de tests (desde `C:\MY_GITHUB\Launchpad97-master`):**
```
C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v
```

**Reglas de código (Python 2.7 y 3 a la vez):**
- `super(Clase, self)`, nunca `super()`.
- Sin f-strings, sin anotaciones de tipo, sin `nonlocal`, sin `:=`, sin `print` como sentencia, sin `except X, e`, sin `raise X, msg`.
- `range` en vez de `xrange`; división entera con `//`; `dict.items()`.
- `from __future__ import absolute_import` no es necesario; los módulos propios se importan como `from .Modulo import X` **solo** en los módulos puros y tests. Los módulos que carga Live usan import plano `from Modulo import X` como hace Launchpad95 (Live 9 añade la carpeta del script al path). Para que ambos funcionen, cada módulo Live hace:
  ```python
  try:
      from .ModifierState import ModifierState
  except (ImportError, ValueError):
      from ModifierState import ModifierState
  ```
  Los módulos puros se importan entre sí con el mismo patrón.

---

## Estructura de archivos

| Archivo | Responsabilidad | Tests |
|---|---|---|
| `LaunchpadLooper/__init__.py` | `create_instance`, `get_capabilities` | manual |
| `LaunchpadLooper/consts.py` | constantes: índices de botones, notas MIDI, tiempos, tablas de valores | — |
| `LaunchpadLooper/ModifierState.py` | qué superiores están mantenidos, orden, acorde INIT, consumo de pulsaciones | `tests/test_modifier_state.py` |
| `LaunchpadLooper/TapTempo.py` | marcas de tiempo, ventana, mínimo 4, cálculo | `tests/test_tap_tempo.py` |
| `LaunchpadLooper/Pulse.py` | fase de parpadeo a partir del tiempo musical | `tests/test_pulse.py` |
| `LaunchpadLooper/SnapshotPlanner.py` | fila libre, lista de copias, rechazos | `tests/test_snapshot_planner.py` |
| `LaunchpadLooper/SlotColors.py` | estado de slot → nombre de color de skin; colores de escena y filas de valores | `tests/test_slot_colors.py` |
| `LaunchpadLooper/Dispatch.py` | gesto + modificador activo → acción | `tests/test_dispatch.py` |
| `LaunchpadLooper/Settings.py` | defaults, validación, archivo JSON | `tests/test_settings.py` |
| `LaunchpadLooper/ClipActions.py` | operaciones sobre objetos Live (duck typing) | `tests/test_clip_actions.py` con `tests/fakes.py` |
| `LaunchpadLooper/Colors.py` | `Rgb` MK1 y skin `Looper.*` | manual |
| `LaunchpadLooper/ConfigurableButtonElement.py` | copia de Launchpad95 | manual |
| `LaunchpadLooper/LooperSession.py` | `SessionComponent` 8×8, slots y escenas, LEDs, desarme | manual |
| `LaunchpadLooper/TopControls.py` | 8 superiores, timers, pulso, tap, INIT | manual |
| `LaunchpadLooper/LaunchpadLooper.py` | `ControlSurface`, elementos MIDI, cableado | manual |
| `LaunchpadLooper/tests/test_py2_syntax.py` | rechaza sintaxis solo-Python-3 | sí |
| `install.ps1` | copia la carpeta a Live 9 y Live 10 | manual |
| `docs/manual-checklist-launchpad-looper.md` | lista de verificación en Live | manual |

---

### Task 1: Esqueleto, constantes y guardia de sintaxis

**Files:**
- Create: `LaunchpadLooper/__init__.py`
- Create: `LaunchpadLooper/consts.py`
- Create: `LaunchpadLooper/tests/__init__.py`
- Create: `LaunchpadLooper/tests/test_py2_syntax.py`

- [ ] **Step 1: Crear `LaunchpadLooper/tests/__init__.py` vacío y `LaunchpadLooper/__init__.py` provisional**

`LaunchpadLooper/__init__.py` (se completa en Task 14):
```python
# LaunchpadLooper - control surface for live looping on the Launchpad MK1.
# The real create_instance / get_capabilities are added once the
# ControlSurface exists (see LaunchpadLooper.py).
```

- [ ] **Step 2: Escribir el test de sintaxis**

`LaunchpadLooper/tests/test_py2_syntax.py`:
```python
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.dirname(HERE)

FORBIDDEN = [
    (re.compile(r'(?<![\w.])f"'), 'f-string'),
    (re.compile(r"(?<![\w.])f'"), 'f-string'),
    (re.compile(r'\bnonlocal\b'), 'nonlocal'),
    (re.compile(r':='), 'walrus'),
    (re.compile(r'\bsuper\(\)'), 'super() sin argumentos'),
    (re.compile(r'^\s*print\s+[^(\s]', re.M), 'print como sentencia'),
    (re.compile(r'\bexcept\s+\w+\s*,\s*\w+\s*:'), 'except X, e'),
    (re.compile(r'^\s*async\s+def\b', re.M), 'async def'),
    (re.compile(r'\bxrange\('), 'xrange'),
    (re.compile(r'\.iteritems\('), 'iteritems'),
    (re.compile(r'\bdef\s+\w+\([^)]*\)\s*->'), 'anotacion de retorno'),
]


def _source_files():
    for name in sorted(os.listdir(PACKAGE)):
        if name.endswith('.py'):
            yield os.path.join(PACKAGE, name)


class Py2SyntaxTest(unittest.TestCase):

    def test_no_python3_only_syntax(self):
        problems = []
        for path in _source_files():
            with open(path, 'r') as handle:
                text = handle.read()
            for pattern, label in FORBIDDEN:
                if pattern.search(text):
                    problems.append('%s: %s' % (os.path.basename(path), label))
        self.assertEqual([], problems)

    def test_consts_exist(self):
        from LaunchpadLooper import consts
        self.assertEqual(8, consts.GRID_SIZE)
        self.assertEqual((1, 2, 4, 8, 16), consts.FIXED_LENGTH_BARS)
        self.assertEqual(('1/4', '1/8', '1/8t', '1/16', '1/16t'), consts.QUANTIZE_GRID_NAMES)
        self.assertEqual(('undo', 'fixed_length', 'quantize'), consts.INIT_CHORD)
```

- [ ] **Step 3: Correr el test y verificar que falla**

Run: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v`
Expected: `test_consts_exist` FAIL con `ModuleNotFoundError: No module named 'LaunchpadLooper.consts'`.

- [ ] **Step 4: Escribir `LaunchpadLooper/consts.py`**

```python
"""Constantes de LaunchpadLooper. Sin dependencias de Live."""

GRID_SIZE = 8

# Hardware MK1 (igual que Launchpad95)
MATRIX_NOTE = lambda row, column: row * 16 + column
SIDE_NOTES = (8, 24, 40, 56, 72, 88, 104, 120)
TOP_CC_BASE = 104
CONFIG_CC = 0
CONFIG_RESET = 0
CONFIG_FLASH_AUTO = 40   # 0x28: doble buffer con parpadeo automatico
CONFIG_FLASH_OFF = 32    # 0x20

# Botones superiores, en orden fisico
TOP_UNDO = 0
TOP_FIXED_LENGTH = 1
TOP_QUANTIZE = 2
TOP_DELETE = 3
TOP_STOP = 4
TOP_COPY = 5
TOP_SNAPSHOT = 6
TOP_PULSE = 7
TOP_NAMES = ('undo', 'fixed_length', 'quantize', 'delete', 'stop', 'copy', 'snapshot', 'pulse')

# Superiores que actuan como modificador mientras se mantienen
MODIFIER_NAMES = ('fixed_length', 'quantize', 'delete', 'stop', 'copy')
INIT_CHORD = ('undo', 'fixed_length', 'quantize')

# Tiempos en segundos
LONG_PRESS = 0.5
INIT_HOLD = 0.5
REJECT_FLASH = 0.3
SNAPSHOT_CYCLE = 1.0
TIMER_TICK = 0.1

# Valores
FIXED_LENGTH_BARS = (1, 2, 4, 8, 16)
QUANTIZE_GRID_NAMES = ('1/4', '1/8', '1/8t', '1/16', '1/16t')
QUANTIZE_AMOUNTS = (0.5, 1.0)
QUANTIZE_AMOUNT_LATERALS = (6, 7)   # laterales que muestran 50% y 100%

# Tap tempo
TAP_WINDOW = 2.0
TAP_MIN = 4
TEMPO_MIN = 20.0
TEMPO_MAX = 999.0

SNAP_NAME = 'SNAP'
```

- [ ] **Step 5: Correr los tests y verificar que pasan**

Run: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v`
Expected: 2 tests OK.

---

### Task 2: ModifierState

**Files:**
- Create: `LaunchpadLooper/ModifierState.py`
- Test: `LaunchpadLooper/tests/test_modifier_state.py`

Responsabilidad: saber qué superiores están abajo y en qué orden, cuál es el modificador activo (el primero que bajó), detectar el acorde INIT, y decidir qué pasa al soltar cada botón (undo, toggle de Fixed Length, tap, o nada si la pulsación fue consumida por una pulsación larga o por el acorde).

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_modifier_state.py`:
```python
import unittest

from LaunchpadLooper.ModifierState import ModifierState
from LaunchpadLooper import consts


def make():
    return ModifierState(consts.MODIFIER_NAMES, consts.INIT_CHORD)


class ActiveModifierTest(unittest.TestCase):

    def test_no_modifier_when_nothing_held(self):
        state = make()
        self.assertIsNone(state.active())

    def test_first_pressed_modifier_wins(self):
        state = make()
        state.press('delete')
        state.press('copy')
        self.assertEqual('delete', state.active())
        state.release('delete')
        self.assertEqual('copy', state.active())

    def test_non_modifier_buttons_are_not_active(self):
        state = make()
        state.press('undo')
        state.press('pulse')
        self.assertIsNone(state.active())
        state.press('stop')
        self.assertEqual('stop', state.active())

    def test_is_held(self):
        state = make()
        self.assertFalse(state.is_held('stop'))
        state.press('stop')
        self.assertTrue(state.is_held('stop'))
        state.release('stop')
        self.assertFalse(state.is_held('stop'))


class ReleaseEventsTest(unittest.TestCase):

    def test_short_undo_release_returns_undo(self):
        state = make()
        state.press('undo')
        self.assertEqual('undo', state.release('undo'))

    def test_consumed_undo_release_returns_nothing(self):
        state = make()
        state.press('undo')
        state.consume('undo')
        self.assertIsNone(state.release('undo'))

    def test_release_without_press_returns_nothing(self):
        state = make()
        self.assertIsNone(state.release('undo'))

    def test_fixed_length_release_toggles_when_no_lateral_touched(self):
        state = make()
        state.press('fixed_length')
        self.assertEqual('toggle_fixed_length', state.release('fixed_length'))

    def test_fixed_length_release_does_not_toggle_after_lateral_touch(self):
        state = make()
        state.press('fixed_length')
        state.note_lateral_touch()
        self.assertIsNone(state.release('fixed_length'))

    def test_lateral_touch_is_forgotten_after_release(self):
        state = make()
        state.press('fixed_length')
        state.note_lateral_touch()
        state.release('fixed_length')
        state.press('fixed_length')
        self.assertEqual('toggle_fixed_length', state.release('fixed_length'))

    def test_pulse_short_release_is_tap(self):
        state = make()
        state.press('pulse')
        self.assertEqual('tap', state.release('pulse'))

    def test_pulse_consumed_release_is_not_tap(self):
        state = make()
        state.press('pulse')
        state.consume('pulse')
        self.assertIsNone(state.release('pulse'))

    def test_other_buttons_release_nothing(self):
        state = make()
        for name in ('quantize', 'delete', 'stop', 'copy', 'snapshot'):
            state.press(name)
            self.assertIsNone(state.release(name))


class InitChordTest(unittest.TestCase):

    def test_chord_requires_all_three(self):
        state = make()
        state.press('undo')
        state.press('fixed_length')
        self.assertFalse(state.chord_held())
        state.press('quantize')
        self.assertTrue(state.chord_held())

    def test_chord_consumes_its_buttons(self):
        state = make()
        state.press('undo')
        state.press('fixed_length')
        state.press('quantize')
        state.release('quantize')
        self.assertFalse(state.chord_held())
        self.assertIsNone(state.release('undo'))
        self.assertIsNone(state.release('fixed_length'))

    def test_chord_does_not_consume_other_buttons(self):
        state = make()
        state.press('delete')
        state.press('undo')
        state.press('fixed_length')
        state.press('quantize')
        state.release('delete')
        # delete never had a release action anyway; check it is no longer held
        self.assertFalse(state.is_held('delete'))

    def test_after_chord_released_buttons_work_again(self):
        state = make()
        for name in consts.INIT_CHORD:
            state.press(name)
        for name in consts.INIT_CHORD:
            state.release(name)
        state.press('undo')
        self.assertEqual('undo', state.release('undo'))

    def test_chord_in_any_order(self):
        state = make()
        state.press('quantize')
        state.press('undo')
        state.press('fixed_length')
        self.assertTrue(state.chord_held())


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_modifier_state -v`
Expected: ERROR `No module named 'LaunchpadLooper.ModifierState'`.

- [ ] **Step 3: Escribir `LaunchpadLooper/ModifierState.py`**

```python
"""Estado de los botones superiores. Modulo puro, sin Live."""


class ModifierState(object):
    """Lleva que superiores estan abajo y en que orden, y decide que
    accion corresponde al soltar cada uno.

    press(name)      -> registra el boton abajo
    release(name)    -> 'undo' | 'toggle_fixed_length' | 'tap' | None
    consume(name)    -> la pulsacion ya hizo algo (long press / acorde);
                        al soltar no debe hacer nada mas
    note_lateral_touch() -> se toco un lateral con un modificador abajo
    active()         -> modificador activo (el primero que bajo) o None
    chord_held()     -> True mientras los tres botones del acorde INIT
                        esten abajo
    """

    def __init__(self, modifier_names, chord_names):
        self._modifiers = tuple(modifier_names)
        self._chord = tuple(chord_names)
        self._held = []
        self._consumed = set()
        self._touched = set()

    def press(self, name):
        if name not in self._held:
            self._held.append(name)
        if self.chord_held():
            for chord_name in self._chord:
                self._consumed.add(chord_name)

    def release(self, name):
        was_held = name in self._held
        if was_held:
            self._held.remove(name)
        consumed = name in self._consumed
        touched = name in self._touched
        self._consumed.discard(name)
        self._touched.discard(name)
        if not was_held or consumed:
            return None
        if name == 'undo':
            return 'undo'
        if name == 'fixed_length':
            if touched:
                return None
            return 'toggle_fixed_length'
        if name == 'pulse':
            return 'tap'
        return None

    def consume(self, name):
        self._consumed.add(name)

    def note_lateral_touch(self):
        active = self.active()
        if active is not None:
            self._touched.add(active)

    def is_held(self, name):
        return name in self._held

    def active(self):
        for name in self._held:
            if name in self._modifiers:
                return name
        return None

    def chord_held(self):
        for name in self._chord:
            if name not in self._held:
                return False
        return True
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_modifier_state -v`
Expected: todos OK.

---

### Task 3: TapTempo

**Files:**
- Create: `LaunchpadLooper/TapTempo.py`
- Test: `LaunchpadLooper/tests/test_tap_tempo.py`

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_tap_tempo.py`:
```python
import unittest

from LaunchpadLooper.TapTempo import TapTempo


class TapTempoTest(unittest.TestCase):

    def setUp(self):
        self.tap = TapTempo(window=2.0, min_taps=4, tempo_min=20.0, tempo_max=999.0)

    def test_fewer_than_four_taps_return_none(self):
        self.assertIsNone(self.tap.tap(0.0))
        self.assertIsNone(self.tap.tap(0.5))
        self.assertIsNone(self.tap.tap(1.0))

    def test_fourth_tap_returns_tempo(self):
        for t in (0.0, 0.5, 1.0):
            self.tap.tap(t)
        self.assertAlmostEqual(120.0, self.tap.tap(1.5))

    def test_following_taps_keep_adjusting(self):
        for t in (0.0, 0.5, 1.0, 1.5):
            self.tap.tap(t)
        # un quinto toque mas lento baja el promedio
        tempo = self.tap.tap(2.1)
        self.assertTrue(tempo < 120.0)
        self.assertTrue(tempo > 100.0)

    def test_gap_longer_than_window_resets(self):
        for t in (0.0, 0.5, 1.0):
            self.tap.tap(t)
        self.assertIsNone(self.tap.tap(3.5))   # 2.5 s despues: reinicia
        self.assertIsNone(self.tap.tap(4.0))
        self.assertIsNone(self.tap.tap(4.5))
        self.assertAlmostEqual(120.0, self.tap.tap(5.0))

    def test_slow_tempo_inside_window(self):
        for t in (0.0, 1.5, 3.0):
            self.tap.tap(t)
        self.assertAlmostEqual(40.0, self.tap.tap(4.5))

    def test_tempo_is_clamped(self):
        for t in (0.0, 0.01, 0.02):
            self.tap.tap(t)
        self.assertEqual(999.0, self.tap.tap(0.03))

    def test_reset_clears_count(self):
        for t in (0.0, 0.5, 1.0):
            self.tap.tap(t)
        self.tap.reset()
        self.assertIsNone(self.tap.tap(1.5))

    def test_is_counting(self):
        self.assertFalse(self.tap.is_counting(0.0))
        self.tap.tap(0.0)
        self.assertTrue(self.tap.is_counting(1.0))
        self.assertFalse(self.tap.is_counting(2.5))

    def test_only_last_eight_taps_are_averaged(self):
        for i in range(8):
            self.tap.tap(i * 1.0)           # 60 BPM durante 8 toques
        for i in range(8):
            tempo = self.tap.tap(8.0 + (i + 1) * 0.5)   # luego 120 BPM
        self.assertAlmostEqual(120.0, tempo)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_tap_tempo -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 3: Escribir `LaunchpadLooper/TapTempo.py`**

```python
"""Tap tempo por marcas de tiempo. Modulo puro, sin Live."""

MAX_TAPS = 8


class TapTempo(object):

    def __init__(self, window=2.0, min_taps=4, tempo_min=20.0, tempo_max=999.0):
        self._window = float(window)
        self._min_taps = int(min_taps)
        self._tempo_min = float(tempo_min)
        self._tempo_max = float(tempo_max)
        self._taps = []

    def tap(self, now):
        """Registra un toque en el instante `now` (segundos). Devuelve el
        tempo calculado a partir del cuarto toque consecutivo, o None."""
        if self._taps and now - self._taps[-1] > self._window:
            self._taps = []
        self._taps.append(float(now))
        if len(self._taps) > MAX_TAPS:
            self._taps = self._taps[-MAX_TAPS:]
        if len(self._taps) < self._min_taps:
            return None
        intervals = [b - a for a, b in zip(self._taps[:-1], self._taps[1:])]
        average = sum(intervals) / float(len(intervals))
        if average <= 0.0:
            return None
        tempo = 60.0 / average
        return max(self._tempo_min, min(self._tempo_max, tempo))

    def reset(self):
        self._taps = []

    def is_counting(self, now):
        return bool(self._taps) and now - self._taps[-1] <= self._window
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_tap_tempo -v`
Expected: todos OK.

---

### Task 4: Pulse

**Files:**
- Create: `LaunchpadLooper/Pulse.py`
- Test: `LaunchpadLooper/tests/test_pulse.py`

Live entrega `song.get_current_beats_song_time()` con `bars`, `beats` (1 a numerador), `sub_division` (1 a 4, semicorcheas) y `ticks`. El pulso está "encendido" en la primera mitad de cada negra (sub_division 1 o 2). Con la canción parada, el pulso se considera encendido y sin tiempo fuerte.

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_pulse.py`:
```python
import unittest

from LaunchpadLooper.Pulse import pulse_phase, PULSE_OFF, PULSE_BEAT, PULSE_DOWNBEAT


class BeatTime(object):
    def __init__(self, bars, beats, sub_division, ticks=1):
        self.bars = bars
        self.beats = beats
        self.sub_division = sub_division
        self.ticks = ticks


class PulseTest(unittest.TestCase):

    def test_first_half_of_downbeat_is_downbeat(self):
        self.assertEqual(PULSE_DOWNBEAT, pulse_phase(BeatTime(1, 1, 1), True))
        self.assertEqual(PULSE_DOWNBEAT, pulse_phase(BeatTime(1, 1, 2), True))

    def test_second_half_of_beat_is_off(self):
        self.assertEqual(PULSE_OFF, pulse_phase(BeatTime(1, 1, 3), True))
        self.assertEqual(PULSE_OFF, pulse_phase(BeatTime(1, 2, 4), True))

    def test_first_half_of_other_beats_is_beat(self):
        self.assertEqual(PULSE_BEAT, pulse_phase(BeatTime(1, 2, 1), True))
        self.assertEqual(PULSE_BEAT, pulse_phase(BeatTime(3, 4, 2), True))

    def test_stopped_song_is_steady_beat(self):
        self.assertEqual(PULSE_BEAT, pulse_phase(BeatTime(1, 1, 4), False))

    def test_none_beat_time_is_steady_beat(self):
        self.assertEqual(PULSE_BEAT, pulse_phase(None, True))


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_pulse -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 3: Escribir `LaunchpadLooper/Pulse.py`**

```python
"""Fase del pulso a partir del tiempo musical de Live. Modulo puro."""

PULSE_OFF = 'off'
PULSE_BEAT = 'beat'
PULSE_DOWNBEAT = 'downbeat'


def pulse_phase(beat_time, is_playing):
    """beat_time: objeto con .beats (1..n) y .sub_division (1..4), o None.
    Devuelve PULSE_DOWNBEAT en la primera mitad del primer tiempo del
    compas, PULSE_BEAT en la primera mitad de los demas tiempos y
    PULSE_OFF en la segunda mitad. Parado o sin datos: PULSE_BEAT fijo."""
    if beat_time is None or not is_playing:
        return PULSE_BEAT
    if beat_time.sub_division > 2:
        return PULSE_OFF
    if beat_time.beats == 1:
        return PULSE_DOWNBEAT
    return PULSE_BEAT


def blink_on(phase):
    return phase != PULSE_OFF
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_pulse -v`
Expected: todos OK.

---

### Task 5: SnapshotPlanner

**Files:**
- Create: `LaunchpadLooper/SnapshotPlanner.py`
- Test: `LaunchpadLooper/tests/test_snapshot_planner.py`

El planificador recibe una "grilla" con `num_tracks`, `num_scenes`, `has_clip(t, s)`, `is_playing(t, s)`, `is_recording(t, s)` y devuelve `(fila, motivo_rechazo, copias)`.

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_snapshot_planner.py`:
```python
import unittest

from LaunchpadLooper.SnapshotPlanner import plan_snapshot, find_free_row, REJECT_RECORDING, REJECT_NO_ROW


class Grid(object):
    """'c' clip detenido, 'p' sonando, 'r' grabando, '.' vacio.
    rows[s][t]."""

    def __init__(self, rows):
        self.rows = rows
        self.num_scenes = len(rows)
        self.num_tracks = len(rows[0])

    def has_clip(self, t, s):
        return self.rows[s][t] != '.'

    def is_playing(self, t, s):
        return self.rows[s][t] == 'p'

    def is_recording(self, t, s):
        return self.rows[s][t] == 'r'


EMPTY = ['........'] * 8


class FindFreeRowTest(unittest.TestCase):

    def test_all_empty_returns_last_row(self):
        self.assertEqual(7, find_free_row(Grid(EMPTY)))

    def test_skips_rows_with_any_clip(self):
        rows = list(EMPTY)
        rows[7] = '.......c'
        rows[6] = 'c.......'
        self.assertEqual(5, find_free_row(Grid(rows)))

    def test_no_free_row(self):
        rows = ['c.......'] * 8
        self.assertIsNone(find_free_row(Grid(rows)))


class PlanSnapshotTest(unittest.TestCase):

    def test_copies_only_playing_clips(self):
        rows = list(EMPTY)
        rows[0] = 'p.c.p...'
        rows[1] = '...p....'
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertEqual(7, row)
        self.assertIsNone(reason)
        self.assertEqual([(0, 0), (3, 1), (4, 0)], sorted(copies))

    def test_rejects_when_any_track_is_recording(self):
        rows = list(EMPTY)
        rows[0] = 'p.r.....'
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertIsNone(row)
        self.assertEqual(REJECT_RECORDING, reason)
        self.assertEqual([], copies)

    def test_rejects_when_no_free_row(self):
        rows = ['p.......'] * 8
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertIsNone(row)
        self.assertEqual(REJECT_NO_ROW, reason)

    def test_nothing_playing_still_makes_empty_snapshot(self):
        rows = list(EMPTY)
        rows[0] = 'c.c.....'
        row, reason, copies = plan_snapshot(Grid(rows))
        self.assertEqual(7, row)
        self.assertIsNone(reason)
        self.assertEqual([], copies)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_snapshot_planner -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 3: Escribir `LaunchpadLooper/SnapshotPlanner.py`**

```python
"""Planificacion de un snapshot sobre la grilla 8x8. Modulo puro."""

REJECT_RECORDING = 'recording'
REJECT_NO_ROW = 'no_free_row'


def find_free_row(grid):
    """Primera fila, buscando desde la ultima hacia la primera, con
    todos sus slots vacios. None si no hay."""
    for row in range(grid.num_scenes - 1, -1, -1):
        free = True
        for track in range(grid.num_tracks):
            if grid.has_clip(track, row):
                free = False
                break
        if free:
            return row
    return None


def plan_snapshot(grid):
    """Devuelve (fila_destino, motivo_rechazo, copias).
    copias es una lista de (track, fila_origen) con los clips sonando."""
    for track in range(grid.num_tracks):
        for scene in range(grid.num_scenes):
            if grid.is_recording(track, scene):
                return (None, REJECT_RECORDING, [])
    row = find_free_row(grid)
    if row is None:
        return (None, REJECT_NO_ROW, [])
    copies = []
    for track in range(grid.num_tracks):
        for scene in range(grid.num_scenes):
            if grid.is_playing(track, scene):
                copies.append((track, scene))
    return (row, None, copies)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_snapshot_planner -v`
Expected: todos OK.

---

### Task 6: SlotColors

**Files:**
- Create: `LaunchpadLooper/SlotColors.py`
- Test: `LaunchpadLooper/tests/test_slot_colors.py`

Traduce estado de slot/escena + modificador + fase de pulso a nombres de color de la skin (`Looper.Slot.*`, `Looper.Scene.*`, `Looper.Value.*`). Los nombres se definen en Task 10.

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_slot_colors.py`:
```python
import unittest

from LaunchpadLooper import SlotColors as C


class SlotStateTest(unittest.TestCase):

    def state(self, **kw):
        args = dict(has_clip=False, is_triggered=False, will_record=False,
                    is_playing=False, is_recording=False, stop_pending=False)
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

    def test_delete_modifier_shows_every_clip_red(self):
        for state in (C.STOPPED, C.PLAYING, C.RECORDING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            self.assertEqual('Looper.Slot.Delete', C.slot_color(state, 'delete', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.EMPTY, 'delete', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.TRIGGERED_RECORD, 'delete', True))

    def test_stop_modifier_shows_only_sounding_slots(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, 'stop', True))
        self.assertEqual('Looper.Slot.Recording', C.slot_color(C.RECORDING, 'stop', True))
        self.assertEqual('Looper.Slot.StopPending', C.slot_color(C.STOP_PENDING_PLAYING, 'stop', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.STOPPED, 'stop', True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.TRIGGERED_PLAY, 'stop', True))

    def test_copy_origin_blinks(self):
        self.assertEqual('Looper.Slot.CopyOrigin', C.slot_color(C.STOPPED, 'copy', True, is_copy_origin=True))
        self.assertEqual('Looper.Slot.Empty', C.slot_color(C.STOPPED, 'copy', False, is_copy_origin=True))
        self.assertEqual('Looper.Slot.Stopped', C.slot_color(C.STOPPED, 'copy', False))

    def test_init_pending_overrides_everything(self):
        self.assertEqual('Looper.Slot.InitPending', C.slot_color(C.PLAYING, 'delete', True, init_pending=True))
        self.assertEqual('Looper.Slot.InitPending', C.slot_color(C.EMPTY, None, False, init_pending=True))

    def test_quantize_and_fixed_length_modifiers_keep_normal_colors(self):
        self.assertEqual('Looper.Slot.Playing', C.slot_color(C.PLAYING, 'quantize', True))
        self.assertEqual('Looper.Slot.Stopped', C.slot_color(C.STOPPED, 'fixed_length', True))


class SceneColorTest(unittest.TestCase):

    def color(self, **kw):
        args = dict(has_playing=False, is_snap=False, has_clips=False,
                    is_triggered=False, modifier=None, blink_on=True)
        args.update(kw)
        return C.scene_color(**args)

    def test_plain_states(self):
        self.assertEqual('Looper.Scene.Off', self.color())
        self.assertEqual('Looper.Scene.Off', self.color(has_clips=True))
        self.assertEqual('Looper.Scene.Snap', self.color(is_snap=True, has_clips=True))
        self.assertEqual('Looper.Scene.Playing', self.color(has_playing=True, has_clips=True))
        self.assertEqual('Looper.Scene.Playing', self.color(has_playing=True, is_snap=True, has_clips=True))

    def test_triggered_blinks(self):
        self.assertEqual('Looper.Scene.Playing', self.color(is_triggered=True, has_clips=True, blink_on=True))
        self.assertEqual('Looper.Scene.Off', self.color(is_triggered=True, has_clips=True, blink_on=False))

    def test_delete_modifier(self):
        self.assertEqual('Looper.Scene.Delete', self.color(has_clips=True, modifier='delete'))
        self.assertEqual('Looper.Scene.Off', self.color(modifier='delete'))

    def test_stop_modifier(self):
        self.assertEqual('Looper.Scene.Playing', self.color(has_playing=True, has_clips=True, modifier='stop'))
        self.assertEqual('Looper.Scene.Off', self.color(is_snap=True, has_clips=True, modifier='stop'))

    def test_copy_modifier_is_like_none(self):
        self.assertEqual('Looper.Scene.Snap', self.color(is_snap=True, has_clips=True, modifier='copy'))


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
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_slot_colors -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 3: Escribir `LaunchpadLooper/SlotColors.py`**

```python
"""Estado -> nombre de color de la skin. Modulo puro."""

EMPTY = 'empty'
STOPPED = 'stopped'
PLAYING = 'playing'
RECORDING = 'recording'
TRIGGERED_PLAY = 'triggered_play'
TRIGGERED_RECORD = 'triggered_record'
STOP_PENDING_PLAYING = 'stop_pending_playing'
STOP_PENDING_RECORDING = 'stop_pending_recording'

SOUNDING = (PLAYING, RECORDING, STOP_PENDING_PLAYING, STOP_PENDING_RECORDING)
WITH_CLIP = (STOPPED, PLAYING, RECORDING, TRIGGERED_PLAY,
             STOP_PENDING_PLAYING, STOP_PENDING_RECORDING)

NUM_FIXED_LENGTH_VALUES = 5
NUM_QUANTIZE_GRIDS = 5
QUANTIZE_AMOUNT_POSITIONS = (6, 7)


def slot_state(has_clip, is_triggered, will_record, is_playing, is_recording, stop_pending):
    if stop_pending and is_recording:
        return STOP_PENDING_RECORDING
    if stop_pending and is_playing:
        return STOP_PENDING_PLAYING
    if is_triggered:
        if will_record:
            return TRIGGERED_RECORD
        return TRIGGERED_PLAY
    if is_recording:
        return RECORDING
    if is_playing:
        return PLAYING
    if has_clip:
        return STOPPED
    return EMPTY


def slot_color(state, modifier, blink_on, is_copy_origin=False, init_pending=False):
    if init_pending:
        return 'Looper.Slot.InitPending'
    if modifier == 'delete':
        if state in WITH_CLIP:
            return 'Looper.Slot.Delete'
        return 'Looper.Slot.Empty'
    if modifier == 'stop':
        if state not in SOUNDING:
            return 'Looper.Slot.Empty'
    if modifier == 'copy' and is_copy_origin:
        if blink_on:
            return 'Looper.Slot.CopyOrigin'
        return 'Looper.Slot.Empty'
    if state == EMPTY:
        return 'Looper.Slot.Empty'
    if state == STOPPED:
        return 'Looper.Slot.Stopped'
    if state == PLAYING:
        return 'Looper.Slot.Playing'
    if state == RECORDING:
        return 'Looper.Slot.Recording'
    if state == TRIGGERED_PLAY:
        return 'Looper.Slot.Playing' if blink_on else 'Looper.Slot.Empty'
    if state == TRIGGERED_RECORD:
        return 'Looper.Slot.Recording' if blink_on else 'Looper.Slot.Empty'
    if state == STOP_PENDING_PLAYING:
        return 'Looper.Slot.StopPending' if blink_on else 'Looper.Slot.Playing'
    if state == STOP_PENDING_RECORDING:
        return 'Looper.Slot.StopPending' if blink_on else 'Looper.Slot.Recording'
    return 'Looper.Slot.Empty'


def scene_color(has_playing, is_snap, has_clips, is_triggered, modifier, blink_on):
    if modifier == 'delete':
        return 'Looper.Scene.Delete' if has_clips else 'Looper.Scene.Off'
    if modifier == 'stop':
        return 'Looper.Scene.Playing' if has_playing else 'Looper.Scene.Off'
    if is_triggered:
        return 'Looper.Scene.Playing' if blink_on else 'Looper.Scene.Off'
    if has_playing:
        return 'Looper.Scene.Playing'
    if is_snap and has_clips:
        return 'Looper.Scene.Snap'
    return 'Looper.Scene.Off'


def fixed_length_row(selected_index):
    row = []
    for index in range(8):
        if index >= NUM_FIXED_LENGTH_VALUES:
            row.append('Looper.Value.Off')
        elif index == selected_index:
            row.append('Looper.Value.Selected')
        else:
            row.append('Looper.Value.Idle')
    return row


def quantize_row(grid_index, amount_index):
    row = []
    for index in range(8):
        if index < NUM_QUANTIZE_GRIDS:
            row.append('Looper.Value.Selected' if index == grid_index else 'Looper.Value.Idle')
        elif index in QUANTIZE_AMOUNT_POSITIONS:
            position = QUANTIZE_AMOUNT_POSITIONS.index(index)
            row.append('Looper.Value.Selected' if position == amount_index else 'Looper.Value.Idle')
        else:
            row.append('Looper.Value.Off')
    return row
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_slot_colors -v`
Expected: todos OK.

---

### Task 7: Dispatch

**Files:**
- Create: `LaunchpadLooper/Dispatch.py`
- Test: `LaunchpadLooper/tests/test_dispatch.py`

Dado el modificador activo y el estado del slot o el índice del lateral, decide la acción. `LooperSession` solo ejecuta.

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_dispatch.py`:
```python
import unittest

from LaunchpadLooper import Dispatch as D
from LaunchpadLooper import SlotColors as C


class PadActionTest(unittest.TestCase):

    def test_no_modifier(self):
        self.assertEqual(D.RECORD, D.pad_action(None, C.EMPTY, False))
        self.assertEqual(D.LAUNCH, D.pad_action(None, C.STOPPED, False))
        self.assertEqual(D.STOP_IMMEDIATE, D.pad_action(None, C.PLAYING, False))
        self.assertEqual(D.STOP_IMMEDIATE, D.pad_action(None, C.STOP_PENDING_PLAYING, False))
        self.assertEqual(D.CLOSE_RECORDING, D.pad_action(None, C.RECORDING, False))
        self.assertEqual(D.CLOSE_RECORDING, D.pad_action(None, C.STOP_PENDING_RECORDING, False))
        self.assertEqual(D.LAUNCH, D.pad_action(None, C.TRIGGERED_PLAY, False))
        self.assertEqual(D.NONE, D.pad_action(None, C.TRIGGERED_RECORD, False))

    def test_delete(self):
        self.assertEqual(D.DELETE_CLIP, D.pad_action('delete', C.STOPPED, False))
        self.assertEqual(D.DELETE_CLIP, D.pad_action('delete', C.RECORDING, False))
        self.assertEqual(D.NONE, D.pad_action('delete', C.EMPTY, False))

    def test_copy(self):
        self.assertEqual(D.COPY_SET_ORIGIN, D.pad_action('copy', C.STOPPED, False))
        self.assertEqual(D.COPY_SET_ORIGIN, D.pad_action('copy', C.PLAYING, True))
        self.assertEqual(D.COPY_PASTE, D.pad_action('copy', C.EMPTY, True))
        self.assertEqual(D.NONE, D.pad_action('copy', C.EMPTY, False))
        self.assertEqual(D.NONE, D.pad_action('copy', C.RECORDING, False))

    def test_quantize(self):
        self.assertEqual(D.QUANTIZE_CLIP, D.pad_action('quantize', C.STOPPED, False))
        self.assertEqual(D.QUANTIZE_CLIP, D.pad_action('quantize', C.PLAYING, False))
        self.assertEqual(D.NONE, D.pad_action('quantize', C.EMPTY, False))
        self.assertEqual(D.NONE, D.pad_action('quantize', C.RECORDING, False))

    def test_stop(self):
        for state in (C.EMPTY, C.STOPPED, C.PLAYING, C.RECORDING):
            self.assertEqual(D.STOP_TRACK, D.pad_action('stop', state, False))

    def test_fixed_length_held_behaves_like_no_modifier(self):
        self.assertEqual(D.RECORD, D.pad_action('fixed_length', C.EMPTY, False))
        self.assertEqual(D.STOP_IMMEDIATE, D.pad_action('fixed_length', C.PLAYING, False))


class LateralActionTest(unittest.TestCase):

    def test_no_modifier_fires_scene(self):
        self.assertEqual((D.FIRE_SCENE, 3), D.lateral_action(None, 3))

    def test_fixed_length_values(self):
        self.assertEqual((D.SET_FIXED_LENGTH, 0), D.lateral_action('fixed_length', 0))
        self.assertEqual((D.SET_FIXED_LENGTH, 4), D.lateral_action('fixed_length', 4))
        self.assertEqual((D.NONE, 5), D.lateral_action('fixed_length', 5))
        self.assertEqual((D.NONE, 7), D.lateral_action('fixed_length', 7))

    def test_quantize_values(self):
        self.assertEqual((D.SET_QUANTIZE_GRID, 0), D.lateral_action('quantize', 0))
        self.assertEqual((D.SET_QUANTIZE_GRID, 4), D.lateral_action('quantize', 4))
        self.assertEqual((D.NONE, 5), D.lateral_action('quantize', 5))
        self.assertEqual((D.SET_QUANTIZE_AMOUNT, 0), D.lateral_action('quantize', 6))
        self.assertEqual((D.SET_QUANTIZE_AMOUNT, 1), D.lateral_action('quantize', 7))

    def test_delete_row(self):
        self.assertEqual((D.DELETE_ROW, 2), D.lateral_action('delete', 2))

    def test_stop_row(self):
        self.assertEqual((D.STOP_ROW, 6), D.lateral_action('stop', 6))

    def test_copy_does_nothing(self):
        self.assertEqual((D.NONE, 1), D.lateral_action('copy', 1))


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_dispatch -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 3: Escribir `LaunchpadLooper/Dispatch.py`**

```python
"""Gesto + modificador activo -> accion. Modulo puro."""

try:
    from . import SlotColors as C
except (ImportError, ValueError):
    import SlotColors as C

NONE = 'none'
RECORD = 'record'
LAUNCH = 'launch'
STOP_IMMEDIATE = 'stop_immediate'
CLOSE_RECORDING = 'close_recording'
DELETE_CLIP = 'delete_clip'
COPY_SET_ORIGIN = 'copy_set_origin'
COPY_PASTE = 'copy_paste'
QUANTIZE_CLIP = 'quantize_clip'
STOP_TRACK = 'stop_track'

FIRE_SCENE = 'fire_scene'
SET_FIXED_LENGTH = 'set_fixed_length'
SET_QUANTIZE_GRID = 'set_quantize_grid'
SET_QUANTIZE_AMOUNT = 'set_quantize_amount'
DELETE_ROW = 'delete_row'
STOP_ROW = 'stop_row'

NUM_FIXED_LENGTH_VALUES = 5
NUM_QUANTIZE_GRIDS = 5
QUANTIZE_AMOUNT_POSITIONS = (6, 7)


def pad_action(modifier, state, has_copy_origin):
    """Accion al bajar un pad. `state` es uno de los estados de SlotColors."""
    if modifier == 'delete':
        return DELETE_CLIP if state in C.WITH_CLIP else NONE
    if modifier == 'copy':
        if state in (C.STOPPED, C.PLAYING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            return COPY_SET_ORIGIN
        if state == C.EMPTY and has_copy_origin:
            return COPY_PASTE
        return NONE
    if modifier == 'quantize':
        if state in (C.STOPPED, C.PLAYING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            return QUANTIZE_CLIP
        return NONE
    if modifier == 'stop':
        return STOP_TRACK
    # sin modificador, o Fixed Length mantenido
    if state == C.EMPTY:
        return RECORD
    if state in (C.RECORDING, C.STOP_PENDING_RECORDING):
        return CLOSE_RECORDING
    if state in (C.PLAYING, C.STOP_PENDING_PLAYING):
        return STOP_IMMEDIATE
    if state in (C.STOPPED, C.TRIGGERED_PLAY):
        return LAUNCH
    return NONE


def lateral_action(modifier, index):
    """Accion al bajar el lateral `index` (0..7). Devuelve (accion, valor)."""
    if modifier == 'fixed_length':
        if index < NUM_FIXED_LENGTH_VALUES:
            return (SET_FIXED_LENGTH, index)
        return (NONE, index)
    if modifier == 'quantize':
        if index < NUM_QUANTIZE_GRIDS:
            return (SET_QUANTIZE_GRID, index)
        if index in QUANTIZE_AMOUNT_POSITIONS:
            return (SET_QUANTIZE_AMOUNT, QUANTIZE_AMOUNT_POSITIONS.index(index))
        return (NONE, index)
    if modifier == 'delete':
        return (DELETE_ROW, index)
    if modifier == 'stop':
        return (STOP_ROW, index)
    if modifier == 'copy':
        return (NONE, index)
    return (FIRE_SCENE, index)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_dispatch -v`
Expected: todos OK.

---

### Task 8: Settings

**Files:**
- Create: `LaunchpadLooper/Settings.py`
- Test: `LaunchpadLooper/tests/test_settings.py`

Persistencia en JSON en la carpeta de usuario. Valores inválidos en el archivo caen al default. Si el archivo no se puede escribir, se registra con `log` y se sigue en memoria.

- [ ] **Step 1: Escribir los tests**

`LaunchpadLooper/tests/test_settings.py`:
```python
import json
import os
import shutil
import tempfile
import unittest

from LaunchpadLooper.Settings import Settings, DEFAULTS


class SettingsTest(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, 'looper.json')
        self.logged = []

    def tearDown(self):
        shutil.rmtree(self.dir)

    def make(self):
        return Settings(self.path, log=self.logged.append)

    def test_defaults_when_file_missing(self):
        s = self.make()
        self.assertEqual(False, s.get('fixed_length_on'))
        self.assertEqual(4, s.get('fixed_length_bars'))
        self.assertEqual('1/16', s.get('quantize_grid'))
        self.assertEqual(1.0, s.get('quantize_amount'))

    def test_set_persists_and_reloads(self):
        s = self.make()
        s.set('fixed_length_on', True)
        s.set('fixed_length_bars', 8)
        s.set('quantize_grid', '1/8t')
        s.set('quantize_amount', 0.5)
        again = self.make()
        self.assertEqual(True, again.get('fixed_length_on'))
        self.assertEqual(8, again.get('fixed_length_bars'))
        self.assertEqual('1/8t', again.get('quantize_grid'))
        self.assertEqual(0.5, again.get('quantize_amount'))

    def test_invalid_values_in_file_fall_back_to_defaults(self):
        with open(self.path, 'w') as handle:
            json.dump({'fixed_length_bars': 3, 'quantize_grid': '1/32',
                       'quantize_amount': 0.75, 'fixed_length_on': 'yes'}, handle)
        s = self.make()
        self.assertEqual(DEFAULTS['fixed_length_bars'], s.get('fixed_length_bars'))
        self.assertEqual(DEFAULTS['quantize_grid'], s.get('quantize_grid'))
        self.assertEqual(DEFAULTS['quantize_amount'], s.get('quantize_amount'))
        self.assertEqual(DEFAULTS['fixed_length_on'], s.get('fixed_length_on'))

    def test_corrupt_file_falls_back_and_logs(self):
        with open(self.path, 'w') as handle:
            handle.write('{not json')
        s = self.make()
        self.assertEqual(4, s.get('fixed_length_bars'))
        self.assertTrue(len(self.logged) > 0)

    def test_set_rejects_invalid_value(self):
        s = self.make()
        self.assertFalse(s.set('fixed_length_bars', 3))
        self.assertEqual(4, s.get('fixed_length_bars'))
        self.assertFalse(s.set('unknown_key', 1))

    def test_index_helpers(self):
        s = self.make()
        s.set('fixed_length_bars', 16)
        self.assertEqual(4, s.fixed_length_index())
        s.set('quantize_grid', '1/4')
        self.assertEqual(0, s.quantize_grid_index())
        s.set('quantize_amount', 0.5)
        self.assertEqual(0, s.quantize_amount_index())

    def test_set_by_index(self):
        s = self.make()
        s.set_fixed_length_index(1)
        self.assertEqual(2, s.get('fixed_length_bars'))
        s.set_quantize_grid_index(2)
        self.assertEqual('1/8t', s.get('quantize_grid'))
        s.set_quantize_amount_index(0)
        self.assertEqual(0.5, s.get('quantize_amount'))

    def test_toggle_fixed_length(self):
        s = self.make()
        self.assertTrue(s.toggle_fixed_length())
        self.assertTrue(s.get('fixed_length_on'))
        self.assertFalse(s.toggle_fixed_length())

    def test_unwritable_path_logs_and_keeps_value(self):
        s = Settings(os.path.join(self.dir, 'no', 'such', 'dir', 'x.json'), log=self.logged.append)
        self.assertTrue(s.set('fixed_length_bars', 2))
        self.assertEqual(2, s.get('fixed_length_bars'))
        self.assertTrue(len(self.logged) > 0)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_settings -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 3: Escribir `LaunchpadLooper/Settings.py`**

```python
"""Ajustes persistentes en un archivo JSON. Modulo puro."""
import json
import os

try:
    from . import consts
except (ImportError, ValueError):
    import consts

DEFAULTS = {
    'fixed_length_on': False,
    'fixed_length_bars': 4,
    'quantize_grid': '1/16',
    'quantize_amount': 1.0,
}

VALID = {
    'fixed_length_on': (True, False),
    'fixed_length_bars': consts.FIXED_LENGTH_BARS,
    'quantize_grid': consts.QUANTIZE_GRID_NAMES,
    'quantize_amount': consts.QUANTIZE_AMOUNTS,
}


def default_path():
    return os.path.join(os.path.expanduser('~'), '.launchpad_looper.json')


def _is_valid(key, value):
    if key not in VALID:
        return False
    allowed = VALID[key]
    if key == 'fixed_length_on':
        return value is True or value is False
    for candidate in allowed:
        if value == candidate and type(value) == type(candidate):
            return True
    return False


class Settings(object):

    def __init__(self, path=None, log=None):
        self._path = path or default_path()
        self._log = log or (lambda message: None)
        self._values = dict(DEFAULTS)
        self._load()

    def _load(self):
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, 'r') as handle:
                data = json.load(handle)
        except Exception as error:
            self._log('LaunchpadLooper settings: no se pudo leer %s (%s)' % (self._path, error))
            return
        if not isinstance(data, dict):
            self._log('LaunchpadLooper settings: contenido invalido en %s' % self._path)
            return
        for key in DEFAULTS:
            if key in data and _is_valid(key, data[key]):
                self._values[key] = data[key]

    def _save(self):
        try:
            with open(self._path, 'w') as handle:
                json.dump(self._values, handle, indent=2, sort_keys=True)
        except Exception as error:
            self._log('LaunchpadLooper settings: no se pudo escribir %s (%s)' % (self._path, error))

    def get(self, key):
        return self._values[key]

    def set(self, key, value):
        if not _is_valid(key, value):
            return False
        self._values[key] = value
        self._save()
        return True

    def toggle_fixed_length(self):
        self.set('fixed_length_on', not self._values['fixed_length_on'])
        return self._values['fixed_length_on']

    def fixed_length_index(self):
        return list(consts.FIXED_LENGTH_BARS).index(self._values['fixed_length_bars'])

    def quantize_grid_index(self):
        return list(consts.QUANTIZE_GRID_NAMES).index(self._values['quantize_grid'])

    def quantize_amount_index(self):
        return list(consts.QUANTIZE_AMOUNTS).index(self._values['quantize_amount'])

    def set_fixed_length_index(self, index):
        return self.set('fixed_length_bars', consts.FIXED_LENGTH_BARS[index])

    def set_quantize_grid_index(self, index):
        return self.set('quantize_grid', consts.QUANTIZE_GRID_NAMES[index])

    def set_quantize_amount_index(self, index):
        return self.set('quantize_amount', consts.QUANTIZE_AMOUNTS[index])
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_settings -v`
Expected: todos OK.

---

### Task 9: ClipActions con fakes de Live

**Files:**
- Create: `LaunchpadLooper/tests/fakes.py`
- Create: `LaunchpadLooper/ClipActions.py`
- Test: `LaunchpadLooper/tests/test_clip_actions.py`

`ClipActions` recibe `song` y la constante `no_quantization` (en Live, `Live.Song.Quantization.q_no_q`) y opera sobre slots, pistas y escenas por duck typing. Cada operación compuesta va en un paso de Undo y captura `RuntimeError` registrando con `log`.

- [ ] **Step 1: Escribir los fakes**

`LaunchpadLooper/tests/fakes.py`:
```python
"""Dobles minimos de la API de Live para los tests de ClipActions."""


class FakeClip(object):
    def __init__(self, is_playing=False, is_recording=False):
        self.is_playing = is_playing
        self.is_recording = is_recording
        self.is_triggered = False
        self.quantize_calls = []

    def quantize(self, grid, amount):
        self.quantize_calls.append((grid, amount))


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


class FakeTrack(object):
    def __init__(self, name='t', can_be_armed=True):
        self.name = name
        self.can_be_armed = can_be_armed
        self.arm = False
        self.playing_slot_index = -1
        self.fired_slot_index = -1
        self.stop_all_calls = 0
        self.clip_slots = []

    def stop_all_clips(self):
        self.stop_all_calls += 1


class FakeScene(object):
    def __init__(self, name=''):
        self.name = name
        self.fire_calls = 0
        self.is_triggered = False
        self.clip_slots = []

    def fire(self):
        self.fire_calls += 1


class FakeSong(object):
    def __init__(self, num_tracks=8, num_scenes=8):
        self.clip_trigger_quantization = 'q_bar'
        self.quantization_history = []
        self.undo_begin = 0
        self.undo_end = 0
        self.tempo = 120.0
        self.metronome = False
        self.signature_numerator = 4
        self.signature_denominator = 4
        self.tracks = [FakeTrack('t%d' % i) for i in range(num_tracks)]
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

    def slot(self, track, scene):
        return self.scenes[scene].clip_slots[track]
```

- [ ] **Step 2: Escribir los tests**

`LaunchpadLooper/tests/test_clip_actions.py`:
```python
import unittest

from LaunchpadLooper.ClipActions import ClipActions
from LaunchpadLooper.tests.fakes import FakeSong, FakeClip

NO_Q = 'q_no_q'


class ClipActionsTest(unittest.TestCase):

    def setUp(self):
        self.song = FakeSong()
        self.logged = []
        self.actions = ClipActions(self.song, NO_Q, log=self.logged.append)

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
        self.assertEqual(1, len(self.logged))

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
        self.assertEqual(1, len(self.logged))

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


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 3: Correr y verificar que falla**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_clip_actions -v`
Expected: ERROR por módulo inexistente.

- [ ] **Step 4: Escribir `LaunchpadLooper/ClipActions.py`**

```python
"""Operaciones sobre objetos de Live por duck typing. Sin import Live:
las constantes de cuantizacion llegan por parametro."""

try:
    from . import consts
except (ImportError, ValueError):
    import consts


class ClipActions(object):

    def __init__(self, song, no_quantization, log=None):
        self._song = song
        self._no_q = no_quantization
        self._log = log or (lambda message: None)

    # -- helpers ----------------------------------------------------------

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
        song.clip_trigger_quantization = self._no_q
        try:
            self._guard('stop_immediately', slot.stop)
        finally:
            song.clip_trigger_quantization = saved

    def record(self, slot, fixed_length_bars):
        """Arma la pista del slot (sin tocar otras) y dispara la grabacion.
        Devuelve True si la pista fue armada por esta llamada."""
        track = slot.canonical_parent
        if not track.can_be_armed:
            return False
        armed_by_us = False
        if not track.arm:
            track.arm = True
            armed_by_us = True
        if fixed_length_bars:
            length = self.record_length_beats(fixed_length_bars)
            quant = self._song.clip_trigger_quantization
            self._guard('record', lambda: slot.fire(record_length=length, launch_quantization=quant))
        else:
            self._guard('record', slot.fire)
        return armed_by_us

    def launch(self, slot):
        self._guard('launch', slot.fire)

    def close_recording(self, slot):
        self._guard('close_recording', slot.fire)

    def delete_clip(self, slot):
        if not slot.has_clip:
            return False
        return self._guard('delete_clip', lambda: (slot.delete_clip(), True)[1])

    def copy_clip(self, source, target):
        if not source.has_clip or target.has_clip:
            return False
        return self._guard('copy_clip', lambda: (source.duplicate_clip_to(target), True)[1])

    def quantize_clip(self, slot, grid, amount):
        if not slot.has_clip:
            return False
        return self._guard('quantize_clip', lambda: (slot.clip.quantize(grid, amount), True)[1])

    # -- pistas y filas ---------------------------------------------------

    def stop_track(self, track):
        self._guard('stop_track', track.stop_all_clips)

    def stop_row(self, tracks, row):
        for track in tracks:
            if track.playing_slot_index == row:
                self.stop_track(track)

    def delete_row(self, scene, snap_name):
        def work():
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
            for scene in scenes:
                for slot in list(scene.clip_slots)[:num_tracks]:
                    if slot.has_clip:
                        self._guard('init_grid', slot.delete_clip)
                if scene.name == snap_name:
                    scene.name = ''
            return True
        return self._undo_step(work)

    # -- globales ---------------------------------------------------------

    def undo(self):
        if getattr(self._song, 'can_undo', True):
            self._guard('undo', self._song.undo)

    def redo(self):
        if getattr(self._song, 'can_redo', True):
            self._guard('redo', self._song.redo)

    def set_tempo(self, tempo):
        self._song.tempo = max(consts.TEMPO_MIN, min(consts.TEMPO_MAX, float(tempo)))

    def toggle_metronome(self):
        self._song.metronome = not self._song.metronome
        return self._song.metronome
```

- [ ] **Step 5: Correr y verificar que pasa**

Run: `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_clip_actions -v`
Expected: todos OK. Luego correr la suite completa y verificar que `test_py2_syntax` sigue OK.

---

### Task 10: Colors y ConfigurableButtonElement (Live)

**Files:**
- Create: `LaunchpadLooper/Colors.py`
- Create: `LaunchpadLooper/ConfigurableButtonElement.py`

Sin tests unitarios (importan `_Framework`). El test de sintaxis los cubre.

- [ ] **Step 1: Copiar `ConfigurableButtonElement.py`**

Copiar literalmente `Launchpad95/ConfigurableButtonElement.py` a `LaunchpadLooper/ConfigurableButtonElement.py` sin cambios (109 líneas; usa `_Framework.Skin` y `_Framework.ButtonElement`).

Run (PowerShell): `Copy-Item Launchpad95\ConfigurableButtonElement.py LaunchpadLooper\ConfigurableButtonElement.py`

- [ ] **Step 2: Escribir `LaunchpadLooper/Colors.py`**

```python
"""Colores del Launchpad MK1 y skin de LaunchpadLooper."""
from _Framework.ButtonElement import Color
from _Framework.Skin import Skin


class Rgb:
    BLACK = Color(4)
    RED = Color(7)
    RED_HALF = Color(6)
    RED_THIRD = Color(5)
    RED_BLINK = Color(11)
    GREEN = Color(52)
    GREEN_HALF = Color(36)
    GREEN_THIRD = Color(20)
    GREEN_BLINK = Color(56)
    AMBER = Color(55)
    AMBER_HALF = Color(38)
    AMBER_THIRD = Color(21)
    AMBER_BLINK = Color(59)


class Colors:

    class DefaultButton:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        Disabled = Rgb.BLACK

    class Looper:

        class Slot:
            Empty = Rgb.BLACK
            Stopped = Rgb.AMBER_THIRD
            Playing = Rgb.GREEN
            Recording = Rgb.RED
            StopPending = Rgb.AMBER
            Delete = Rgb.RED
            CopyOrigin = Rgb.AMBER
            InitPending = Rgb.RED_BLINK

        class Scene:
            Off = Rgb.BLACK
            Playing = Rgb.GREEN
            Snap = Rgb.AMBER
            Delete = Rgb.RED

        class Value:
            Selected = Rgb.AMBER
            Idle = Rgb.AMBER_THIRD
            Off = Rgb.BLACK

        class Top:
            Undo = Rgb.AMBER_THIRD
            UndoHeld = Rgb.AMBER
            FixedLengthOff = Rgb.GREEN_THIRD
            FixedLengthOn = Rgb.GREEN_BLINK
            Quantize = Rgb.AMBER
            Delete = Rgb.RED
            Stop = Rgb.RED_THIRD
            Copy = Rgb.GREEN
            SnapshotA = Rgb.RED
            SnapshotB = Rgb.AMBER
            SnapshotC = Rgb.GREEN
            PulseOff = Rgb.BLACK
            PulseWeak = Rgb.GREEN_THIRD
            PulseStrong = Rgb.GREEN
            PulseMetroWeak = Rgb.AMBER_THIRD
            PulseMetroStrong = Rgb.AMBER
            Reject = Rgb.RED


SNAPSHOT_CYCLE = ('Looper.Top.SnapshotA', 'Looper.Top.SnapshotB', 'Looper.Top.SnapshotC')


def make_skin():
    return Skin(Colors)
```

- [ ] **Step 3: Correr la suite y verificar que `test_py2_syntax` sigue OK**

Run: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v`
Expected: todo OK.

---

### Task 11: LooperSession (Live)

**Files:**
- Create: `LaunchpadLooper/LooperSession.py`

Sin tests unitarios. Toda la decisión está en `Dispatch`, `SlotColors`, `SnapshotPlanner`, `ClipActions`; este módulo solo lee el estado de Live y ejecuta.

- [ ] **Step 1: Escribir `LaunchpadLooper/LooperSession.py`**

```python
"""SessionComponent 8x8 fija: pads, laterales, LEDs, desarme al cerrar."""
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
    from .SnapshotPlanner import plan_snapshot
except (ImportError, ValueError):
    import consts
    import Dispatch
    import SlotColors
    import Pulse
    from SnapshotPlanner import plan_snapshot

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

    def state(self):
        slot = self._clip_slot
        if slot is None:
            return SlotColors.EMPTY
        track = slot.canonical_parent
        has_clip = slot.has_clip
        clip = slot.clip if has_clip else None
        is_playing = bool(clip is not None and clip.is_playing)
        is_recording = bool(clip is not None and clip.is_recording)
        is_triggered = bool(clip.is_triggered if clip is not None else slot.is_triggered)
        will_record = bool(slot.will_record_on_start) if not has_clip else False
        stop_pending = bool(track.fired_slot_index == -2) and (is_playing or is_recording)
        return SlotColors.slot_state(has_clip, is_triggered, will_record,
                                     is_playing, is_recording, stop_pending)

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

    def _update_launch_button(self):
        if self.is_enabled() and self._launch_button is not None:
            if self._parent is None or self._scene is None:
                self._launch_button.set_light('Looper.Scene.Off')
            else:
                self._launch_button.set_light(self._parent.scene_color_for(self))


class LooperSession(SessionComponent):
    scene_component_type = LooperScene

    def __init__(self, settings, actions, modifiers, control_surface, *a, **k):
        self._settings = settings
        self._actions = actions
        self._modifiers = modifiers
        self._control_surface = control_surface
        self._copy_origin = None
        self._armed_by_script = []
        self._init_pending = False
        self._blink_on = True
        self._pulse_phase = Pulse.PULSE_BEAT
        super(LooperSession, self).__init__(num_tracks=consts.GRID_SIZE,
                                            num_scenes=consts.GRID_SIZE,
                                            enable_skinning=False,
                                            name='Looper_Session',
                                            is_root=True, *a, **k)
        for scene_index in range(consts.GRID_SIZE):
            self.scene(scene_index).set_parent(self, scene_index)
        self._register_timer_callback(self._on_tick)

    def disconnect(self):
        self._unregister_timer_callback(self._on_tick)
        self._copy_origin = None
        self._armed_by_script = []
        super(LooperSession, self).disconnect()

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
        slot = slot_component.live_slot()
        state = slot_component.state()
        action = Dispatch.pad_action(self.modifier(), state, self._copy_origin is not None)
        if action == Dispatch.RECORD:
            bars = None
            if self._settings.get('fixed_length_on'):
                bars = self._settings.get('fixed_length_bars')
            if self._actions.record(slot, bars):
                self._armed_by_script.append(slot.canonical_parent)
        elif action == Dispatch.LAUNCH:
            self._actions.launch(slot)
        elif action == Dispatch.STOP_IMMEDIATE:
            self._actions.stop_immediately(slot)
        elif action == Dispatch.CLOSE_RECORDING:
            self._actions.close_recording(slot)
        elif action == Dispatch.DELETE_CLIP:
            self._actions.delete_clip(slot)
        elif action == Dispatch.COPY_SET_ORIGIN:
            self._copy_origin = slot
        elif action == Dispatch.COPY_PASTE:
            if not self._actions.copy_clip(self._copy_origin, slot):
                self.flash_reject(slot_component._launch_button_value.subject)
        elif action == Dispatch.QUANTIZE_CLIP:
            grid = QUANTIZE_GRIDS[self._settings.get('quantize_grid')]
            self._actions.quantize_clip(slot, grid, self._settings.get('quantize_amount'))
        elif action == Dispatch.STOP_TRACK:
            self._actions.stop_track(slot.canonical_parent)
        self.update()

    def on_lateral(self, scene_component):
        index = scene_component.scene_index
        action, value = Dispatch.lateral_action(self.modifier(), index)
        if action == Dispatch.FIRE_SCENE:
            scene_component.live_scene().fire()
        elif action == Dispatch.SET_FIXED_LENGTH:
            self._settings.set_fixed_length_index(value)
            self._modifiers.note_lateral_touch()
        elif action == Dispatch.SET_QUANTIZE_GRID:
            self._settings.set_quantize_grid_index(value)
            self._modifiers.note_lateral_touch()
        elif action == Dispatch.SET_QUANTIZE_AMOUNT:
            self._settings.set_quantize_amount_index(value)
            self._modifiers.note_lateral_touch()
        elif action == Dispatch.DELETE_ROW:
            self._actions.delete_row(scene_component.live_scene(), consts.SNAP_NAME)
        elif action == Dispatch.STOP_ROW:
            self._actions.stop_row(self.tracks(), value)
        self.update()

    def clear_copy_origin(self):
        self._copy_origin = None

    def set_init_pending(self, pending):
        self._init_pending = bool(pending)
        self.update()

    # -- snapshot e INIT --------------------------------------------------

    def take_snapshot(self):
        """Devuelve None si se hizo, o el motivo del rechazo."""
        row, reason, copies = plan_snapshot(_GridView(self))
        if reason is not None:
            return reason
        self._actions.take_snapshot(self.scenes(), row, copies, consts.SNAP_NAME)
        self.update()
        return None

    def init_grid(self):
        self._actions.init_grid(self.scenes(), consts.GRID_SIZE, consts.SNAP_NAME)
        self._copy_origin = None
        self.set_init_pending(False)

    # -- desarme al cerrar la grabacion -----------------------------------

    def on_recording_changed(self, slot_component):
        slot = slot_component.live_slot()
        if slot is None:
            return
        track = slot.canonical_parent
        if track not in self._armed_by_script:
            return
        clip = slot.clip if slot.has_clip else None
        still_recording = clip is not None and clip.is_recording
        if not still_recording:
            track_recording_elsewhere = False
            for other in track.clip_slots:
                if other.has_clip and other.clip.is_recording:
                    track_recording_elsewhere = True
                    break
            if not track_recording_elsewhere:
                track.arm = False
                self._armed_by_script.remove(track)

    # -- LEDs -------------------------------------------------------------

    def slot_color_for(self, slot_component):
        state = slot_component.state()
        is_origin = self._copy_origin is not None and slot_component.live_slot() == self._copy_origin
        return SlotColors.slot_color(state, self.modifier(), self._blink_on,
                                     is_copy_origin=is_origin, init_pending=self._init_pending)

    def scene_color_for(self, scene_component):
        modifier = self.modifier()
        index = scene_component.scene_index
        if modifier == 'fixed_length':
            return SlotColors.fixed_length_row(self._settings.fixed_length_index())[index]
        if modifier == 'quantize':
            return SlotColors.quantize_row(self._settings.quantize_grid_index(),
                                           self._settings.quantize_amount_index())[index]
        scene = scene_component.live_scene()
        has_playing = False
        has_clips = False
        for slot in list(scene.clip_slots)[:consts.GRID_SIZE]:
            if slot.has_clip:
                has_clips = True
                if slot.clip.is_playing:
                    has_playing = True
        is_snap = scene.name == consts.SNAP_NAME
        return SlotColors.scene_color(has_playing, is_snap, has_clips,
                                      bool(scene.is_triggered), modifier, self._blink_on)

    def flash_reject(self, button):
        if button is None:
            return
        button.set_light('Looper.Top.Reject')
        self._tasks.add(Task.sequence(Task.wait(consts.REJECT_FLASH), Task.run(self.update)))

    def _on_tick(self):
        song = self.song()
        try:
            beat_time = song.get_current_beats_song_time()
        except Exception:
            beat_time = None
        phase = Pulse.pulse_phase(beat_time, song.is_playing)
        on = Pulse.blink_on(phase)
        self._pulse_phase = phase
        if on != self._blink_on:
            self._blink_on = on
            self.update()


class _GridView(object):
    """Adaptador de la ventana 8x8 para SnapshotPlanner."""

    def __init__(self, session):
        self.num_tracks = consts.GRID_SIZE
        self.num_scenes = consts.GRID_SIZE
        self._scenes = session.scenes()

    def _slot(self, track, scene):
        slots = self._scenes[scene].clip_slots
        return slots[track] if track < len(slots) else None

    def has_clip(self, track, scene):
        slot = self._slot(track, scene)
        return bool(slot is not None and slot.has_clip)

    def is_playing(self, track, scene):
        slot = self._slot(track, scene)
        return bool(slot is not None and slot.has_clip and slot.clip.is_playing and not slot.clip.is_recording)

    def is_recording(self, track, scene):
        slot = self._slot(track, scene)
        return bool(slot is not None and slot.has_clip and slot.clip.is_recording)
```

Notas de implementación:
- `_register_timer_callback` está marcado DEPRECATED en el framework pero funciona en Live 9 y 10 y es lo que usa Launchpad95; llama al callback cada 100 ms.
- `update()` en cada medio pulso reenvía solo los LEDs cuyo valor cambió, porque `InputControlElement.send_value` descarta valores repetidos.
- `on_recording_changed` también se dispara al borrar un clip que grababa (cambia `has_clip`), lo que desarma la pista en el caso Delete más pad grabando.

- [ ] **Step 2: Correr la suite y verificar que `test_py2_syntax` sigue OK**

Run: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v`

---

### Task 12: TopControls (Live)

**Files:**
- Create: `LaunchpadLooper/TopControls.py`

- [ ] **Step 1: Escribir `LaunchpadLooper/TopControls.py`**

```python
"""Los 8 botones superiores: modificadores, Undo/Redo, Fixed Length,
Snapshot, Pulso/Tap/metronomo, acorde INIT y sus LEDs."""
import time
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework import Task

try:
    from . import consts
    from . import Pulse
    from .Colors import SNAPSHOT_CYCLE
except (ImportError, ValueError):
    import consts
    import Pulse
    from Colors import SNAPSHOT_CYCLE


class TopControls(ControlSurfaceComponent):

    def __init__(self, buttons, session, settings, actions, modifiers, tap_tempo, *a, **k):
        super(TopControls, self).__init__(name='Looper_Top', is_root=True, *a, **k)
        self._buttons = list(buttons)
        self._session = session
        self._settings = settings
        self._actions = actions
        self._modifiers = modifiers
        self._tap = tap_tempo
        self._snapshot_index = 0
        self._snapshot_elapsed = 0.0
        self._redo_task = self._tasks.add(Task.sequence(Task.wait(consts.LONG_PRESS), Task.run(self._do_redo)))
        self._redo_task.kill()
        self._metro_task = self._tasks.add(Task.sequence(Task.wait(consts.LONG_PRESS), Task.run(self._do_metronome)))
        self._metro_task.kill()
        self._init_task = self._tasks.add(Task.sequence(Task.wait(consts.INIT_HOLD), Task.run(self._do_init)))
        self._init_task.kill()
        for index, button in enumerate(self._buttons):
            button.add_value_listener(self._button_value, identify_sender=True)
        self._register_timer_callback(self._on_tick)
        self.update()

    def disconnect(self):
        self._unregister_timer_callback(self._on_tick)
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
        self._modifiers.press(name)
        if name == 'undo':
            self._redo_task.restart()
        elif name == 'pulse':
            self._metro_task.restart()
        elif name == 'snapshot':
            reason = self._session.take_snapshot()
            if reason is not None:
                self._session.flash_reject(self._buttons[consts.TOP_SNAPSHOT])
        if self._modifiers.chord_held():
            self._redo_task.kill()
            self._init_task.restart()
            self._session.set_init_pending(True)

    def _on_release(self, name):
        chord_was_held = self._modifiers.chord_held()
        event = self._modifiers.release(name)
        if name == 'undo':
            self._redo_task.kill()
        elif name == 'pulse':
            self._metro_task.kill()
        elif name == 'copy':
            self._session.clear_copy_origin()
        if chord_was_held and not self._modifiers.chord_held():
            self._init_task.kill()
            self._session.set_init_pending(False)
        if event == 'undo':
            self._actions.undo()
        elif event == 'toggle_fixed_length':
            self._settings.toggle_fixed_length()
        elif event == 'tap':
            tempo = self._tap.tap(time.time())
            if tempo is not None:
                self._actions.set_tempo(tempo)

    # -- pulsaciones largas y acorde --------------------------------------

    def _do_redo(self):
        self._modifiers.consume('undo')
        self._actions.redo()
        self.update()

    def _do_metronome(self):
        self._modifiers.consume('pulse')
        self._tap.reset()
        self._actions.toggle_metronome()
        self.update()

    def _do_init(self):
        self._session.init_grid()
        self.update()

    # -- LEDs -------------------------------------------------------------

    def update(self):
        super(TopControls, self).update()
        if not self.is_enabled() or not self._buttons:
            return
        held = self._modifiers.is_held
        self._buttons[consts.TOP_UNDO].set_light('Looper.Top.UndoHeld' if held('undo') else 'Looper.Top.Undo')
        if self._settings.get('fixed_length_on'):
            self._buttons[consts.TOP_FIXED_LENGTH].set_light('Looper.Top.FixedLengthOn')
        else:
            self._buttons[consts.TOP_FIXED_LENGTH].set_light('Looper.Top.FixedLengthOff')
        self._buttons[consts.TOP_QUANTIZE].set_light('Looper.Top.Quantize')
        self._buttons[consts.TOP_DELETE].set_light('Looper.Top.Delete')
        self._buttons[consts.TOP_STOP].set_light('Looper.Top.Stop')
        self._buttons[consts.TOP_COPY].set_light('Looper.Top.Copy')
        self._buttons[consts.TOP_SNAPSHOT].set_light(SNAPSHOT_CYCLE[self._snapshot_index])
        self._update_pulse_led()

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

    def _on_tick(self):
        self._snapshot_elapsed += consts.TIMER_TICK
        if self._snapshot_elapsed >= consts.SNAPSHOT_CYCLE:
            self._snapshot_elapsed = 0.0
            self._snapshot_index = (self._snapshot_index + 1) % len(SNAPSHOT_CYCLE)
            if self.is_enabled() and self._buttons:
                self._buttons[consts.TOP_SNAPSHOT].set_light(SNAPSHOT_CYCLE[self._snapshot_index])
        if self.is_enabled() and self._buttons:
            self._update_pulse_led()
```

Notas:
- Los `Task` de `_Framework` se crean una vez, se matan (`kill`) y se reinician (`restart`) en cada pulsación, el mismo patrón que `_end_undo_step_task` en Launchpad95.
- El orden en `_on_release`: primero se consulta `chord_held()` antes de soltar, para detectar la ruptura del acorde.
- El tap se cuenta al soltar: los intervalos entre soltadas son iguales a los intervalos entre apretadas en toques regulares, y así una pulsación larga nunca cuenta como tap.

- [ ] **Step 2: Correr la suite y verificar que `test_py2_syntax` sigue OK**

---

### Task 13: LaunchpadLooper (ControlSurface) y `__init__`

**Files:**
- Create: `LaunchpadLooper/LaunchpadLooper.py`
- Modify: `LaunchpadLooper/__init__.py`

- [ ] **Step 1: Escribir `LaunchpadLooper/LaunchpadLooper.py`**

```python
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
        with self.component_guard():
            self._skin = make_skin()
            self._config_button = ButtonElement(True, MIDI_CC_TYPE, 0, consts.CONFIG_CC, optimized_send_midi=False)
            self._build_controls()
            self._build_components()
            self.set_highlighting_session_component(self._session)
            self.request_rebuild_midi_map()
        self.log_message('LaunchpadLooper loaded')

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
        self._modifiers = ModifierState(consts.MODIFIER_NAMES, consts.INIT_CHORD)
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
        self._config_button.send_value(consts.CONFIG_RESET)
        self._config_button.send_value(consts.CONFIG_FLASH_AUTO)
        for control in self.controls:
            if isinstance(control, ConfigurableButtonElement):
                control.force_next_send()
        self.set_enabled(True)
        self.update()

    def _send_midi(self, midi_bytes, optimized=None):
        if self._suppress_send_midi:
            return False
        return ControlSurface._send_midi(self, midi_bytes, optimized=optimized)

    def disconnect(self):
        self._suppress_send_midi = True
        ControlSurface.disconnect(self)
        self._suppress_send_midi = False
        if self._config_button is not None:
            self._config_button.send_value(consts.CONFIG_FLASH_OFF)
            self._config_button.send_value(consts.CONFIG_RESET)
            self._config_button = None
```

- [ ] **Step 2: Completar `LaunchpadLooper/__init__.py`**

```python
from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
from LaunchpadLooper import LaunchpadLooper


def create_instance(c_instance):
    return LaunchpadLooper(c_instance)


def get_capabilities():
    return {
        CONTROLLER_ID_KEY: controller_id(
            vendor_id=4661,
            product_ids=[14, 32, 54],
            model_name=['Launchpad', 'Launchpad S', 'Launchpad Mini']),
        PORTS_KEY: [
            inport(props=[NOTES_CC, SCRIPT, REMOTE]),
            outport(props=[NOTES_CC, SCRIPT, SYNC, REMOTE])]
    }
```

Atención: `from LaunchpadLooper import LaunchpadLooper` dentro del paquete `LaunchpadLooper` importa el módulo `LaunchpadLooper.py` en Python 2 (import implícito relativo), igual que `from Launchpad import Launchpad` en Launchpad95. Esto rompe los tests bajo Python 3 si algo importa el paquete `LaunchpadLooper`, porque `_Framework` no existe. Por eso `__init__.py` debe quedar protegido:

```python
try:
    from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
    from LaunchpadLooper import LaunchpadLooper
    _IN_LIVE = True
except ImportError:
    _IN_LIVE = False


def create_instance(c_instance):
    return LaunchpadLooper(c_instance)


def get_capabilities():
    return {
        CONTROLLER_ID_KEY: controller_id(
            vendor_id=4661,
            product_ids=[14, 32, 54],
            model_name=['Launchpad', 'Launchpad S', 'Launchpad Mini']),
        PORTS_KEY: [
            inport(props=[NOTES_CC, SCRIPT, REMOTE]),
            outport(props=[NOTES_CC, SCRIPT, SYNC, REMOTE])]
    }
```

Usar esta segunda versión.

- [ ] **Step 3: Correr la suite completa**

Run: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v`
Expected: todo OK (los tests importan `LaunchpadLooper.X`, lo que ejecuta `__init__.py`; debe seguir funcionando sin `_Framework`).

---

### Task 14: Instalación y lista de verificación manual

**Files:**
- Create: `install.ps1`
- Create: `docs/manual-checklist-launchpad-looper.md`

- [ ] **Step 1: Escribir `install.ps1`**

```powershell
# Copia LaunchpadLooper a los MIDI Remote Scripts de Live 9 y Live 10.
$source = Join-Path $PSScriptRoot 'LaunchpadLooper'
$targets = @(
    'C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\LaunchpadLooper',
    'C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\LaunchpadLooper'
)
foreach ($target in $targets) {
    $parent = Split-Path $target -Parent
    if (-not (Test-Path $parent)) { Write-Host "No existe $parent, se omite"; continue }
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    New-Item -ItemType Directory -Force $target | Out-Null
    Get-ChildItem $source -Filter '*.py' | Where-Object { $_.Name -ne '__pycache__' } |
        Copy-Item -Destination $target
    Write-Host "Instalado en $target"
}
```

No se copian `tests/` ni `__pycache__`.

- [ ] **Step 2: Escribir `docs/manual-checklist-launchpad-looper.md`**

```markdown
# LaunchpadLooper — verificación manual en Live

Preparación: set con 8 pistas de audio con entrada asignada y Monitor Off, 8 escenas vacías, cuantización de lanzamiento en 1 Bar, LaunchpadLooper elegido en Preferencias > MIDI con entrada y salida del Launchpad. Repetir en Live 9 y Live 10.

## Arranque
- [ ] Al cargar, la grilla queda apagada, los laterales apagados, los superiores con sus colores (Undo ámbar tenue, Fixed Length verde tenue, Quantize ámbar, Delete rojo, Stop rojo tenue, Copy verde, Snapshot ciclando, Pulso latiendo en verde).
- [ ] El rectángulo rojo de Live cubre pistas 1–8 y escenas 1–8.
- [ ] Con Play, el botón Pulso late en cada negra y más fuerte en el uno.

## Pads
- [ ] Slot vacío: parpadea rojo al pulso hasta el compás, luego rojo fijo grabando; la pista se armó. Al tocar de nuevo cierra en el próximo compás, queda verde y la pista se desarma.
- [ ] Fixed Length prendido en 2 compases: la grabación cierra sola a los 2 compases, pista desarmada.
- [ ] Clip detenido: parpadea verde al pulso y entra en el compás.
- [ ] Clip sonando: se detiene al instante. La cuantización de lanzamiento de Live sigue en 1 Bar.
- [ ] Dos slots vacíos en pistas distintas tocados dentro del mismo compás arrancan juntos y se desarman cada uno al cerrar.
- [ ] Pista ya armada a mano: grabar no la desarma al terminar.

## Undo / Redo
- [ ] Toque corto deshace. Mantener medio segundo rehace y al soltar no deshace.

## Fixed Length
- [ ] Toque corto alterna; LED titila prendido, verde tenue apagado. El estado sobrevive a cerrar y abrir Live.
- [ ] Mantener: laterales 1–5 muestran 1, 2, 4, 8, 16, el elegido fuerte. Tocar uno lo cambia; al soltar el estado no cambió.

## Quantize
- [ ] Mantener: laterales 1–5 resoluciones, 6 apagado, 7–8 cantidades. Elegir 1/8 y 50%.
- [ ] Quantize más pad con clip de audio: los warp markers se mueven la mitad hacia la grilla de 1/8.

## Delete
- [ ] Mantener: clips rojos, filas con clips rojas. Más pad borra. Más pad grabando cancela y deja vacío, pista desarmada.
- [ ] Más lateral de una fila: borra sus 8 clips y el nombre SNAP; un solo Undo lo recupera todo.

## Stop
- [ ] Mantener: solo se ven clips sonando y grabando y laterales con clips sonando.
- [ ] Más pad de columna sonando: alterna ámbar/verde al pulso y para en el compás. Más pad de columna grabando: ámbar/rojo y queda detenida.
- [ ] Más lateral: paran solo las pistas cuyo clip sonando está en esa fila. Tocar dos laterales seguidos: todo para en el mismo compás.
- [ ] Lanzar una fila vacía detiene todo en el compás.

## Copy
- [ ] Mantener, tocar clip: parpadea. Tocar dos slots vacíos: dos copias. Tocar slot ocupado: parpadeo rojo, no se pisa. Soltar: se limpia.

## Snapshot
- [ ] Con clips sonando en filas 1 y 2: Snapshot crea en fila 8 copias solo de los que suenan, nombre SNAP, lateral 8 ámbar. Un Undo lo deshace entero.
- [ ] Segundo Snapshot va a la fila 7.
- [ ] Con una pista grabando: parpadeo rojo del botón, nada cambia.
- [ ] Con las 8 filas ocupadas: parpadeo rojo.
- [ ] Tocar lateral de la SNAP: entra en el compás, las pistas sin clip en la fila se callan.

## Pulso / Tap / Metrónomo
- [ ] Cuatro toques a 120 ponen el tempo en ~120. Tres toques no cambian nada. Pausa de 3 s y cuatro toques nuevos funcionan.
- [ ] Mantener medio segundo alterna el metrónomo; el latido pasa a ámbar. No cuenta como tap.

## INIT
- [ ] Undo + Fixed Length + Quantize mantenidos: la grilla parpadea roja; soltar antes de medio segundo cancela y ninguno de los tres hizo nada.
- [ ] Mantenidos más de medio segundo: los 64 slots quedan vacíos, nombres SNAP borrados, pistas y escenas intactas, un solo Undo lo recupera.

## Persistencia
- [ ] Cerrar Live con Fixed Length prendido en 8, Quantize 1/8t al 50%; abrir: igual. Archivo en `%USERPROFILE%\.launchpad_looper.json`.

## Desconexión
- [ ] Cambiar el script a None en Preferencias: el Launchpad se apaga, sin errores en Log.txt.
```

- [ ] **Step 3: Correr la suite completa una última vez**

Run: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t . -v`
Expected: todo OK.

- [ ] **Step 4: Instalar**

Run: `powershell -ExecutionPolicy Bypass -File install.ps1`
Expected: "Instalado en ..." para Live 9 y Live 10. Luego el usuario verifica con la lista manual.

---

## Autorrevisión del plan contra la especificación

| Sección de la spec | Tarea |
|---|---|
| 2 mapa de botones | Task 1 consts, Task 13 cableado |
| 3 pads sin modificador, autorecord acumulativo, desarme | Task 7 Dispatch, Task 9 record, Task 11 on_pad / on_recording_changed |
| 4.1 stop inmediato | Task 9 stop_immediately |
| 4.2 Undo/Redo | Task 2, Task 12 |
| 4.3 Fixed Length | Task 2 (toggle/touch), Task 6 fila, Task 8 settings, Task 12 LED |
| 4.4 Quantize | Task 6 fila, Task 7, Task 9, Task 11 QUANTIZE_GRIDS |
| 4.5 Delete | Task 7, Task 9 delete_clip/delete_row, Task 6 colores |
| 4.6 Stop | Task 7, Task 9 stop_track/stop_row, Task 6 colores |
| 4.7 Copy | Task 7, Task 9 copy_clip, Task 11 origen y rechazo |
| 4.8 Snapshot | Task 5, Task 9 take_snapshot, Task 11, Task 12 rechazo |
| 4.9 INIT | Task 2 acorde, Task 9 init_grid, Task 11 init_pending, Task 12 tarea |
| 4.10 Pulso/Tap/Metrónomo | Task 3, Task 4, Task 12 |
| 4.11 escenas | Task 6 scene_color, Task 11 |
| 5 colores | Task 6, Task 10 |
| 6 persistencia | Task 8 |
| 7 arquitectura | estructura de archivos |
| 8 pruebas | tests por tarea + Task 14 lista manual |

Consistencia de nombres verificada: `ModifierState.press/release/consume/note_lateral_touch/active/chord_held/is_held`; `TapTempo.tap/reset/is_counting`; `Pulse.pulse_phase/blink_on`; `SnapshotPlanner.plan_snapshot/find_free_row`; `SlotColors.slot_state/slot_color/scene_color/fixed_length_row/quantize_row`; `Dispatch.pad_action/lateral_action`; `Settings.get/set/toggle_fixed_length/*_index/set_*_index`; `ClipActions.stop_immediately/record/launch/close_recording/delete_clip/copy_clip/quantize_clip/stop_track/stop_row/delete_row/take_snapshot/init_grid/undo/redo/set_tempo/toggle_metronome`; `LooperSession.on_pad/on_lateral/clear_copy_origin/set_init_pending/take_snapshot/init_grid/on_recording_changed/slot_color_for/scene_color_for/flash_reject/pulse_phase/blink_on`.
