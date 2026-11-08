"""Gain de clip en escalera de 8 niveles (laterales con Snapshot abajo).
Modulo puro: Live expone `Clip.gain` como float 0..1 sin documentar la curva
hacia dB, y `Clip.gain_display_string` con el texto en dB. La tabla
float->nivel se halla por biseccion leyendo ese texto (Calibration)."""

import re

LEVELS_DB = (6.0, 3.0, 0.0, -3.0, -6.0, -12.0, -15.0, -18.0)
NUM_LEVELS = len(LEVELS_DB)
ZERO_INDEX = 2
# aproximacion (curva lineal de 40 dB por unidad, 0 dB en 0.85) si no se
# puede leer el texto en dB de Live
FALLBACK = (1.0, 0.925, 0.85, 0.775, 0.7, 0.55, 0.475, 0.4)

_DB_RE = re.compile(r'([+-]?)\s*(inf|\d+(?:[.,]\d+)?)', re.IGNORECASE)


def parse_db(text):
    """'+6.0 dB' -> 6.0, '-3,5 dB' -> -3.5, '-inf dB' -> -inf, basura -> None."""
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
    """Indice del nivel mas cercano en dB; None si no hay valor."""
    if db is None:
        return None
    if db == float('-inf'):
        return NUM_LEVELS - 1
    if db == float('inf'):
        return 0
    best, best_distance = 0, None
    for index, level in enumerate(LEVELS_DB):
        distance = abs(level - db)
        if best_distance is None or distance < best_distance:
            best, best_distance = index, distance
    return best


def lateral_color(index, current_index):
    """Color del lateral `index` con un clip enfocado en `current_index`
    (None = sin foco): el actual verde, el de 0 dB ambar tenue, resto apagado."""
    if current_index is None:
        return 'Looper.Scene.Off'
    if index == current_index:
        return 'Looper.Scene.Playing'
    if index == ZERO_INDEX:
        return 'Looper.Scene.Stopped'
    return 'Looper.Scene.Off'


class Calibration(object):
    """Tabla float->nivel hallada por biseccion sobre un clip real.
    `calibrate(write, read)`: write(float) escribe el gain, read() devuelve
    el texto en dB. Devuelve la lista de niveles que quedaron aproximados,
    o None si el texto no se pudo leer (queda FALLBACK)."""

    ITERATIONS = 24
    TOLERANCE = 0.005  # Live 11 muestra dos decimales: '-3.00 dB', no '-2.99 dB'

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
