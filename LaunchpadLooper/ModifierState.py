"""Estado de los botones superiores. Modulo puro, sin Live."""
import time


class ModifierState(object):
    """Lleva que superiores estan abajo y en que orden, y decide que
    accion corresponde al soltar cada uno.

    press(name)      -> registra el boton abajo
    release(name)    -> 'undo' | 'toggle_fixed_length' | None
                        (el tap del pulso se registra al bajar, no al soltar)
    consume(name)    -> la pulsacion ya hizo algo (long press / acorde);
                        al soltar no debe hacer nada mas
    note_lateral_touch() -> se toco un lateral con un modificador abajo
    note_pad_touch() -> se toco un pad con un modificador abajo
    break_chord()    -> llego un pad o lateral con un acorde abajo: el
                        acorde no era intencional y queda bloqueado hasta
                        soltar todos sus botones
    active()         -> modificador activo (el primero que bajo) o None
    held_chord()     -> nombre del acorde cuyos botones estan todos abajo
    chord_held()     -> True mientras haya un acorde abajo

    Un modificador que ya se uso sobre pads o laterales no puede formar
    acorde mientras siga abajo. Los Launchpad MK1 mandan pulsaciones
    fantasma de los superiores vecinos con uno abajo (visto en el Log.txt),
    y sin esto armaban acordes e ignoraban los pads.

    Gracia: soltar el modificador y bajar el pad en el mismo gesto llega
    como 'release' y 16-50 ms despues el pad. Los modificadores de
    `grace_names` siguen activos `grace` segundos despues de soltarlos, si
    eran el activo al soltar. `now` se pasa en los tests; en Live es
    time.time().
    """

    def __init__(self, modifier_names, chord_names, grace=0.0, grace_names=()):
        self._modifiers = tuple(modifier_names)
        if isinstance(chord_names, dict):
            self._chords = dict((key, tuple(value)) for key, value in chord_names.items())
        else:
            self._chords = {'init': tuple(chord_names)}
        self._grace = float(grace)
        self._grace_names = tuple(grace_names)
        self._held = []
        self._consumed = set()
        self._touched = set()
        self._used = set()      # modificadores ya usados sobre pads o laterales
        self._broken = set()    # acordes rotos por un pad, hasta soltar todos
        self._grace_until = None  # (nombre, hora limite) del ultimo activo soltado

    def press(self, name):
        if name not in self._held:
            self._held.append(name)
        chord = self.held_chord()
        if chord is not None:
            for chord_name in self._chords[chord]:
                self._consumed.add(chord_name)

    def release(self, name, now=None):
        was_held = name in self._held
        was_active = self.active(now) == name and was_held
        if was_held:
            self._held.remove(name)
        if was_active and name in self._grace_names and self._grace > 0:
            self._grace_until = (name, self._now(now) + self._grace)
        consumed = name in self._consumed
        touched = name in self._touched
        self._consumed.discard(name)
        self._touched.discard(name)
        self._used.discard(name)
        for chord in list(self._broken):
            if not any(chord_name in self._held for chord_name in self._chords[chord]):
                self._broken.discard(chord)
        if not was_held or consumed:
            return None
        if name == 'undo':
            return 'undo'
        if name == 'fixed_length':
            if touched:
                return None
            return 'toggle_fixed_length'
        return None

    def consume(self, name):
        self._consumed.add(name)

    def note_lateral_touch(self, now=None):
        active = self.active(now)
        if active is not None and active in self._held:
            self._touched.add(active)
            self._used.add(active)

    def note_pad_touch(self, now=None):
        active = self.active(now)
        if active is not None and active in self._held:
            self._used.add(active)

    def break_chord(self):
        """Bloquea el acorde abajo (si hay) y devuelve su nombre."""
        chord = self.held_chord()
        if chord is not None:
            self._broken.add(chord)
        return chord

    def is_held(self, name):
        return name in self._held

    def active(self, now=None):
        for name in self._held:
            if name in self._modifiers:
                return name
        if self._grace_until is not None:
            name, deadline = self._grace_until
            if self._now(now) < deadline:
                return name
            self._grace_until = None
        return None

    def held_chord(self):
        """Nombre del acorde cuyos botones estan todos abajo, o None.
        Ignora los acordes rotos y los que incluyen un modificador en uso."""
        for chord, names in self._chords.items():
            if chord in self._broken:
                continue
            if any(name in self._used for name in names):
                continue
            if all(name in self._held for name in names):
                return chord
        return None

    def chord_held(self):
        return self.held_chord() is not None

    @staticmethod
    def _now(now):
        return time.time() if now is None else now
