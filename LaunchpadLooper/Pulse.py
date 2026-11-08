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
