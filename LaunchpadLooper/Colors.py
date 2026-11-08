"""Colores del Launchpad MK1 y skin de LaunchpadLooper."""
from _Framework.ButtonElement import Color
from _Framework.Skin import Skin


class Rgb:
    BLACK = Color(4)
    RED = Color(7)
    RED_HALF = Color(6)
    RED_THIRD = Color(5)
    RED_BLINK = Color(11)
    GREEN = Color(52)
    GREEN_HALF = Color(36)
    GREEN_THIRD = Color(20)
    GREEN_BLINK = Color(56)
    AMBER = Color(55)
    AMBER_HALF = Color(38)
    AMBER_THIRD = Color(21)
    AMBER_BLINK = Color(59)
    ORANGE = Color(39)
    ORANGE_HALF = Color(22)
    ORANGE_BLINK = Color(43)   # parpadeo por hardware (flag 0x08, sin copy), sigue sin Play
    MANDARIN = Color(23)
    YELLOW = Color(54)
    LIME = Color(53)


class Colors:

    class DefaultButton:
        On = Rgb.GREEN
        Off = Rgb.GREEN_THIRD
        Disabled = Rgb.BLACK

    class Looper:

        class Slot:
            Empty = Rgb.BLACK
            Stopped = Rgb.AMBER_THIRD
            Playing = Rgb.GREEN
            Recording = Rgb.RED
            StopPending = Rgb.AMBER
            Delete = Rgb.RED
            CopyOrigin = Rgb.AMBER
            InitPending = Rgb.RED

        class Scene:
            Off = Rgb.BLACK
            Playing = Rgb.GREEN
            Stopped = Rgb.AMBER_THIRD
            Delete = Rgb.RED

        class Value:
            Selected = Rgb.AMBER
            Idle = Rgb.AMBER_THIRD
            Off = Rgb.BLACK

        class Top:
            UndoNone = Rgb.GREEN_THIRD      # nada para deshacer
            Undo = Rgb.GREEN                # hay para deshacer
            UndoRedo = Rgb.LIME             # alterna con Undo al pulso si tambien hay para rehacer
            UndoHeld = Rgb.AMBER
            FixedLengthOff = Rgb.ORANGE_HALF
            FixedLengthOn = Rgb.ORANGE_BLINK  # parpadeo del Launchpad, no del pulso
            Quantize = Rgb.YELLOW
            Delete = Rgb.RED
            Stop = Rgb.AMBER
            Copy = Rgb.MANDARIN
            Rainbow1 = Rgb.RED
            Rainbow2 = Rgb.MANDARIN
            Rainbow3 = Rgb.ORANGE
            Rainbow4 = Rgb.AMBER
            Rainbow5 = Rgb.YELLOW
            Rainbow6 = Rgb.LIME
            Rainbow7 = Rgb.GREEN
            SnapshotHeld = Rgb.GREEN      # Snapshot abajo, sin clips marcados
            SnapshotMarked = Rgb.AMBER    # Snapshot abajo, con clips marcados para bounce
            PulseOff = Rgb.BLACK
            PulseWeak = Rgb.GREEN_THIRD
            PulseStrong = Rgb.GREEN
            PulseMetroWeak = Rgb.AMBER_THIRD
            PulseMetroStrong = Rgb.AMBER
            Reject = Rgb.RED


# Arcoiris ida y vuelta, un paso cada consts.RAINBOW_TICKS tics de 100 ms.
SNAPSHOT_CYCLE = tuple('Looper.Top.Rainbow%d' % n for n in (1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2))


def make_skin():
    return Skin(Colors)
