"""Seleccion con Snapshot abajo y bounce en curso. Modulo puro."""


class BounceSelection(object):
    """Mientras Snapshot esta abajo: clips marcados y si se toco algo.
    Al soltar decide si corresponde la foto (corto y sin tocar nada)."""

    def __init__(self, long_press):
        self._long_press = float(long_press)
        self._active = False
        self._pressed_at = 0.0
        self._touched = False
        self._marked = []
        self._focus = None

    def press(self, now):
        self._active = True
        self._pressed_at = float(now)
        self._touched = False
        self._marked = []
        self._focus = None

    def is_active(self):
        return self._active

    def mark(self, key):
        """Marca el clip (sin alternar) y lo deja enfocado para el gain.
        Devuelve True si marco. No hay desmarcado individual: soltar
        Snapshot limpia todo."""
        if not self._active:
            return False
        self._touched = True
        self._focus = key
        if key not in self._marked:
            self._marked.append(key)
        return True

    def is_marked(self, key):
        return key in self._marked

    def focused(self):
        """Ultimo clip tocado con Snapshot abajo, o None."""
        return self._focus

    def marked(self):
        return list(self._marked)

    def note_touch(self):
        if self._active:
            self._touched = True

    def touched(self):
        return self._touched

    def release(self, now):
        """'snapshot' si fue corto y no se toco nada; None en otro caso."""
        short = (float(now) - self._pressed_at) < self._long_press
        result = 'snapshot' if (short and not self._touched) else None
        self.clear()
        return result

    def clear(self):
        self._active = False
        self._touched = False
        self._marked = []
        self._focus = None


class BounceJob(object):
    """Un bounce en curso: destino, origenes y estado guardado para reponer."""

    def __init__(self, target, origins, saved, bars):
        self.target = tuple(target)
        self.origins = [tuple(key) for key in origins]
        self.saved = saved
        self.bars = int(bars)
        self.started = False
        self.closing = False
        self.origins_stopped = False

    def origin_tracks(self):
        tracks = []
        for track, _scene in self.origins:
            if track not in tracks:
                tracks.append(track)
        return tracks

    def is_origin_track(self, track):
        return track in self.origin_tracks()

    def is_target_track(self, track):
        return track == self.target[0]

    def involves_track(self, track):
        return self.is_origin_track(track) or self.is_target_track(track)

    def origin_rows_include(self, scene):
        return scene in [s for _t, s in self.origins]

    def involves_row(self, scene):
        return self.origin_rows_include(scene) or scene == self.target[1]

    def is_target(self, key):
        return tuple(key) == self.target
