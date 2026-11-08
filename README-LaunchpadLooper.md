# LaunchpadLooper

Script de control para Ableton Live que convierte un Launchpad original (MK1, Launchpad S o Launchpad Mini MK1) en un looper de 8 pistas × 8 escenas, sin modos ni navegación.

Funciona en Live 9, 10, 11 y 12 en Windows. No sirve para Launchpad MK2, Pro, X ni Mini MK3.

## Instalación

1. Cerrar Live.
2. Descomprimir el zip. Adentro hay una carpeta `LaunchpadLooper` con archivos `.py`.
3. Copiar la carpeta `LaunchpadLooper` entera (no los archivos sueltos) dentro de la carpeta `MIDI Remote Scripts` de la versión de Live:

   | Versión | Pegar la carpeta en |
   |---|---|
   | Live 9 | `C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\` |
   | Live 10 | `C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\` |
   | Live 11 | `C:\ProgramData\Ableton\Live 11 Suite\Resources\MIDI Remote Scripts\` |
   | Live 12 | `C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\` |

   Si la edición no es Suite, la carpeta se llama `Live 11 Standard`, `Live 11 Lite`, etc. `ProgramData` es una carpeta oculta: escribir la ruta directo en la barra del Explorador.

   Tiene que quedar así: `...\MIDI Remote Scripts\LaunchpadLooper\LaunchpadLooper.py`, junto a las demás carpetas de scripts (`Launchpad`, `Push`, ...).

   Alternativa para Live 11 y 12, sin permisos de administrador: pegarla en `Documentos\Ableton\User Library\Remote Scripts\` (crear la carpeta `Remote Scripts` si no existe).

4. Si ya había una versión anterior de `LaunchpadLooper`, reemplazar toda la carpeta.
5. Abrir Live. En Opciones > Preferencias > Link/MIDI (en Live 9: MIDI/Sync), en una fila de Superficie de control elegir **LaunchpadLooper**, con entrada y salida **Launchpad**.
6. La barra de estado de Live, abajo a la izquierda, dice `LAUNCHPAD LOOPER OK` y los botones superiores se iluminan.

Para desinstalar: borrar la carpeta `LaunchpadLooper` de `MIDI Remote Scripts` y elegir None en Preferencias.

## Preparar el set

- 8 pistas de audio con la entrada asignada y Monitor en Off (o In si se quiere escuchar el instrumento antes de grabar).
- Cuantización de lanzamiento global en 1 Bar.
- Las 8 primeras escenas se usan como filas. El rectángulo rojo de Live marca el área de 8×8.

## Uso

Grilla: cada pad es un slot de clip. Laterales: escenas. Superiores, de izquierda a derecha:

| Botón | Toque | Mantener |
|---|---|---|
| 1 Undo | deshace | medio segundo: rehace |
| 2 Fixed Length | prende/apaga el largo fijo de grabación | laterales 1–5 eligen 1, 2, 4, 8, 16 compases |
| 3 Quantize | | laterales 1–5 grilla (1/4, 1/8, 1/8t, 1/16, 1/16t), 7–8 cantidad (50 %, 100 %); más pad cuantiza ese clip |
| 4 Delete | | más pad borra el clip; más lateral borra la fila |
| 5 Stop | | más pad de un clip sonando (o de una columna vacía) detiene la pista en el compás; más pad de un clip parado lo lanza en el compás, así el play y el stop salen juntos; más lateral detiene las pistas que suenan en esa fila |
| 6 Copy | | tocar clip origen, luego slots vacíos destino |
| 7 Snapshot | copia los clips que suenan a la fila libre más baja y la nombra SNAP | **bounce**: tocar los clips sonando a fundir (o ninguno = todos) y luego un slot vacío de otra pista; graba la mezcla en tiempo real y al terminar suena el bounce y los originales quedan detenidos. **Gain**: tocar un clip sonando y luego un lateral fija su nivel (1 = +6 dB … 8 = −18 dB) |
| 8 Pulso / Tap | late al tempo; 4 toques seguidos fijan el tempo | medio segundo: metrónomo on/off |

Pads sin modificador: slot vacío arma la pista y graba en el próximo compás; clip detenido lo lanza; clip sonando lo para al instante; clip grabando cierra la grabación en el próximo compás. Al cerrar, la pista se desarma sola. Delete, Stop y Quantize siguen valiendo 150 ms después de soltarlos, así soltar el botón y bajar el pad en el mismo gesto no convierte un borrado en un stop.

INIT: mantener Undo + Fixed Length + Quantize (los tres de la izquierda) más de medio segundo vacía los 64 slots y deja listo el retorno BOUNCE (lo crea si no existe, lo toma si existe, y lo pone en "Sends Only"). Un Undo recupera la grilla; el retorno queda.

INIT solo vale con las manos fuera de la grilla: si mientras está abajo se toca un pad o un lateral, el acorde se cancela y el pad obedece al modificador que bajó primero. Tampoco se arma con un modificador que ya se usó sobre pads o laterales sin soltarlo. Esto protege de los Launchpad MK1 que, con un superior abajo, mandan pulsaciones fantasma de sus vecinos de la derecha (quedan en Log.txt como `rompe acorde`); por eso el setup del bounce dejó de ser Delete + Stop + Copy y pasó a INIT.

Bounce: necesita un retorno llamado BOUNCE con salida "Sends Only". Lo deja listo el INIT del comienzo del set; si no se quiere vaciar la grilla, alcanza con crear a mano un retorno llamado BOUNCE con salida "Sends Only", que el bounce usa tal cual. Sin retorno, el bounce se rechaza con el aviso de hacer INIT. Después, el bounce lo usa como bus: sube los sends de los clips elegidos, pone el retorno como entrada de la pista destino y graba. Al terminar deja todo como estaba. Dura lo que tarden en coincidir los loops elegidos (2 y 3 compases → 6), o lo que diga Fixed Length si es más corto. Mientras graba, tocar el pad destino o Snapshot cierra antes; Delete + pad destino cancela y tira lo grabado. Para volver atrás: Delete sobre el bounce y relanzar los originales.

Gain de clip: con Snapshot mantenido, tocar un clip que suena y después un lateral. Los laterales son una escalera: 1 = +6 dB, 2 = +3, 3 = 0, 4 = -3, 5 = -6, 6 = -12, 7 = -15, 8 = -18. Mientras hay un clip tocado, el lateral de su nivel actual se ve verde y el de 0 dB ámbar tenue. Se puede ir tocando clips y ajustando cada uno; al soltar Snapshot sin tocar un slot vacío no pasa nada más (ni foto ni bounce) y los niveles quedan. Es el Clip Gain de Live, así que el bounce lo captura y Undo lo deshace. Tocar de nuevo un clip ya elegido no lo quita de la selección: para empezar de cero, soltar Snapshot.

Colores de pads: apagado vacío, ámbar tenue detenido, verde sonando, rojo grabando. Parpadeo al pulso: verde por lanzar, rojo por grabar, rojo/verde grabación por cerrar, ámbar/verde o ámbar/rojo stop pendiente.

Cada acción deja un texto en la barra de estado de Live.

## Ajustes

No se guarda nada entre sesiones. Cada vez que carga el script, Fixed Length arranca apagado y en 1 compás, y Quantize en 1/16 al 100 %. Lo que se elija con los laterales vale hasta cerrar Live.

## Si algo falla

Mirar el final de `%APPDATA%\Ableton\Live <versión>\Preferences\Log.txt`. Las líneas que importan dicen `LaunchpadLooper` o `RemoteScriptError`.

## Diagnóstico

Con `DIAG_LOG = True` en `consts.py` (valor por defecto) el script escribe en el `Log.txt` de Live una línea con prefijo `LaunchpadLooper diag:` por cada acción sobre el set: pads y laterales tocados, grabaciones disparadas (con estado del transporte, cuantización, pista y slot), cada paso del bounce (sends, ruteo, monitor, arm, fire) con el valor leído de vuelta, el desarme diferido de pistas, y Undo/Redo con los sends del último bounce antes y después. Sirve para ver qué hacía el script justo antes de un crash de Live o de un send que no volvió a 0. Para apagarlo, poner `DIAG_LOG = False`.

`Log.txt` está en la carpeta de Preferences de Live (por ejemplo `%AppData%\Ableton\Live 11.1.1\Preferences\Log.txt`).
