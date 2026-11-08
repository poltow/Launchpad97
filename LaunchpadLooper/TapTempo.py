"""Tap tempo por marcas de tiempo. Modulo puro, sin Live."""

MAX_TAPS = 8


class TapTempo(object):

    def __init__(self, window=2.0, min_taps=4, tempo_min=20.0, tempo_max=999.0):
        self._window = float(window)
        self._min_taps = int(min_taps)
        self._tempo_min = float(tempo_min)
        self._tempo_max = float(tempo_max)
        self._taps = []

    def tap(self, now):
        """Registra un toque en el instante `now` (segundos). Devuelve el
        tempo calculado a partir del cuarto toque consecutivo, o None."""
        if self._taps and now - self._taps[-1] > self._window:
            self._taps = []
        self._taps.append(float(now))
        if len(self._taps) > MAX_TAPS:
            self._taps = self._taps[-MAX_TAPS:]
        if len(self._taps) < self._min_taps:
            return None
        intervals = [b - a for a, b in zip(self._taps[:-1], self._taps[1:])]
        average = sum(intervals) / float(len(intervals))
        if average <= 0.0:
            return None
        tempo = 60.0 / average
        return max(self._tempo_min, min(self._tempo_max, tempo))

    def reset(self):
        self._taps = []

    def count(self):
        """Toques acumulados en la serie actual."""
        return len(self._taps)

    def is_counting(self, now):
        return bool(self._taps) and now - self._taps[-1] <= self._window
