# LaunchpadLooper Gain de clip — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** implementar la spec `docs/specs/2026-10-21-launchpad-looper-clip-gain-design.md`: con Snapshot mantenido, los laterales fijan el gain del último clip tocado en 8 niveles fijos de dB.

**Architecture:** módulo puro nuevo `ClipGain` (niveles, parser del texto en dB, nivel más cercano, color de laterales, calibración por bisección) con tests; foco en `BounceSelection`; rama `SET_GAIN` en `Dispatch`; `ClipActions.set_gain_level` agrupa calibración y escritura en un paso de Undo; cableado fino en `LooperSession` (laterales bajo `snapshot` y color de laterales), sin cambios en `TopControls`.

**Tech Stack:** Python 2.7/3 común, `unittest`, fakes en `LaunchpadLooper/tests/fakes.py`. Tests: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t .` desde `C:\MY_GITHUB\Launchpad97-master`. No hay git: no hay commits. Borrar `__pycache__` al terminar.

---

## Archivos

- Crear: `LaunchpadLooper/ClipGain.py`, `LaunchpadLooper/tests/test_clip_gain.py`
- Modificar: `LaunchpadLooper/BounceState.py` (foco, marca sin alternar), `LaunchpadLooper/Dispatch.py` (`SET_GAIN`), `LaunchpadLooper/Messages.py` (3 textos), `LaunchpadLooper/ClipActions.py` (`set_gain_level`), `LaunchpadLooper/LooperSession.py` (rama `SET_GAIN`, color de laterales), `LaunchpadLooper/tests/fakes.py` (`FakeClip.gain`), tests existentes de bounce_state, dispatch y messages
- Docs: `docs/manual-checklist-launchpad-looper.md`, `README-LaunchpadLooper.md`, `docs/manual-visual-launchpad-looper.html` (+ PDF), spec principal, zip

---

### Task 1: ClipGain puro (niveles, parser, color)

**Files:** crear `LaunchpadLooper/ClipGain.py`, `LaunchpadLooper/tests/test_clip_gain.py`

- [x] **Step 1: test que falla**

```python
import math
import unittest

from LaunchpadLooper import ClipGain as G


class LevelsTest(unittest.TestCase):

    def test_eight_levels_descending_with_zero_at_index_2(self):
        self.assertEqual((6.0, 3.0, 0.0, -3.0, -6.0, -12.0, -15.0, -18.0), G.LEVELS_DB)
        self.assertEqual(2, G.ZERO_INDEX)
        self.assertEqual(8, len(G.FALLBACK))


class ParseDbTest(unittest.TestCase):

    def test_plain_values(self):
        self.assertEqual(6.0, G.parse_db('+6.0 dB'))
        self.assertEqual(-3.0, G.parse_db('-3.0 dB'))
        self.assertEqual(0.0, G.parse_db('0.0 dB'))
        self.assertEqual(-3.5, G.parse_db('-3,5 dB'))

    def test_infinity_and_garbage(self):
        self.assertEqual(float('-inf'), G.parse_db('-inf dB'))
        self.assertIsNone(G.parse_db(''))
        self.assertIsNone(G.parse_db(None))
        self.assertIsNone(G.parse_db('dB'))


class NearestLevelTest(unittest.TestCase):

    def test_exact_and_between(self):
        self.assertEqual(0, G.nearest_level(6.0))
        self.assertEqual(3, G.nearest_level(-3.0))
        self.assertEqual(5, G.nearest_level(-10.0))
        self.assertEqual(7, G.nearest_level(-40.0))
        self.assertEqual(7, G.nearest_level(float('-inf')))
        self.assertEqual(0, G.nearest_level(20.0))
        self.assertIsNone(G.nearest_level(None))


class LateralColorTest(unittest.TestCase):

    def test_no_focus_is_off(self):
        for i in range(8):
            self.assertEqual('Looper.Scene.Off', G.lateral_color(i, None))

    def test_current_zero_and_rest(self):
        self.assertEqual('Looper.Scene.Playing', G.lateral_color(4, 4))
        self.assertEqual('Looper.Scene.Stopped', G.lateral_color(2, 4))
        self.assertEqual('Looper.Scene.Off', G.lateral_color(0, 4))
        self.assertEqual('Looper.Scene.Playing', G.lateral_color(2, 2))
```

- [x] **Step 2:** correr `C:\Python311\python.exe -m unittest LaunchpadLooper.tests.test_clip_gain` → ImportError.
- [x] **Step 3: implementación**

```python
"""Gain de clip en escalera de 8 niveles (laterales con Snapshot abajo). Modulo puro."""

import re

LEVELS_DB = (6.0, 3.0, 0.0, -3.0, -6.0, -12.0, -15.0, -18.0)
NUM_LEVELS = len(LEVELS_DB)
ZERO_INDEX = 2
# aproximacion (curva lineal de 40 dB por unidad, 0 dB en 0.85) si no se
# puede leer el texto en dB de Live
FALLBACK = (1.0, 0.925, 0.85, 0.775, 0.7, 0.55, 0.475, 0.4)

_DB_RE = re.compile(r'([+-]?)\s*(inf|\d+(?:[.,]\d+)?)', re.IGNORECASE)


def parse_db(text):
    if text is None:
        return None
    match = _DB_RE.search(str(text))
    if match is None:
        return None
    sign = -1.0 if match.group(1) == '-' else 1.0
    body = match.group(2).lower().replace(',', '.')
    if body == 'inf':
        return sign * float('inf')
    return sign * float(body)


def nearest_level(db):
    if db is None:
        return None
    best, best_distance = 0, None
    for index, level in enumerate(LEVELS_DB):
        distance = abs(level - db)
        if best_distance is None or distance < best_distance:
            best, best_distance = index, distance
    return best


def lateral_color(index, current_index):
    if current_index is None:
        return 'Looper.Scene.Off'
    if index == current_index:
        return 'Looper.Scene.Playing'
    if index == ZERO_INDEX:
        return 'Looper.Scene.Stopped'
    return 'Looper.Scene.Off'
```

- [x] **Step 4:** correr el test → OK.

### Task 2: Calibración por bisección

**Files:** `LaunchpadLooper/ClipGain.py`, `LaunchpadLooper/tests/test_clip_gain.py`

- [x] **Step 1: test que falla** (curva simulada: dB = 40·(g − 0,85), "-inf dB" en 0)

```python
class FakeGainClip(object):
    def __init__(self):
        self.gain = 0.85

    def display(self):
        if self.gain <= 0.0:
            return '-inf dB'
        return '%+.1f dB' % (40.0 * (self.gain - 0.85))


class CalibrationTest(unittest.TestCase):

    def test_starts_with_fallback(self):
        cal = G.Calibration()
        self.assertFalse(cal.is_done())
        self.assertEqual(G.FALLBACK[3], cal.value_for(3))

    def test_calibrates_all_levels_on_a_monotonic_curve(self):
        clip = FakeGainClip()
        cal = G.Calibration()
        approx = cal.calibrate(lambda v: setattr(clip, 'gain', v), clip.display)
        self.assertEqual([], approx)
        self.assertTrue(cal.is_done())
        for index, target in enumerate(G.LEVELS_DB):
            clip.gain = cal.value_for(index)
            self.assertEqual(target, G.parse_db(clip.display()), index)

    def test_unreachable_level_is_reported_as_approximate(self):
        clip = FakeGainClip()
        cal = G.Calibration()
        # curva que tope en +3 dB: +6 no se alcanza
        approx = cal.calibrate(lambda v: setattr(clip, 'gain', min(v, 0.925)), clip.display)
        self.assertEqual([0], approx)
        self.assertTrue(cal.is_done())

    def test_unreadable_text_keeps_fallback(self):
        cal = G.Calibration()
        self.assertIsNone(cal.calibrate(lambda v: None, lambda: 'nada'))
        self.assertFalse(cal.is_done())
        self.assertEqual(G.FALLBACK[0], cal.value_for(0))
```

- [x] **Step 2:** correr → AttributeError `Calibration`.
- [x] **Step 3: implementación** (agregar a `ClipGain.py`)

```python
class Calibration(object):
    """Tabla float->nivel hallada por biseccion sobre un clip real.
    `calibrate(write, read)`: write(float) escribe el gain, read() devuelve
    el texto en dB. Devuelve la lista de niveles que quedaron aproximados,
    o None si el texto no se pudo leer (queda FALLBACK)."""

    ITERATIONS = 24
    TOLERANCE = 0.05

    def __init__(self):
        self._values = None
        self.approximate = []

    def is_done(self):
        return self._values is not None

    def value_for(self, index):
        table = self._values if self._values is not None else FALLBACK
        return table[index]

    def calibrate(self, write, read):
        values, approximate = [], []
        for index, target in enumerate(LEVELS_DB):
            value, exact = self._search(target, write, read)
            if value is None:
                self._values = None
                return None
            values.append(value)
            if not exact:
                approximate.append(index)
        self._values = tuple(values)
        self.approximate = approximate
        return approximate

    def _search(self, target, write, read):
        low, high = 0.0, 1.0
        best, best_distance = None, None
        for _ in range(self.ITERATIONS):
            mid = (low + high) / 2.0
            write(mid)
            db = parse_db(read())
            if db is None:
                return (None, False)
            distance = abs(db - target)
            if best_distance is None or distance < best_distance:
                best, best_distance = mid, distance
            if distance <= self.TOLERANCE:
                return (mid, True)
            if db < target:
                low = mid
            else:
                high = mid
        return (best, False)
```

- [x] **Step 4:** correr → OK.

### Task 3: Foco en BounceSelection, marca sin alternar

**Files:** `LaunchpadLooper/BounceState.py`, `LaunchpadLooper/tests/test_bounce_state.py`

- [x] **Step 1:** reemplazar `test_unmarking_everything_still_counts_as_touched` y `test_mark_toggles_and_keeps_order` por:

```python
    def test_mark_twice_keeps_mark_and_order(self):
        self.sel.press(0.0)
        self.assertTrue(self.sel.mark((2, 1)))
        self.assertTrue(self.sel.mark((0, 0)))
        self.assertTrue(self.sel.mark((2, 1)))
        self.assertEqual([(2, 1), (0, 0)], self.sel.marked())
        self.assertTrue(self.sel.is_marked((2, 1)))

    def test_focus_follows_last_touch(self):
        self.sel.press(0.0)
        self.assertIsNone(self.sel.focused())
        self.sel.mark((2, 1))
        self.sel.mark((0, 0))
        self.assertEqual((0, 0), self.sel.focused())
        self.sel.mark((2, 1))
        self.assertEqual((2, 1), self.sel.focused())

    def test_focus_is_cleared_on_release_and_ignored_when_inactive(self):
        self.sel.press(0.0)
        self.sel.mark((1, 1))
        self.sel.release(0.1)
        self.assertIsNone(self.sel.focused())
        self.sel.mark((1, 1))
        self.assertIsNone(self.sel.focused())
```

- [x] **Step 2:** correr `test_bounce_state` → fallan (focused no existe, mark alterna).
- [x] **Step 3:** en `BounceSelection`: `self._focus = None` en `__init__`, `press` y `clear`; `mark`:

```python
    def mark(self, key):
        """Marca (sin alternar) y deja el clip enfocado. Devuelve True si marco."""
        if not self._active:
            return False
        self._touched = True
        self._focus = key
        if key not in self._marked:
            self._marked.append(key)
        return True

    def focused(self):
        return self._focus
```

- [x] **Step 4:** correr → OK.

### Task 4: Dispatch y Messages

**Files:** `Dispatch.py`, `Messages.py`, `tests/test_dispatch.py`, `tests/test_messages.py`

- [x] **Step 1:** en `test_dispatch.py` cambiar la línea `self.assertEqual((D.NONE, 3), D.lateral_action('snapshot', 3))` por `self.assertEqual((D.SET_GAIN, 3), D.lateral_action('snapshot', 3))`. En `test_messages.py` agregar:

```python
    def test_gain_messages(self):
        self.assertEqual('GAIN  PISTA 1  ESCENA 2: -3.0 DB', M.text('gain', track=0, scene=1, db='-3.0 dB'))
        self.assertEqual('GAIN: TOCAR UN CLIP SONANDO PRIMERO', M.text('gain_no_focus'))
        self.assertEqual('GAIN: ERROR DE LIVE (VER LOG)', M.text('gain_failed'))
        self.assertIn('LATERAL = GAIN', M.text('press_snapshot'))
```

- [x] **Step 2:** correr → fallan.
- [x] **Step 3:** `Dispatch`: `SET_GAIN = 'set_gain'`; en `lateral_action`: `if modifier == 'snapshot': return (SET_GAIN, index)` antes del caso `copy`. `Messages._TEMPLATES`: `'press_snapshot': 'SNAPSHOT: SOLTAR = FOTO  /  + CLIPS + SLOT VACIO = BOUNCE  /  + CLIP + LATERAL = GAIN'`, `'gain': 'GAIN  PISTA %(track)d  ESCENA %(scene)d: %(db)s'`, `'gain_no_focus': 'GAIN: TOCAR UN CLIP SONANDO PRIMERO'`, `'gain_failed': 'GAIN: ERROR DE LIVE (VER LOG)'`.
- [x] **Step 4:** correr → OK.

### Task 5: ClipActions.set_gain_level

**Files:** `ClipActions.py`, `tests/fakes.py`, `tests/test_clip_actions.py`

- [x] **Step 1:** `FakeClip` con gain y curva simulada:

```python
    # en __init__: gain=0.85 como parametro; self._gain = gain; self.raise_on_gain = None; self.gain_writes = 0
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
```

Tests nuevos en `test_clip_actions.py` (clase `GainTest`, mismo setUp que las demás: `FakeSong`, `ClipActions(song, 'q_none')`):

```python
    def test_first_use_calibrates_and_sets_in_one_undo_step(self):
        clip = FakeClip(is_playing=True)
        cal = ClipGain.Calibration()
        self.assertTrue(self.actions.set_gain_level(clip, cal, 3))
        self.assertTrue(cal.is_done())
        self.assertEqual('-3.0 dB', clip.gain_display_string)
        self.assertEqual((1, 1), (self.song.undo_begin, self.song.undo_end))

    def test_next_use_only_writes_once(self):
        clip = FakeClip(is_playing=True)
        cal = ClipGain.Calibration()
        self.actions.set_gain_level(clip, cal, 3)
        clip.gain_writes = 0
        self.assertTrue(self.actions.set_gain_level(clip, cal, 0))
        self.assertEqual(1, clip.gain_writes)
        self.assertEqual('+6.0 dB', clip.gain_display_string)

    def test_live_error_restores_and_returns_false(self):
        clip = FakeClip(is_playing=True)
        clip.raise_on_gain = RuntimeError('no')
        cal = ClipGain.Calibration()
        self.assertFalse(self.actions.set_gain_level(clip, cal, 3))
        self.assertFalse(cal.is_done())
        self.assertEqual(0.85, clip.gain)
        self.assertEqual((1, 1), (self.song.undo_begin, self.song.undo_end))
```

- [x] **Step 2:** correr → fallan.
- [x] **Step 3:** en `ClipActions`:

```python
    def set_gain_level(self, clip, calibration, index):
        """Fija el gain del clip en el nivel `index` de ClipGain.LEVELS_DB.
        Si la tabla no esta calibrada, calibra primero sobre este clip.
        Todo en un solo paso de Undo. Devuelve True si pudo escribir."""
        def run():
            original = clip.gain
            try:
                if not calibration.is_done():
                    approx = calibration.calibrate(lambda v: setattr(clip, 'gain', v),
                                                   lambda: clip.gain_display_string)
                    if approx is None:
                        self._log('LaunchpadLooper gain: texto en dB ilegible, tabla aproximada')
                    elif approx:
                        self._log('LaunchpadLooper gain: niveles aproximados %s' % approx)
                clip.gain = float(calibration.value_for(index))
                return True
            except RuntimeError as error:
                self._log('LaunchpadLooper set_gain_level: %s' % error)
                try:
                    clip.gain = original
                except RuntimeError:
                    pass
                return False
        return self._undo_step(run)
```

Importar `ClipGain` arriba con el mismo patrón `try: from . import ...`.

- [x] **Step 4:** correr → OK. Correr toda la suite.

### Task 6: Cableado en LooperSession

**Files:** `LaunchpadLooper/LooperSession.py` (sin test automático: se verifica en Live)

- [x] **Step 1:** importar `ClipGain` (ambas ramas del try). En `__init__`, junto a `self._bounce_sel`: `self._gain_calibration = ClipGain.Calibration()`.
- [x] **Step 2:** en `on_lateral`, antes de `elif action == Dispatch.DELETE_ROW`:

```python
        elif action == Dispatch.SET_GAIN:
            self._set_gain_level(value)
```

y los métodos:

```python
    def _focused_clip(self):
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
        self._bounce_sel.note_touch()
        clip = self._focused_clip()
        if clip is None:
            self.show('gain_no_focus')
            return
        track, scene = self._bounce_sel.focused()
        if self._actions.set_gain_level(clip, self._gain_calibration, index):
            self.show('gain', track=track, scene=scene, db=clip.gain_display_string)
        else:
            self.show('gain_failed')
```

- [x] **Step 3:** en `scene_color_for`, después del caso `quantize`: `if modifier == 'snapshot': return ClipGain.lateral_color(index, self._focused_gain_index())`.
- [x] **Step 4:** en `show`, loguear también `event.startswith('gain')`.
- [x] **Step 5:** `python -m py_compile` de los archivos tocados con Python 3.11 y suite completa; borrar `__pycache__`.

### Task 7: Docs, instalación y zip

- [x] Spec principal `docs/specs/2026-10-18-launchpad-looper-design.md`: en la tabla de superiores, Snapshot mantenido menciona el gain y remite a la spec nueva.
- [x] Checklist: sección "Gain (Snapshot mantenido)" con: lateral sin foco → mensaje; tocar clip y lateral 4 → "-3.0 DB", lateral 4 verde, lateral 3 ámbar tenue; Undo deshace el toque entero (incluida la primera calibración); tocar de nuevo un clip marcado no lo desmarca; soltar sin destino no saca foto ni bouncea; el bounce de un clip a -6 dB suena más bajo.
- [x] README: fila Snapshot "Mantener" y párrafo nuevo "Gain de clip".
- [x] Manual visual HTML: texto del botón Snapshot (mantener) y de los laterales con Snapshot; regenerar PDF con Chrome headless.
- [x] `install.ps1` y rebuild de `dist/LaunchpadLooper-2026-10-21.zip` (borrar el del 20).
- [x] Memoria del proyecto: una línea sobre el gain y la calibración.
