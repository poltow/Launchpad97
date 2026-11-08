# LaunchpadLooper — verificación manual en Live

Preparación: set con 8 pistas de audio con entrada asignada y Monitor Off, 8 escenas vacías, cuantización de lanzamiento en 1 Bar, LaunchpadLooper elegido en Preferencias > MIDI con entrada y salida del Launchpad. Repetir en Live 9 y Live 10.

## Arranque
- [ ] Al cargar, la grilla queda apagada, los laterales apagados, los superiores con sus colores (Undo verde tenue en un set recién abierto, Fixed Length naranja tenue, Quantize amarillo, Delete rojo, Stop ámbar, Copy mandarina, Snapshot en arcoíris continuo, Pulso latiendo en verde). La barra de estado de Live dice "LAUNCHPAD LOOPER OK".
- [ ] El rectángulo rojo de Live cubre pistas 1–8 y escenas 1–8.
- [ ] Con Play, el botón Pulso late en cada negra y más fuerte en el uno, clavado con el metrónomo de Live (sin retraso visible).
- [ ] Cada acción deja un texto en la barra de estado de Live (abajo a la izquierda): grabar, lanzar, stop, borrar, copiar, escena, ajustes, Undo/Redo, tap, metrónomo, snapshot, INIT.
- [ ] Al cambiar algo desde la pantalla de Live (lanzar o borrar clips con el mouse), el Launchpad refleja el cambio en todos los pads y laterales.

## Pads
- [ ] Slot vacío: parpadea rojo al pulso hasta el compás, luego rojo fijo grabando; la pista se armó. Al tocar de nuevo alterna rojo y verde al pulso hasta el próximo compás, queda verde y la pista se desarma.
- [ ] Fixed Length prendido en 2 compases: el primer compás rojo fijo, el segundo alterna rojo y verde al pulso, la grabación cierra sola a los 2 compases, pista desarmada. Con 4 compases el aviso aparece recién en el cuarto.
- [ ] Fixed Length en 1 compás: alterna rojo y verde desde que empieza a grabar.
- [ ] Clip detenido: parpadea verde al pulso y entra en el compás.
- [ ] Laterales: fila con solo clips parados se ve ámbar tenue; con algún clip sonando, verde; fila vacía, apagado.
- [ ] Clip sonando: se detiene al instante. La cuantización de lanzamiento de Live sigue en 1 Bar.
- [ ] Dos slots vacíos en pistas distintas tocados dentro del mismo compás arrancan juntos y se desarman cada uno al cerrar.
- [ ] Pista ya armada a mano: grabar no la desarma al terminar.
- [ ] Después de varias grabaciones, `Log.txt` no tiene "Changes cannot be triggered by notifications".

## Undo / Redo
- [ ] Toque corto deshace. Mantener medio segundo rehace y al soltar no deshace.
- [ ] LED: verde tenue sin historial; verde fuerte tras una acción; tras un Undo alterna verde y lima al pulso (hay Undo y Redo); tras deshacer todo queda lima.

## Fixed Length
- [ ] Toque corto alterna; prendido el LED parpadea naranja (parpadeo propio del Launchpad, sigue con el transporte parado), apagado queda naranja tenue fijo.
- [ ] Al bajar cualquier superior aparece de inmediato su texto en la barra de estado (por ejemplo "FIXED LENGTH  LATERALES = COMPASES"); al soltar o al actuar, el texto de lo hecho. El estado sobrevive a cerrar y abrir Live.
- [ ] Mantener: laterales 1–5 muestran 1, 2, 4, 8, 16, el elegido fuerte. Tocar uno lo cambia; al soltar el estado no cambió.

## Quantize
- [ ] Mantener: laterales 1–5 resoluciones, 6 apagado, 7–8 cantidades. Elegir 1/8 y 50%.
- [ ] Quantize más pad con clip de audio: los warp markers se mueven la mitad hacia la grilla de 1/8.

## Delete
- [ ] Mantener: clips rojos, filas con clips rojas. Más pad borra. Más pad grabando cancela y deja vacío, pista desarmada.
- [ ] Más lateral de una fila: borra sus 8 clips y el nombre SNAP; un solo Undo lo recupera todo.

## Stop
- [ ] Mantener: la grilla se ve como siempre (parados ámbar tenue, sonando verde); laterales prendidos solo en filas con clips sonando.
- [ ] Más pad de un clip parado: parpadea verde al pulso y arranca en el compás; si en esa pista sonaba otro clip, lo reemplaza. Tocar un clip parado y el pad de otra pista sonando: el play y el stop salen en el mismo compás.
- [ ] Más pad de columna sonando: alterna ámbar/verde al pulso y para en el compás. Más pad de columna grabando: ámbar/rojo y queda detenida; también si esa grabación ya alternaba rojo/verde.
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

## Bounce (Snapshot mantenido)
Preparación: dos clips sonando en pistas 1 y 2, de 2 y 4 compases. Pista 5 vacía. Sin retorno BOUNCE en el set.
- [ ] Sin retorno BOUNCE, intentar un bounce: parpadeo rojo y "BOUNCE NO: SIN RETORNO BOUNCE, MANTENER DELETE+STOP+COPY".
- [ ] Mantener Delete + Stop + Copy: barra "BOUNCE SETUP: MANTENER 1/2 SEG"; a los ½ s aparece el retorno BOUNCE con salida Sends Only y la barra dice "RETORNO BOUNCE CREADO". Soltar antes de ½ s: nada. Tocar pads o laterales mientras el acorde está abajo: nada (ni borra, ni para, ni copia).
- [ ] Repetir el acorde con el retorno ya creado: "RETORNO BOUNCE LISTO", no aparece otro retorno. Si se le cambió la salida a Master, vuelve a Sends Only.
- [ ] Bajar Snapshot: barra "SNAPSHOT: SOLTAR = FOTO / + CLIPS SONANDO + SLOT VACIO = BOUNCE"; grilla muestra solo los dos clips sonando, laterales apagados, botón Snapshot verde fijo.
- [ ] Tocar el clip de pista 1: parpadea ámbar, botón Snapshot ámbar, barra "BOUNCE: 1 CLIPS ELEGIDOS". Tocarlo otra vez lo deja marcado (solo cambia el foco del gain); para desmarcar, soltar Snapshot y empezar de nuevo.
- [ ] Marcar los dos y tocar slot vacío de pista 5: barra "BOUNCE 2 CLIPS -> PISTA 5 ESCENA n (4 COMPASES)"; sends de pistas 1 y 2 a BOUNCE al máximo; pista 5 con entrada "A-BOUNCE" (o similar), monitor Off, armada; pad destino rojo al pulso.
- [ ] En el compás arranca a grabar (rojo). En el 4.º compás el pad alterna rojo/verde y los clips origen ámbar/verde.
- [ ] Al terminar: el bounce suena verde, los dos originales quedan ámbar tenue, sends vuelven a cero, entrada de pista 5 vuelve a Ext. In, desarmada. Barra "BOUNCE LISTO". El bounce suena igual que sonaban los dos juntos.
- [ ] Snapshot mantenido y tocar slot vacío sin marcar nada: bouncea todo lo que suena.
- [ ] Toque corto de Snapshot sin tocar pads: foto. Pulsación de 1 s sin pads: nada. Marcar y soltar sin destino: nada, sin foto.
- [ ] Durante el bounce: tocar el pad destino cierra en el próximo compás y los originales paran con él, barra "BOUNCE: CIERRA EN EL COMPAS". Lo mismo con toque corto de Snapshot y con Stop + pad destino.
- [ ] Durante el bounce: Delete + pad destino cancela, el clip se borra, los originales siguen sonando, ruteo repuesto, barra "BOUNCE CANCELADO". Antes del compás de arranque, el pad destino o Snapshot también cancelan.
- [ ] Durante el bounce: pads de pistas 1, 2 y 5 (cualquier slot), laterales solos, Undo, Delete/Stop + lateral de una fila con origen, INIT: parpadeo rojo y "BOUNCE EN CURSO". Pads de otras pistas, Copy, Fixed Length y Quantize con laterales: funcionan.
- [ ] Rechazos: slot ocupado como destino, destino en pista 1, destino en pista MIDI, nada sonando, algo grabando, segundo bounce con uno en curso. Cada uno con parpadeo rojo y su mensaje.
- [ ] Clips de 2 y 3 compases: el bounce dura 6. Con Fixed Length en 2 prendido: dura 2.
- [ ] Parar el transporte de Live a mitad: ruteo repuesto, barra "BOUNCE CORTADO".
- [ ] Cambiar el script a None a mitad de bounce: ruteo repuesto, sin errores en Log.txt.
- [ ] Vuelta atrás: Delete + pad del bounce lo borra; lateral de la fila original relanza los clips.

## Gain de clip (Snapshot mantenido + lateral)
Preparación: clips sonando en pistas 1 y 2. Sin bounce en curso.
- [ ] Bajar Snapshot: la barra menciona "+ CLIP + LATERAL = GAIN". Tocar un lateral sin haber tocado ningún clip: nada cambia, barra "GAIN: TOCAR UN CLIP SONANDO PRIMERO". Soltar: no saca foto.
- [ ] Bajar Snapshot, tocar el clip de pista 1 (parpadea ámbar), tocar lateral 4: la barra dice "GAIN  PISTA 1  ESCENA n: -3.0 DB" y en Live el Clip Gain del clip marca -3.0 dB. Lateral 4 verde, lateral 3 ámbar tenue, el resto apagado.
- [ ] Laterales 1 a 8 dan +6, +3, 0, -3, -6, -12, -15, -18 dB en el Clip Gain de Live. Si alguno no coincide, `Log.txt` dice "gain: niveles aproximados" o "texto en dB ilegible" (anotar qué muestra Live).
- [ ] Un solo Undo después del primer toque devuelve el gain original (la calibración no deja pasos sueltos). El LED de Undo se puso verde fuerte.
- [ ] Tocar el clip de pista 2 y lateral 6: solo ese clip pasa a -12 dB; los laterales muestran el nivel del clip de pista 2. Volver a tocar el clip de pista 1: los laterales muestran -3 dB y el clip sigue marcado.
- [ ] Soltar Snapshot sin tocar slot vacío: no hay foto ni bounce, los gains quedan.
- [ ] Con un clip a -6 dB, Snapshot mantenido, marcar ese clip y slot vacío: el bounce suena al nivel bajado.
- [ ] Cambiar el Clip Gain desde la pantalla de Live con Snapshot abajo y el clip enfocado: al siguiente pulso el lateral se mueve al escalón más cercano.

## Pulso / Tap / Metrónomo
- [ ] Cuatro toques a 120 ponen el tempo en ~120. Tres toques no cambian nada. Pausa de 3 s y cuatro toques nuevos funcionan.
- [ ] Mantener medio segundo alterna el metrónomo; el latido pasa a ámbar. La cuenta de taps se reinicia.
- [ ] El tap se registra al bajar el botón, no al soltar: la barra dice "TAP 1/4" en el momento del toque.

## INIT
- [ ] Undo + Fixed Length + Quantize mantenidos: la grilla parpadea roja; soltar antes de medio segundo cancela y ninguno de los tres hizo nada.
- [ ] Mantenidos más de medio segundo: los 64 slots quedan vacíos, nombres SNAP borrados, pistas y escenas intactas, un solo Undo lo recupera.

## Persistencia
- [ ] Cerrar Live con Fixed Length prendido en 8, Quantize 1/8t al 50%; abrir: Fixed Length apagado y en 1 compás, Quantize 1/16 al 100%. No se escribe ningún archivo.

## Desconexión
- [ ] Cambiar el script a None en Preferencias: el Launchpad se apaga, sin errores en Log.txt, y el log dice "LaunchpadLooper disconnected".
- [ ] Cerrar Live: el Launchpad se apaga. Si queda prendido, mirar si el log tiene "LaunchpadLooper disconnected" (si no está, Live cerró sin avisar al script).
