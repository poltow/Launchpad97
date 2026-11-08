# LaunchpadLooper Bounce — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** implementar la spec `docs/specs/2026-10-20-launchpad-looper-bounce-design.md`: Snapshot mantenido + clips sonando + slot vacío graba un bounce por el retorno BOUNCE, con la matriz de comportamiento 2.3.

**Architecture:** igual que el resto del script: módulos puros con tests (`BouncePlanner`, `BounceState`, `BounceGuard`, `Routing` por duck typing, extensiones de `ClipActions`, `Dispatch`, `SlotColors`, `Messages`) y cableado fino en `LooperSession` y `TopControls`, que solo se verifica en Live. Un único bounce en curso, representado por `BounceJob`.

**Tech Stack:** Python 2.7/3 común, `unittest`, fakes en `LaunchpadLooper/tests/fakes.py`. Tests: `C:\Python311\python.exe -m unittest discover -s LaunchpadLooper\tests -t .` desde la raíz. No hay git: no hay commits.

---

## Interfaces acordadas

```python
# consts
MODIFIER_NAMES = ('fixed_length', 'quantize', 'delete', 'stop', 'copy', 'snapshot')
BOUNCE_RETURN_NAME = 'BOUNCE'; BOUNCE_MAX_BARS = 64; BOUNCE_SEND_LEVEL = 1.0
SENDS_ONLY = 'Sends Only'; MONITOR_IN, MONITOR_AUTO, MONITOR_OFF = 0, 1, 2

# BouncePlanner (puro)
lcm(a, b); length_beats(lengths_beats, beats_per_bar, fixed_length_bars=None) -> beats enteros, compases enteros
plan_bounce(grid, marked, target, fixed_length_bars, in_progress) -> (origins, length_beats, reason)
# grid: num_tracks, num_scenes, has_clip, is_playing, is_recording, clip_length(t, s), is_audio_track(t), beats_per_bar
REJECT_*: in_progress, recording, nothing_playing, target_occupied, target_on_origin_track, target_not_audio, too_long

# BounceState (puro)
BounceSelection(long_press): press(now), mark(key)->bool, unmark, marked(), touched(), release(now)->'snapshot'|None, clear(), is_active()
BounceJob(target, origins, origin_tracks, saved, bars): started, closing, origins_stopped, finished; involves_track(t), involves_row(s), is_origin_track(t), is_target(key)

# BounceGuard (puro)   P1 = job and not job.started ; P2/P3 = job.started
pad_decision(job, modifier, key, state) -> ALLOW | REJECT | CANCEL | CLOSE | IGNORE
lateral_decision(job, modifier, scene_index, row_tracks) -> ALLOW | REJECT
top_decision(job, name) -> ALLOW | REJECT | CANCEL | CLOSE

# Dispatch: modifier 'snapshot' -> BOUNCE_MARK (pad sonando), BOUNCE_TARGET (pad vacio), NONE; lateral -> NONE
# SlotColors: modifier 'snapshot': sonando verde, marcado ambar/apagado al pulso, resto apagado; scene_color -> Off

# Routing (duck typing)
find_return(song, name) -> (index, track) | (None, None)
ensure_return(song, name, sends_only) -> (index, track, created)
input_routing_for(track, return_index, return_name) -> cadena de track.input_routings | None

# ClipActions
bounce_start(origin_slots, target_slot, length_beats, send_index, input_routing) -> saved | None
bounce_restore(saved); bounce_cancel(target_slot); stop_tracks(tracks)
```

---

### Task 1: constantes y mensajes

**Files:** `LaunchpadLooper/consts.py`, `LaunchpadLooper/Messages.py`, `LaunchpadLooper/tests/test_messages.py`, `LaunchpadLooper/tests/test_py2_syntax.py` (si verifica consts)

- [ ] Test: `press_snapshot`, `bounce_marked`, `bounce_start`, `bounce_reject` por cada razón, `bounce_busy`, `bounce_cancelled`, `bounce_closing`, `bounce_done`, `bounce_cut`, `bounce_return_created`, todo ASCII y mayúsculas.
- [ ] Implementar plantillas. `MODIFIER_NAMES` suma `'snapshot'`; constantes de bounce.
- [ ] Correr tests: verde.

### Task 2: BouncePlanner

**Files:** `LaunchpadLooper/BouncePlanner.py`, `LaunchpadLooper/tests/test_bounce_planner.py`

- [ ] Tests de `lcm` y `length_beats`: 8 y 16 beats → 16; 8 y 12 → 24; 6 y 8 (1,5 y 2 compases) → 24; 2 beats solo → 4 (un compás); Fixed Length 2 compases con mcm 16 → 8; Fixed Length 8 con mcm 4 → 4; largos no enteros se redondean al beat.
- [ ] Tests de `plan_bounce`: en curso; grabando; nada marcado y nada sonando; marcados filtrados a los que siguen sonando; sin marcados toma todos los sonando; destino ocupado; destino en pista origen; destino no audio; demasiado largo con FL apagado; FL acorta y pasa.
- [ ] Implementar. Verde.

### Task 3: BounceState y BounceGuard

**Files:** `LaunchpadLooper/BounceState.py`, `LaunchpadLooper/BounceGuard.py`, tests correspondientes

- [ ] `BounceSelection`: release corto sin tocar → `'snapshot'`; release largo sin tocar → None; marcado y release (corto o largo) → None; mark alterna; clear.
- [ ] `BounceJob`: involves_track/row, is_target, flags.
- [ ] `BounceGuard`: cada fila de la matriz 2.3 con job en P1 y en P2; sin job → ALLOW siempre.
- [ ] Implementar. Verde.

### Task 4: Dispatch y SlotColors con modificador `snapshot`

**Files:** `Dispatch.py`, `SlotColors.py`, tests

- [ ] Tests: pad_action('snapshot', PLAYING) → BOUNCE_MARK; EMPTY → BOUNCE_TARGET; STOPPED/RECORDING/TRIGGERED → NONE; lateral_action('snapshot', i) → NONE. slot_color con 'snapshot': PLAYING → Playing; marcado → CopyOrigin/Empty al pulso; STOPPED/EMPTY/RECORDING → Empty. scene_color('snapshot') → Off.
- [ ] Implementar (`slot_color` gana `is_bounce_mark=False`). Verde.

### Task 5: Routing por duck typing

**Files:** `LaunchpadLooper/Routing.py`, `tests/fakes.py` (FakeSong.return_tracks, create_return_track, FakeTrack.input_routings/current_input_routing/current_monitoring_state/has_audio_input/mixer_device.sends, FakeReturnTrack.output_routings/current_output_routing), `tests/test_routing.py`

- [ ] Tests: find_return por nombre; ensure_return crea con nombre y Sends Only cuando falta, no duplica cuando existe, devuelve None si create falla (RuntimeError); input_routing_for acepta `'BOUNCE'`, `'A-BOUNCE'`, `'A BOUNCE'` (índice 0) y rechaza `'DEBOUNCE'` y `'B-BOUNCE'`.
- [ ] Implementar. Verde.

### Task 6: ClipActions bounce

**Files:** `ClipActions.py`, `tests/test_clip_actions.py`

- [ ] Tests: `bounce_start` sube sends de origen a 1.0 y no toca otros, cambia entrada, monitor Off, arma, dispara con `record_length` y `launch_quantization`, devuelve lo guardado; `bounce_restore` repone sends, entrada, monitor y arm; `bounce_start` con RuntimeError al disparar repone y devuelve None; `bounce_cancel` borra el clip si hay, o `stop()` del slot si solo está disparado; `stop_tracks`.
- [ ] Implementar. Verde.

### Task 7: colores y cableado en Live

**Files:** `Colors.py` (Top.SnapshotHeld verde, Top.SnapshotMarked ámbar), `LooperSession.py`, `TopControls.py`

- [ ] `LooperSession`: `_bounce_sel`, `_bounce_job`; `begin_bounce_select(now)`, `end_bounce_select(now)` (foto si corresponde), `on_pad` con guard y acciones BOUNCE_MARK/BOUNCE_TARGET, `_start_bounce(target_component)`, `close_bounce()`, `cancel_bounce(reason)`, `_bounce_tick()` dentro de `_on_tick` (started, último compás → stop orígenes una vez, fin → restore + BOUNCE LISTO, disparo perdido → BOUNCE CORTADO), `on_lateral` con guard, `bounce_in_progress()`, `bounce_started()`, disconnect repone.
- [ ] `TopControls`: Snapshot press → si job: CANCEL/CLOSE según guard; si no: begin select; release → end select. Undo/INIT con job → rechazo. Otros superiores con Snapshot abajo → consumidos. LED de Snapshot mientras está abajo.
- [ ] `py_compile` de los tres, suite completa verde, `__pycache__` limpio, `install.ps1`.

### Task 8: documentación

- [ ] `docs/manual-checklist-launchpad-looper.md`: sección Bounce con los casos de la spec 8.
- [ ] `README-LaunchpadLooper.md`: Snapshot mantenido = bounce; retorno BOUNCE automático.
- [ ] `docs/specs/2026-10-18-launchpad-looper-design.md`: nota en 4.8 que remite a la spec de Bounce.
- [ ] Memoria del proyecto.
