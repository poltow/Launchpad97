# LaunchpadLooper — Gain de clip con Snapshot mantenido

Fecha: 2026-10-21. Extiende la spec de Bounce (`2026-10-20-launchpad-looper-bounce-design.md`).

## 1. Objetivo

Con Snapshot mantenido, los 8 laterales fijan el gain del clip que se tocó último. Así, mientras se eligen clips para un bounce, se les puede ajustar el nivel; y si después no se toca un slot destino, el gesto sirvió solo para cambiar volúmenes.

El gain es del clip (`Clip.gain`), no de la pista. Va antes de los sends, así que el bounce lo captura.

## 2. Gesto

Snapshot mantenido (modificador `snapshot`):

| Toque | Efecto |
|---|---|
| Pad de clip sonando | Lo marca para bounce si no estaba y lo deja **enfocado**. Si ya estaba marcado, solo cambia el foco. No existe desmarcar uno solo: soltar Snapshot limpia todo. |
| Lateral `i` (0..7) | Fija el gain del clip enfocado en el nivel `i`. Sin clip enfocado: nada, barra "GAIN: TOCAR UN CLIP SONANDO PRIMERO". |
| Pad de slot vacío | Destino del bounce, como hasta ahora. |
| Soltar Snapshot | Toque corto sin haber tocado pads ni laterales = foto. Cualquier otro caso = nada. Marcas y foco se limpian. |

Niveles, de arriba hacia abajo (lateral 1 arriba):

| Lateral | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| dB | +6 | +3 | 0 | -3 | -6 | -12 | -15 | -18 |

Solo clips sonando: bajo Snapshot los clips detenidos se ven vacíos y, tocados, se rechazan como destino ocupado (sin cambios).

Tocar un lateral marca la selección como "tocada" (`note_touch`), igual que un pad.

## 3. LEDs y mensajes

Laterales con Snapshot mantenido:

- Sin clip enfocado: todos apagados (como hoy).
- Con clip enfocado: el lateral del nivel actual del clip en verde fuerte (`Looper.Scene.Playing`); el lateral de 0 dB en ámbar tenue (`Looper.Scene.Stopped`) como referencia, salvo que sea el actual; el resto apagado. Si el gain del clip no coincide con ningún escalón, se marca el más cercano en dB.

Pads: el enfocado parpadea ámbar como cualquier marcado (sin color propio). Botón Snapshot: ámbar en cuanto hay una marca (sin cambios).

Mensajes nuevos en `Messages`:

| Evento | Texto |
|---|---|
| `gain` | `GAIN PISTA %(track)d  ESCENA %(scene)d: %(db)s` con `db` = `gain_display_string` del clip en mayúsculas (por ejemplo "-3.0 DB") |
| `gain_no_focus` | `GAIN: TOCAR UN CLIP SONANDO PRIMERO` |
| `press_snapshot` (cambia) | `SNAPSHOT: SOLTAR = FOTO  /  + CLIPS + SLOT VACIO = BOUNCE  /  + CLIP + LATERAL = GAIN` |

## 4. Cómo se fija el dB

`Clip.gain` es un float 0.0..1.0 y Live no documenta su curva hacia dB; `Clip.gain_display_string` devuelve el texto ("-3.0 dB", "+6.0 dB", "-inf dB"; el separador decimal puede ser coma según el idioma). El script de Push de Live 9 usa exactamente estas dos propiedades, así que existen en 9, 10 y 11.

Calibración: la primera vez en la sesión que se toca un lateral de gain, el script busca por bisección el float de cada uno de los 8 niveles sobre el clip enfocado, leyendo `gain_display_string` tras cada escritura, y guarda la tabla en memoria (`ClipGain.Calibration`). Termina escribiendo el float del nivel pedido. Todo ocurre dentro de `song.begin_undo_step()` / `end_undo_step()`, así que un Undo deshace el toque completo, incluida la calibración. Los toques siguientes usan la tabla y son un paso de Undo normal cada uno.

Bisección: 24 iteraciones por nivel sobre [0.0, 1.0], criterio "el dB leído, redondeado a 0.1, es igual al pedido"; si no converge, se usa el float cuyo dB leído quedó más cerca y se escribe en el log `LaunchpadLooper: gain calib <nivel> aprox`. Si el texto no se puede leer (regex no coincide), toda la calibración se descarta y se usa la tabla aproximada `ClipGain.FALLBACK` (floats fijos), con un aviso en el log. Nunca se lanza una excepción hacia Live.

El nivel actual (para los LEDs) se obtiene del texto en dB del clip, con `nearest_level(db)`; "-inf" cae en el nivel 8 (-18).

## 5. Bounce en curso y rechazos

Sin cambios en `BounceGuard`: con un bounce en curso, bajar Snapshot cancela o cierra el bounce según la fase (spec de Bounce, `top_decision`) y no abre una selección, así que no hay foco ni gain mientras dura. Fuera de un bounce, los laterales bajo `snapshot` llegan a `on_lateral` como hoy y la rama `SET_GAIN` actúa sobre el clip enfocado.

## 6. Arquitectura

Módulo puro nuevo `LaunchpadLooper/ClipGain.py`:

- `LEVELS_DB = (6.0, 3.0, 0.0, -3.0, -6.0, -12.0, -15.0, -18.0)`, `ZERO_INDEX = 2`.
- `FALLBACK` tabla de floats aproximados (se corrige con la primera prueba en Live).
- `parse_db(text) -> float | None` (acepta "+6.0 dB", "-3,0 dB", "-inf dB" → `-inf`).
- `nearest_level(db) -> int`.
- `lateral_color(index, current_index) -> str` (nombres de color de escena).
- `Calibration`: `is_done()`, `calibrate(write, read)` donde `write(float)` y `read() -> str` son callables; devuelve la tabla y una lista de niveles aproximados; `value_for(index)`.

Cambios en módulos existentes:

- `BounceState.BounceSelection`: `mark(key)` ya no alterna, siempre deja marcado y enfoca; `focused() -> key | None`; `clear()` limpia el foco.
- `Dispatch.lateral_action`: `snapshot` → `(SET_GAIN, index)`.
- `SlotColors.scene_color`: bajo `snapshot` recibe `gain_index` (nivel actual o `None`) y delega en `ClipGain.lateral_color`.
- `ClipActions.set_gain(clip, value)` y `ClipActions.calibrate_gain(song, clip, calibration)` (agrupa en un undo step, maneja `RuntimeError` restaurando el float original).
- `Messages`: eventos de la sección 3.
- `LooperSession.on_lateral`: rama `SET_GAIN`; `LooperSession` guarda una `Calibration` por sesión; `scene_color_for` pasa el `gain_index` del clip enfocado cuando el modificador es `snapshot`.
- `tests/fakes.py`: `FakeClip.gain` y `gain_display_string` con una curva simulada (por ejemplo dB = 40·gain − 34, con "-inf dB" en 0.0) y `FakeSong.begin_undo_step/end_undo_step` contando llamadas.

## 7. Pruebas

- `test_clip_gain.py`: `parse_db` (signos, coma, inf, basura), `nearest_level` (exactos, intermedios, -inf), `lateral_color` (actual, cero, resto, actual == cero), `Calibration` con la curva del fake (converge en los 8, `value_for`, tabla aproximada cuando `read` devuelve basura).
- `test_bounce_state.py`: marcar dos veces no desmarca; foco sigue al último toque; `clear` limpia foco.
- `test_dispatch.py`: lateral bajo `snapshot` → `SET_GAIN`.
- `test_slot_colors.py`: laterales bajo `snapshot` con y sin foco.
- `test_clip_actions.py`: `set_gain`, `calibrate_gain` agrupa en un undo step y restaura ante `RuntimeError`.
- `test_messages.py`: los tres textos.
- Manual (checklist): sección nueva "Gain (Snapshot mantenido)".

## 8. Fuera de alcance

Gain de clips detenidos, gain por pista, pasos finos (subir/bajar de a 1 dB), persistencia de la tabla de calibración entre sesiones.
