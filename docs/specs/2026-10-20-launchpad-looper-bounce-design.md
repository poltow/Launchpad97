# LaunchpadLooper · Bounce — diseño

Extiende `docs/specs/2026-10-18-launchpad-looper-design.md`. Todo lo no dicho acá sigue valiendo.

## 1. Qué es

Bounce funde varios clips que están sonando en un clip nuevo, grabado en tiempo real en un slot vacío de otra pista. Al terminar, el clip nuevo suena en loop y los originales quedan detenidos, no borrados. Es el "merge" de un pedal de loops, hecho con el ruteo de Live.

Para qué: liberar pistas y seguir grabando capas encima, conservando los originales por si hay que volver.

## 2. Gesto

Botón superior 7, **Snapshot**, mantenido. El toque corto sigue siendo la foto (spec base 4.8).

| Paso | Acción | Realimentación |
|---|---|---|
| 1 | Bajar Snapshot | Barra: `SNAPSHOT: SOLTAR = FOTO · + CLIPS SONANDO + SLOT VACIO = BOUNCE`. La grilla muestra solo clips sonando (verde) y slots vacíos elegibles (apagados pero activos). Laterales apagados. |
| 2 | Tocar clips sonando (opcional) | Cada uno queda marcado y parpadea al pulso. Tocar uno marcado lo deja marcado y solo cambia el foco del gain (spec `2026-10-21-launchpad-looper-clip-gain-design.md`); no hay desmarcado individual, soltar Snapshot limpia todo. Barra: `BOUNCE: 2 CLIPS ELEGIDOS`. |
| 3 | Tocar un slot vacío | Arranca el bounce (sección 4) con los clips marcados, o con **todos los clips sonando** si no se marcó ninguno. Barra: `BOUNCE 2 CLIPS → PISTA 4 ESCENA 3  (4 COMPASES)`. Snapshot puede soltarse. |

Al soltar Snapshot:

| Duración | Tocó pads | Resultado |
|---|---|---|
| corta, menos de ½ s (`LONG_PRESS`) | no | **foto**, como hoy |
| corta | sí, sin destino | nada; la selección se descarta |
| larga, ½ s o más | no | nada |
| larga | sí, sin destino | nada; la selección se descarta |
| cualquiera | sí, con destino | nada más; el bounce ya arrancó al tocar el destino |

No puede iniciarse un segundo bounce hasta que termine el primero (rechazo).

### 2.1 Arranque y duración

- **Arranque:** al tocar el destino se hace `fire` con la cuantización global de Live, igual que cualquier pad. Con la global en 1 Bar entra en el próximo compás, en fase con lo que suena. El script asume 1 Bar, como el resto del looper.
- **Duración prevista `L`:** mínimo común múltiplo de los largos de los orígenes (4.4), redondeado hacia arriba a compases enteros. Si **Fixed Length está prendido y su largo es menor**, manda Fixed Length: `L = min(mcm, Fixed Length)`. Fixed Length nunca alarga. Si `L` supera 64 compases se rechaza; prender Fixed Length es la forma de acortarlo.
- **Corte anticipado:** mientras graba, un toque corto en **Snapshot**, un toque en el **pad destino**, o **Stop + pad destino** cierran la grabación en el próximo compás. En el mismo instante el script manda el stop a las pistas origen, así que bounce y orígenes conmutan en el mismo compás, igual que en el fin natural.
- **Fin natural:** en el último compás de `L` el script manda el stop a los orígenes; Live corta la grabación y el bounce empieza a sonar en el mismo compás.

### 2.2 Fases

| Fase | Desde | Hasta | Pad destino |
|---|---|---|---|
| **P0 Selección** | bajar Snapshot | tocar destino, o soltar Snapshot | — |
| **P1 Esperando** | tocar destino | el compás en que arranca la grabación | rojo al pulso |
| **P2 Grabando** | arranque | principio del último compás | rojo fijo |
| **P3 Último compás** | principio del último compás, o pedido de corte | fin de la grabación | rojo / verde al pulso; orígenes ámbar / verde |
| **P4 Listo** | fin de la grabación | — | verde; orígenes ámbar tenue; ruteo repuesto |

### 2.3 Matriz de comportamiento

"Rechazo" = parpadeo rojo del botón o pad tocado y mensaje `BOUNCE EN CURSO` (o el indicado). "Normal" = lo que hace hoy sin bounce. "Pista origen" = cualquier pista que tiene un clip origen; "pista destino" = la del bounce.

| Control | P0 Selección (Snapshot abajo) | P1 Esperando | P2 Grabando | P3 Último compás | P4 Listo |
|---|---|---|---|---|---|
| **Snapshot** toque corto | soltar sin pads = foto; con pads = nada | **cancela**: quita el disparo, repone ruteo, orígenes siguen sonando. `BOUNCE CANCELADO` | **cierra** en el próximo compás, orígenes paran con él | nada, ya está cerrando | foto |
| **Snapshot** pulsación larga | nada al soltar | igual que corto | igual que corto | nada | nada |
| **Pad destino** | arranca el bounce si está vacío y es válido | cancela (igual que Snapshot) | cierra (igual que Snapshot) | nada | normal: lo detiene al instante |
| **Pad de un clip origen** | marca (y enfoca para gain) | rechazo | rechazo (pararía lo que se está grabando) | rechazo | normal |
| **Otro pad de una pista origen** (vacío o detenido) | vacío: nada, no es destino válido en pista origen; detenido: rechazo, no elegible | rechazo (lanzaría o grabaría sobre el origen) | rechazo | rechazo | normal |
| **Pad vacío o detenido en pista destino** | vacío: es el destino; detenido: rechazo | rechazo | rechazo | rechazo | normal |
| **Pads de otras pistas** | vacío: posible destino; sonando: marca; detenido/grabando/triggered: rechazo, no elegible | normal (grabar, lanzar, parar) | normal | normal | normal |
| **Lateral** solo | nada | rechazo (lanzaría la fila sobre orígenes y destino) | rechazo | rechazo | normal |
| **Undo / Redo** | ignorado | rechazo (desharía ruteo o arm a mitad) | rechazo | rechazo | normal |
| **Fixed Length** toque | ignorado | normal: alterna; no cambia el bounce en curso, `L` ya está fijado | normal | normal | normal |
| **Fixed Length** mantenido + lateral | ignorado | normal: cambia el valor para el futuro | normal | normal | normal |
| **Quantize** + lateral | ignorado | normal | normal | normal | normal |
| **Quantize** + pad origen | ignorado | rechazo (alteraría el audio que se graba) | rechazo | rechazo | normal |
| **Quantize** + pad de otra pista | ignorado | normal | normal | normal | normal |
| **Delete** + pad destino | ignorado | **cancela**: borra el disparo, repone ruteo | **cancela**: borra lo grabado, repone ruteo, orígenes siguen sonando. `BOUNCE CANCELADO` | igual que P2 | normal: borra el bounce |
| **Delete** + pad origen | ignorado | rechazo | rechazo | rechazo | normal |
| **Delete** + otro pad | ignorado | normal | normal | normal | normal |
| **Delete** + lateral | ignorado | rechazo si la fila contiene un origen o el destino; si no, normal | idem | idem | normal |
| **Stop** + pad destino | ignorado | cancela (igual que Delete + destino, no hay nada grabado) | cierra en el próximo compás, orígenes paran con él | nada | normal |
| **Stop** + pad origen | ignorado | rechazo | rechazo | rechazo | normal |
| **Stop** + otro pad | ignorado | normal | normal | normal | normal |
| **Stop** + lateral | ignorado | rechazo si la fila contiene un origen; si no, normal | idem | idem | normal |
| **Copy** + pads | ignorado | normal; pegar en pistas origen o destino no lanza nada, así que se permite | normal | normal | normal |
| **Pulso** tap tempo | ignorado | normal; cambiar el tempo a mitad afecta por igual a orígenes y bounce, Live graba en beats | normal | normal | normal |
| **Pulso** mantenido, metrónomo | ignorado | normal; el metrónomo no entra al bounce | normal | normal | normal |
| **INIT** (acorde) | ignorado, Snapshot no es parte del acorde | rechazo | rechazo | rechazo | normal |
| **Otro superior bajado con Snapshot abajo** | ignorado hasta soltar Snapshot | — | — | — | — |
| **Clip origen se detiene desde Live** (mouse) | se desmarca solo | el bounce sigue con los que quedan; si no queda ninguno, cancela | sigue grabando lo que suena; se saca de la lista de orígenes a detener | idem | — |
| **Stop del transporte de Live** | selección se descarta | cancela, repone ruteo | la grabación corta donde estaba; se repone ruteo; orígenes ya pararon. `BOUNCE CORTADO` | idem | — |
| **Desconexión del script** | nada | cancela y repone | detiene el slot destino, repone ruteo | idem | — |

Decisiones detrás de la matriz:

- **Todo lo que toque una pista origen o la destino durante P1–P3 se rechaza**, porque un bounce a medias no se puede rehacer sin volver a empezar. Las otras seis pistas quedan libres: se puede seguir grabando y lanzando en ellas, no entran al bounce porque su send a BOUNCE está en cero.
- **Cancelar y cerrar son cosas distintas.** Cancelar (Delete + destino, o Snapshot en P1) tira lo grabado y deja los orígenes sonando. Cerrar (Snapshot, pad destino o Stop + destino en P2) conserva lo grabado hasta ese compás y detiene los orígenes con él.
- **Los laterales se rechazan** en P1–P3 porque lanzar una fila cambia las ocho pistas a la vez. Con un modificador de valores (Fixed Length, Quantize) siguen funcionando porque no lanzan nada.
- **Undo se rechaza** en P1–P3 porque Live registraría como pasos los cambios de ruteo y arm, y deshacerlos a mitad dejaría el bounce grabando silencio.

## 3. Condiciones y rechazos

Rechazo = parpadeo rojo breve del botón Snapshot (o del pad tocado) y mensaje en la barra. La selección se mantiene salvo que se indique.

| Condición | Mensaje |
|---|---|
| Sin clips marcados y nada sonando | `BOUNCE NO: NADA SONANDO` |
| Destino ocupado | `BOUNCE NO: DESTINO OCUPADO` (parpadea el pad) |
| Destino en la misma pista que un clip origen (marcado, o sonando si no se marcó nada) | `BOUNCE NO: DESTINO EN PISTA DE ORIGEN` |
| Destino en pista que no es de audio | `BOUNCE NO: DESTINO NO ES PISTA DE AUDIO` |
| Alguna pista grabando (cualquiera de las 8) | `BOUNCE NO: HAY PISTA GRABANDO` |
| Ya hay un bounce en curso | `BOUNCE NO: YA HAY UNO EN CURSO` |
| Largo calculado mayor a 64 compases (con Fixed Length apagado o mayor) | `BOUNCE NO: LARGO MAYOR A 64 COMPASES, USAR FIXED LENGTH` |
| Cualquier control de la matriz 2.3 marcado como rechazo | `BOUNCE EN CURSO` |
| La pista destino no ofrece el retorno como entrada | `BOUNCE NO: SIN ENTRADA DESDE RETORNO` |
| No existe el retorno BOUNCE (falta el acorde de setup, 4.1) | `BOUNCE NO: SIN RETORNO BOUNCE, MANTENER DELETE+STOP+COPY` |

Un clip marcado que deja de sonar antes de tocar el destino se desmarca solo.

## 4. Ruteo y secuencia

### 4.1 Retorno BOUNCE

El script usa un retorno llamado exactamente `BOUNCE`. Se prepara con un acorde, una vez por set:

**Delete + Stop + Copy mantenidos más de ½ s** (los tres superiores del medio, 4-5-6; INIT es 1-2-3, sin botones en común; ninguno de los tres hace nada por sí solo, así que no hay efectos colaterales si se baja uno primero). Mientras cualquier acorde está abajo, pads y laterales se ignoran.

- Si el retorno existe, lo toma y le asegura la salida en `Sends Only`. Mensaje: `BOUNCE SETUP: RETORNO BOUNCE LISTO (SENDS ONLY)`.
- Si no existe, lo crea (`create_return_track`), lo nombra `BOUNCE`, salida `Sends Only`. Mensaje: `BOUNCE SETUP: RETORNO BOUNCE CREADO (SENDS ONLY)`.
- Mientras se cuenta el medio segundo: `BOUNCE SETUP: MANTENER 1/2 SEG`. Soltar antes cancela y los tres botones no hacen su función normal.
- Si Live no puede crearlo (límite de 12 retornos): `BOUNCE SETUP: NO SE PUDO CREAR EL RETORNO`.

El bounce no crea nada solo: sin retorno `BOUNCE` se rechaza con `BOUNCE NO: SIN RETORNO BOUNCE, MANTENER DELETE+STOP+COPY`. El retorno nunca se borra; si el usuario lo renombra, el acorde crea otro.

### 4.2 Lo que se guarda antes de empezar

Para poder reponer todo al terminar, pase lo que pase:

- Por cada pista origen: el valor del send hacia BOUNCE.
- Del destino: entrada actual (`current_input_routing`), canal de entrada, estado de arm, monitor.

### 4.3 Secuencia

1. Guardar el estado (4.2).
2. Sends de las pistas origen hacia BOUNCE a 0 dB (valor 1.0). Las demás pistas no se tocan.
3. Destino: entrada = retorno BOUNCE (la cadena de `input_routings` que corresponde al retorno), monitor Off, arm. La pista se marca como "armada por el script".
4. `fire(record_length=L, launch_quantization=actual)` en el slot destino, igual que una grabación con largo fijo. Entra en el próximo compás, en fase con lo que suena.
5. Durante el último compás de la grabación (lo detecta `FixedLengthTracker`): `stop_all_clips()` en cada pista origen. Con cuantización de 1 compás, el stop cae justo cuando el bounce empieza a sonar.
6. Cuando el clip destino deja de grabar: reponer sends, entrada, monitor y arm (4.2), desarmar, y mensaje `BOUNCE LISTO`.

En un cierre anticipado (2.1) el script manda el stop a los orígenes en el mismo instante que el cierre, así que conmutan en el mismo compás. En una cancelación (2.3) no se detiene ningún origen.

### 4.4 Largo

`L` en beats = mínimo común múltiplo de los largos de los clips origen, redondeados al beat, y luego redondeado hacia arriba a compases enteros. Ejemplos en 4/4: 2 y 4 compases → 4; 2 y 3 → 6; 1, 2 y 8 → 8; 1,5 y 2 → 6; medio compás solo → 1. Un clip sin loop usa su largo total. Con Fixed Length prendido, `L = min(mcm, Fixed Length)`. Tope: 64 compases; si el resultado lo supera se rechaza.

### 4.5 Reposición ante fallas

Cualquier `RuntimeError` de la API durante los pasos 2–4 repone lo guardado y rechaza con `BOUNCE NO: ERROR DE LIVE (ver Log)`. La desconexión del script con un bounce en curso repone lo guardado antes de salir. La reposición se hace fuera de notificaciones de Live, con una tarea diferida, como el desarme actual.

### 4.6 Deshacer un bounce

El script no agrupa nada en pasos de Undo para el bounce, porque una grabación en tiempo real no puede quedar dentro de un `begin_undo_step` y partirla en dos pasos confunde. El camino de vuelta es manual y predecible: **Delete + pad** sobre el clip bounceado lo borra, y los originales, que quedaron detenidos y guardados, se relanzan con su pad o con el lateral de su fila. Undo sigue existiendo para todo lo demás; sobre un bounce puede deshacer de a uno los cambios que Live haya registrado (sends, ruteo, el clip), pero no se promete nada sobre ese orden.

## 5. LEDs

Con Snapshot mantenido:

| Elemento | Color |
|---|---|
| Clip sonando no marcado | verde |
| Clip marcado | ámbar / apagado al pulso (como el origen de Copy) |
| Slot vacío | apagado, elegible |
| Clip detenido, grabando o triggered | apagado, no elegible |
| Laterales | apagados |
| Botón Snapshot | verde fijo sin marcados, ámbar fijo con marcados; el arcoíris se detiene mientras está abajo |

Durante el bounce, sin modificador: el destino pasa por rojo al pulso (esperando), rojo (grabando), rojo / verde (último compás), verde (sonando). Los orígenes, en el último compás, ámbar / verde al pulso (stop pendiente) y luego ámbar tenue (detenidos).

## 6. Arquitectura

| Módulo | Responsabilidad |
|---|---|
| `BouncePlanner.py` (puro, nuevo) | Validación de origen y destino sobre una vista de la grilla, cálculo del largo (mcm con tope), razón de rechazo. Sin Live. |
| `BounceState.py` (puro, nuevo) | Selección mientras Snapshot está abajo: marcar (sin alternar), foco para gain, limpiar, `touched()` y duración de la pulsación para decidir foto o nada al soltar. |
| `Routing.py` (Live, nuevo) | Búsqueda o creación del retorno BOUNCE; resolución de la cadena de `input_routings` que corresponde al retorno (comparando nombres sin espacios ni guiones, porque Live muestra `A-Return` para un retorno llamado `A Return`); índice del send. |
| `ClipActions.py` | `bounce_start(origins, target_slot, length, return_index, routing_string)` que guarda estado, rutea, arma y dispara; `bounce_restore(saved)`; `stop_tracks(tracks)`. |
| `LooperSession.py` | Modo Snapshot mantenido (colores y `on_pad`), inicio del bounce, seguimiento con `FixedLengthTracker` para el stop de orígenes en el último compás, reposición diferida al terminar o al desconectar. |
| `TopControls.py` | Snapshot: al bajar entra al modo y anota la hora; al soltar, foto solo si fue corto y no se tocó nada; en cualquier otro caso descarta la selección. Color del botón. |
| `Messages.py` | Textos nuevos de la sección 2 y 3. |

Estado de un bounce en curso: `(destino, orígenes, estado guardado)`; uno solo a la vez.

## 7. API de Live 9 usada

Verificada en los menús de Live 9 (capturas del 2026-10-20): una pista de audio ofrece `A-Return` en "Audio From"; un retorno ofrece `Sends Only` en "Audio To".

- `song.return_tracks`, `song.create_return_track()`.
- `track.name`, `track.has_audio_input`, `track.can_be_armed`, `track.arm`.
- `track.input_routings` (lista de cadenas), `track.current_input_routing` (cadena), `track.current_monitoring_state` (0 In, 1 Auto, 2 Off).
- `return_track.output_routings`, `return_track.current_output_routing`.
- `track.mixer_device.sends[i].value` (0.0 a 1.0, 1.0 = 0 dB), `i` = índice del retorno en `song.return_tracks`.
- `clip.length`, `clip.looping`, `clip_slot.fire(record_length=, launch_quantization=)`, `track.stop_all_clips()`.

Riesgo conocido: el texto exacto que Live 9 usa en `input_routings` para un retorno llamado `BOUNCE`. Se resuelve por comparación normalizada y, si no hay coincidencia, rechazo con mensaje; el log escribe la lista completa para ajustar.

## 8. Pruebas

- **Unitarias**: `BouncePlanner` (rechazos de la sección 3, "todos los sonando" sin marcados, mcm con tope, largos no enteros), `BounceState` (marcar sin alternar, foco, limpiar, touched, corto/largo al soltar), `ClipActions.bounce_start/bounce_restore` con los fakes (sends a 1.0 y repuestos, ruteo cambiado y repuesto, arm, fire con el largo, reposición ante `RuntimeError` a mitad), `Messages`.
- **Manual en Live 9**: agregar a la checklist: bounce de 2 clips de 2 y 4 compases a una pista vacía, verificar que entra en el compás, que el bounce suena y los originales paran en el mismo compás, que sends y entrada vuelven a como estaban, que el retorno BOUNCE se creó una sola vez, bounce de todo lo que suena sin marcar, toque corto = foto y pulsación larga sin pads = nada, cierre anticipado, cancelación con Delete, cada rechazo de la sección 3, vuelta atrás con Delete + relanzar originales, desconexión a mitad de bounce.

## 9. Fuera de alcance

Bounce con niveles distintos por pista (los sends van siempre a 0 dB), bounce de filas enteras, borrar originales automáticamente, más de un bounce simultáneo.
