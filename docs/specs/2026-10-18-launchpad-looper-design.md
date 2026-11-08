# LaunchpadLooper — Diseño

Fecha: 2026-10-18
Estado: aprobado en conversación, pendiente de revisión escrita

## 1. Objetivo

Script de control surface para Ableton Live 9 y 10 (Python 2.7, `_Framework`) que convierte un Novation Launchpad MK1 (Launchpad, Launchpad S, Launchpad Mini) en un controlador de **live looping de audio**. Deriva de la lógica de Pro Session de Launchpad95 pero es un script nuevo, autocontenido, instalado en una carpeta propia llamada `LaunchpadLooper`. Launchpad95 queda intacto.

Alcance fijo: las **primeras 8 pistas** por las **primeras 8 escenas** del set. No hay navegación, modos ni páginas. El usuario acomoda el set para que lo que quiere controlar esté ahí.

Fuera del script: stop, mute y solo por pista y sus variantes "todos" se manejan desde otro controlador (Korg nanoKONTROL2) o desde Live. Monitoreo se resuelve en Live con pistas en Monitor Off o pistas no controladas por el script. La cuantización de lanzamiento del set se asume en **1 compás** y el script no la cambia salvo de forma transitoria para el stop inmediato (ver 4.1).

## 2. Hardware y mapa

```
        [1][2][3][4][5][6][7][8]        <- superiores (CC 104-111)
   (1)  [ ][ ][ ][ ][ ][ ][ ][ ]        <- fila 1 = escena 1
   (2)  [ ][ ][ ][ ][ ][ ][ ][ ]
   ...
   (8)  [ ][ ][ ][ ][ ][ ][ ][ ]        <- fila 8 = escena 8
         ^ columnas = pistas 1-8          (n) = laterales = escenas
```

| Superior | Función | Gesto |
|---|---|---|
| 1 | Undo / Redo | toque: undo; mantener 0,5 s o más: redo |
| 2 | Fixed Length | toque: alterna; mantener: laterales muestran largos |
| 3 | Quantize | mantener: laterales muestran resolución y cantidad; más pad aplica |
| 4 | Delete | mantener más pad o lateral |
| 5 | Stop | mantener más pad o lateral |
| 6 | Copy | mantener más pad origen más pads destino |
| 7 | Snapshot | toque: foto; mantener más pads y slot vacío: bounce; mantener más pad y lateral: gain del clip |
| 8 | Pulso / Tap | taps: tempo; mantener 0,5 s o más: metrónomo |

Laterales 1–8: escenas 1–8. Grilla: slots de clip.

LEDs del MK1: rojo, ámbar y verde en dos intensidades; parpadeo de hardware (color/apagado, ritmo fijo) y parpadeo por software con el tic de 100 ms del `ControlSurface`.

## 3. Comportamiento de los pads (sin modificador)

| Estado del slot | Toque |
|---|---|
| Vacío | arma la pista (sin desarmar otras) y dispara la grabación. Con Fixed Length prendido, graba el largo elegido y cierra solo. |
| Clip detenido | lanza desde el principio, entra en el próximo compás |
| Clip sonando | detiene **de inmediato** (4.1) |
| Clip grabando | cierra la grabación en el próximo compás y el clip queda sonando |

Reglas:

- **Autorecord acumulativo**: el script arma la pista escribiendo `track.arm` directamente, sin aplicar el armado exclusivo de Live, para que arrancar una segunda grabación no desarme la primera. Dos slots vacíos tocados dentro del mismo compás arrancan juntos.
- **Desarme al cerrar**: cuando una grabación termina y el clip pasa a sonar (o se detiene), el script desarma esa pista. Se detecta con los listeners de `playing_status` / `is_recording` del slot.
- Un slot con clip detenido en una pista que está sonando otro clip: lanza el nuevo, Live detiene el anterior en el compás (comportamiento normal).

## 4. Funciones

### 4.1 Stop inmediato de un clip sonando

Secuencia atómica: guardar `song.clip_trigger_quantization`, ponerla en `q_no_q`, `clip_slot.stop()`, restaurar el valor guardado. Siempre se restaura el valor que había, sea cual sea.

### 4.2 Undo / Redo (superior 1)

- Toque corto (soltar antes de 0,5 s): `song.undo()` al soltar.
- Mantener 0,5 s o más: `song.redo()` una vez al cumplirse el tiempo; al soltar no hace nada más.
- Si forma parte del acorde de INIT (4.9) no ejecuta ninguna de las dos.

### 4.3 Fixed Length (superior 2)

- Al bajar el botón, los laterales pasan de inmediato a mostrar los largos. Si se suelta sin haber tocado ningún lateral, alterna prendido/apagado (no persistente: cada vez que carga el script arranca apagado). Si se tocó un lateral, al soltar no alterna.
- Mientras se mantiene: los laterales 1–5 muestran 1, 2, 4, 8 y 16 compases; el elegido fuerte, los demás tenues; laterales 6–8 apagados. Tocar uno lo selecciona (vale hasta cerrar Live; al cargar vuelve a 1 compás) sin cambiar el estado prendido/apagado. Al soltar, los laterales vuelven a escenas.
- Implementación: al disparar una grabación con Fixed Length prendido se usa el mecanismo de grabación de largo fijo de Live con el valor elegido (como hace Pro Session hoy); apagado, la grabación es abierta.
- LED: titila (hardware) prendido, verde tenue apagado.

### 4.4 Quantize (superior 3)

- Mantener: laterales 1–5 muestran resolución 1/4, 1/8, 1/8t, 1/16, 1/16t; lateral 6 apagado; laterales 7–8 muestran cantidad 50% y 100%. El valor elegido fuerte, el resto tenue. Tocar selecciona (vale hasta cerrar Live; al cargar vuelve a 1/16 al 100%).
- Mantener más pad con clip: `clip.quantize(resolución, cantidad)` con cantidad 0,5 o 1,0. Funciona con clips de audio (warp markers) y MIDI.
- Mantener más pad vacío: nada. Mantener más lateral: solo selección de valores, nunca cuantiza filas.

### 4.5 Delete (superior 4)

- Mantener más pad con clip: borra el clip. Si está grabando, cancela la grabación y deja el slot vacío.
- Mantener más lateral N: borra los clips de los 8 slots de la fila N y, si la escena se llama "SNAP", le quita el nombre. Un paso de Undo (`begin_undo_step` / `end_undo_step`).
- Mientras se mantiene, todos los slots con clip se ven rojo fuerte; los laterales de filas con algún clip, rojo.
- Mantener más pad vacío: nada.

### 4.6 Stop (superior 5)

- Mientras se mantiene, la grilla se ve como siempre (parado ámbar tenue, sonando verde, grabando rojo, lanzado verde al pulso). Los laterales de filas con algún clip sonando o grabando se encienden; el resto apagado.
- Mantener más pad de una columna sin clip, o con clip sonando, grabando o por lanzar: detiene la pista al próximo compás (`track.stop_all_clips()`, equivalente al botón de stop de pista). Si la pista está grabando, la grabación cierra en el compás y queda detenida.
- Mantener más pad de un clip parado: lo lanza al próximo compás con la cuantización del set (`clip_slot.fire()`, igual que sin modificador); si en esa pista sonaba otro clip, lo reemplaza. Así, con Stop mantenido se toca un clip parado y el pad de otra pista sonando y el play y el stop salen en el mismo compás.
- Mantener más lateral N: para cada pista cuyo clip sonando o grabando está en la fila N, detiene la pista al próximo compás. Pistas sonando clips de otras filas no se tocan.
- Varios laterales en secuencia o simultáneos: cada pedido entra en Live al llegar; todos los que entran antes del próximo compás paran juntos.
- Stop solo, sin pad ni lateral: nada. No hay doble toque ni combinaciones.
- Realimentación: el clip con stop pendiente alterna al pulso ámbar/verde si sonaba, ámbar/rojo si grababa.

Para detener todo en el mismo compás también sirve lanzar una fila vacía (sus slots tienen botón de stop).

### 4.7 Copy (superior 6)

- Mantener, tocar un pad con clip: queda marcado como origen (parpadea). Tocar pads vacíos: en cada uno se pega una copia (`ClipSlot.duplicate_clip_to`). Varios destinos mientras no se suelte.
- Destino ocupado: rechazo (parpadeo rojo del pad destino), no se pisa.
- Tocar otro pad con clip mientras hay origen: lo reemplaza como origen.
- Soltar Copy: limpia el origen. Copy más lateral: nada. Solo clips, no filas.

### 4.8 Snapshot (superior 7)

Toque corto: foto (abajo). Mantenido con pads: bounce, ver `2026-10-20-launchpad-looper-bounce-design.md`. Mantenido, pad de clip sonando y laterales: gain de ese clip en 8 niveles, ver `2026-10-21-launchpad-looper-clip-gain-design.md`. Desde esas specs, Snapshot es un modificador más y la foto solo se hace con un toque de menos de ½ s sin tocar pads ni laterales.

Toque corto:

1. Si alguna de las 8 pistas está grabando: rechazo, no hace nada.
2. Buscar, desde la fila 8 hacia la fila 1, la primera fila cuyos 8 slots estén vacíos. Si no hay: rechazo.
3. Para cada pista con un clip sonando en la ventana 8×8: copiar ese clip al slot de esa pista en la fila elegida. Pistas detenidas o vacías: no se copia nada; el slot queda vacío con botón de stop.
4. Renombrar la escena a "SNAP".
5. Todo en un paso de Undo.

Los originales no se tocan. Relanzar la foto es tocar su lateral: entra en el compás, los clips arrancan desde el principio y las pistas sin clip en la fila se detienen. Borrar la foto es Delete más lateral (4.5). Las SNAP se acumulan de abajo hacia arriba; cuando no queda fila vacía, Snapshot se rechaza.

LED: ciclo lento por software rojo, ámbar, verde (un cambio por segundo aproximadamente). Rechazo: parpadeo rojo breve.

### 4.9 INIT

Acorde: superiores 1, 2 y 3 (Undo, Fixed Length, Quantize) mantenidos **juntos** más de 0,5 s.

- Mientras los tres estén abajo, ninguno ejecuta su función propia; al soltar tampoco (ni undo ni cambio de Fixed Length).
- Al cumplirse el tiempo: borra los clips de los 64 slots de la ventana y quita el nombre "SNAP" de las escenas 1–8. No toca pistas, escenas ni nada fuera de la ventana. Un solo paso de Undo.
- Realimentación: durante la cuenta la grilla parpadea roja al pulso; al ejecutarse queda apagada.

### 4.10 Pulso / Tap tempo / Metrónomo (superior 8)

- Reposo: late al tempo de la canción leyendo la posición en el tic de 100 ms: tenue en cada negra, fuerte en el primer tiempo del compás. Verde con metrónomo apagado, ámbar con metrónomo prendido.
- Tap: cada toque corto registra una marca de tiempo. Si pasan más de **2 s** desde el toque anterior, la cuenta se reinicia. A partir del **cuarto** toque consecutivo, tempo = 60 / promedio de los intervalos, escrito en `song.tempo`, y se recalcula con cada toque adicional. Con menos de 4 toques no se cambia nada. Mientras hay cuenta en curso, el LED responde al toque en lugar del pulso. No se usa `song.tap_tempo()` porque arranca la reproducción.
- Mantener 0,5 s o más: alterna `song.metronome`. No cuenta como tap.
- Límite: tempos tapeables desde 30 BPM (ventana de 2 s).

### 4.11 Escenas (laterales solos)

Toque: `song.scenes[n].fire()`. LED: verde si la fila tiene algún clip sonando (aunque haya otros parados), ámbar tenue (como un clip detenido) si solo tiene clips parados, apagado si la fila está vacía. El nombre SNAP no cambia el color.

## 5. Colores

### Slots

| Estado | Color |
|---|---|
| Vacío | apagado |
| Clip detenido | ámbar tenue |
| Sonando | verde fuerte |
| Grabando | rojo fuerte |
| Lanzado, esperando el compás | verde al pulso |
| Esperando para grabar | rojo al pulso |
| Grabando, por pasar a reproducir en el próximo compás | rojo / verde al pulso |
| Stop pendiente, sonaba | ámbar / verde al pulso |
| Stop pendiente, grababa | ámbar / rojo al pulso |

"Grabando, por pasar a reproducir" cubre dos casos: se volvió a tocar el pad de una grabación (cierre manual, Live la marca como disparada) y el último compás de una grabación con Fixed Length (el script cuenta los compases desde que empezó a grabar). Si además hay un stop pendiente, gana ámbar / rojo.

"Al pulso" = parpadeo por software sincronizado a la negra de la canción. Con Delete mantenido: clips rojo fuerte. Con Stop mantenido: la grilla se ve igual que sin modificador. Con Copy mantenido: origen parpadeando.

### Superiores

| Botón | Reposo | Activo |
|---|---|---|
| Undo | verde tenue sin nada que deshacer; verde fuerte con Undo disponible; verde/lima al pulso si además hay Redo; lima solo con Redo | ámbar fuerte mientras se mantiene |
| Fixed Length | naranja tenue (apagado) | naranja parpadeando por hardware del Launchpad (prendido); no depende del pulso, así se ve también con el transporte parado |
| Quantize | amarillo | igual |
| Delete | rojo fuerte | igual |
| Stop | ámbar fuerte | igual |
| Copy | mandarina | igual |
| Snapshot | arcoíris ida y vuelta rojo → verde → rojo, un paso cada 300 ms (ciclo de 3,6 s) | parpadeo rojo si se rechaza |
| Pulso | verde latiendo | ámbar latiendo con metrónomo |

Rechazo de cualquier función: parpadeo rojo breve del botón tocado.

## 6. Ajustes

Nada se guarda en disco. Cada vez que carga el script arranca con estos valores; lo elegido con los laterales vale hasta cerrar Live o cambiar de script:

| Clave | Valores | Al cargar |
|---|---|---|
| fixed_length_on | true/false | false |
| fixed_length_bars | 1, 2, 4, 8, 16 | 1 |
| quantize_grid | 1/4, 1/8, 1/8t, 1/16, 1/16t | 1/16 |
| quantize_amount | 0.5, 1.0 | 1.0 |

## 7. Arquitectura

Carpeta `LaunchpadLooper` junto a `Launchpad95` en `MIDI Remote Scripts` de Live 9 y Live 10. Autocontenida: copia (no importa) de Launchpad95 el botón configurable, la skin/colores y el log.

| Módulo | Responsabilidad |
|---|---|
| `LaunchpadLooper.py` | `ControlSurface`: crea 64 pads, 8 laterales, 8 superiores, skin, tic de 100 ms, conecta componentes. Sin lógica musical. |
| `LooperSession.py` | `SessionComponent` fija en offset (0,0), 8×8. Comportamiento del pad según estado y modificador, desarme al cerrar grabación, colores de slots y laterales, parpadeos al pulso. |
| `Modifiers.py` | Estado de los superiores: cuál está mantenido, Undo corto / Redo largo, acorde de INIT, filas de valores en laterales para Fixed Length y Quantize, Pulso/Tap/metrónomo. |
| `ClipActions.py` | Operaciones puras sobre la API: stop inmediato, borrar clip/fila, copiar, cuantizar, stop de pista/fila en sync, INIT, todas con agrupación de Undo donde corresponde. |
| `Snapshot.py` | Búsqueda de fila libre, copia de lo que suena, nombre SNAP, rechazos. |
| `FixedLengthTracker.py` | Sigue cada grabación disparada con Fixed Length: compás de inicio y largo, para marcar su último compás. |
| `TapTempo.py` | Marcas de tiempo, ventana 2 s, mínimo 4, cálculo y escritura del tempo, latido del LED. |
| `Settings.py` | Valores de Fixed Length y Quantize con validación. Solo en memoria. |
| `Colors.py`, `ConfigurableButtonElement.py`, `Log.py` | Copias adaptadas de Launchpad95. |

Prioridad de modificadores: si hay más de un superior mantenido (fuera del acorde de INIT), vale el primero que bajó; los demás se ignoran hasta soltar.

Desconexión: cada componente libera listeners y encadena al `disconnect` de su base, como se verificó en Launchpad95.

## 8. Pruebas

- **Unitarias (Python 2.7, unittest)** contra un Live simulado mínimo: búsqueda de fila para Snapshot, promedio de taps y reinicio de ventana, máquina de estados de modificadores (corto/largo, acorde INIT, prioridad), mapa de colores por estado, lectura/escritura de Settings.
- **Manual en Live 9 y 10**, lista de verificación gesto por gesto: cada fila de las tablas de la sección 4, más: dos grabaciones simultáneas arrancan juntas y se desarman por separado; stop inmediato no deja la cuantización cambiada; Snapshot con pista grabando se rechaza; INIT es un solo Undo; LEDs al pulso siguen un cambio de tempo.

## 9. Fuera de alcance

Navegación, otros modos de Launchpad95, Shift, Duplicate, Double, grabación de sesión, Arm manual, tempo +/−, nudge, mute/solo/stop por pista, Copy de filas, páginas de Setup, soporte MK2/RGB, Python 3.
