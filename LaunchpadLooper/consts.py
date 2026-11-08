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
CONFIG_LAYOUT_XY = 1     # mapeo X-Y de la grilla (Launchpad95 lo manda despues del flash)
LED_OFF = 12             # 0x0C: apagado en los dos buffers

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
MODIFIER_NAMES = ('fixed_length', 'quantize', 'delete', 'stop', 'copy', 'snapshot')
# INIT (los 3 de la izquierda, medio segundo) vacia la grilla y ademas crea o toma
# el retorno BOUNCE. El setup del bounce era Delete + Stop + Copy, pero el
# Launchpad MK1 manda Stop y Copy fantasma con Delete abajo y lo armaba solo.
INIT_CHORD = ('undo', 'fixed_length', 'quantize')
CHORDS = {'init': INIT_CHORD}
# Tras soltar uno de estos, los pads lo siguen usando MODIFIER_GRACE segundos:
# soltar y bajar el pad en el mismo gesto llega al reves por 16-50 ms.
GRACE_MODIFIERS = ('delete', 'stop', 'quantize')
MODIFIER_GRACE = 0.15

# Tiempos en segundos
LONG_PRESS = 0.5
INIT_HOLD = 0.5
REJECT_FLASH = 0.3
TIMER_TICK = 0.1
RAINBOW_TICKS = 3        # el arcoiris de Snapshot avanza un color cada 3 tics (300 ms)

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

# Bounce
BOUNCE_RETURN_NAME = 'BOUNCE'
BOUNCE_MAX_BARS = 64
BOUNCE_SEND_LEVEL = 1.0      # 0 dB
SENDS_ONLY = 'Sends Only'    # texto de Live para la salida del retorno
MONITOR_IN = 0
MONITOR_AUTO = 1
MONITOR_OFF = 2

# Diagnostico: con True cada accion sobre el set deja una linea detallada en
# Log.txt (prefijo 'LaunchpadLooper diag:'). Sirve para ubicar que hacia el
# script justo antes de un crash de Live o de un send que no volvio.
DIAG_LOG = True
