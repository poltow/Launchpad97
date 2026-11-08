"""Sigue las grabaciones con largo fijo para avisar su ultimo compas. Modulo puro."""


class FixedLengthTracker(object):

    def __init__(self):
        self._pending = {}
        self._active = {}
        self._ending = set()

    def fired(self, key, bars):
        """Se disparo una grabacion de `bars` compases en `key`."""
        self._active.pop(key, None)
        self._ending.discard(key)
        self._pending[key] = int(bars)

    def forget(self, key):
        self._pending.pop(key, None)
        self._active.pop(key, None)
        self._ending.discard(key)

    def is_tracked(self, key):
        return key in self._pending or key in self._active

    def tracked_keys(self):
        return list(self._pending.keys()) + list(self._active.keys())

    def ending_soon(self, key):
        return key in self._ending

    def update(self, key, is_recording, is_triggered, current_bar):
        """Actualiza `key` con el estado actual del slot. Devuelve True si la
        grabacion esta en su ultimo compas."""
        if key in self._pending:
            if is_recording:
                self._active[key] = (int(current_bar), self._pending.pop(key))
            elif not is_triggered:
                self._pending.pop(key)
                return False
            else:
                return False
        if key not in self._active:
            self._ending.discard(key)
            return False
        if not is_recording:
            self.forget(key)
            return False
        start_bar, bars = self._active[key]
        ending = int(current_bar) >= start_bar + bars - 1
        if ending:
            self._ending.add(key)
        else:
            self._ending.discard(key)
        return ending
