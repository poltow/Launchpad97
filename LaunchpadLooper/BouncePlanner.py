"""Validacion y largo de un bounce sobre la grilla 8x8. Modulo puro.

grid: num_tracks, num_scenes, beats_per_bar, has_clip(t, s), is_playing(t, s),
is_recording(t, s), clip_length(t, s) en beats, is_audio_track(t)."""

try:
    from . import consts
except (ImportError, ValueError):
    import consts

REJECT_IN_PROGRESS = 'in_progress'
REJECT_RECORDING = 'recording'
REJECT_NOTHING_PLAYING = 'nothing_playing'
REJECT_TARGET_OCCUPIED = 'target_occupied'
REJECT_TARGET_ON_ORIGIN_TRACK = 'target_on_origin_track'
REJECT_TARGET_NOT_AUDIO = 'target_not_audio'
REJECT_TOO_LONG = 'too_long'


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return a * b // _gcd(a, b)


def length_beats(lengths_beats, beats_per_bar, fixed_length_bars=None):
    """Minimo comun multiplo de los largos (redondeados al beat), llevado a
    compases enteros hacia arriba. Fixed Length solo acorta."""
    beats_per_bar = int(beats_per_bar)
    total = 0
    for length in lengths_beats:
        beats = int(round(float(length)))
        if beats < 1:
            beats = 1
        total = beats if total == 0 else lcm(total, beats)
    if total == 0:
        return 0
    bars = (total + beats_per_bar - 1) // beats_per_bar
    if fixed_length_bars and int(fixed_length_bars) < bars:
        bars = int(fixed_length_bars)
    return bars * beats_per_bar


def _playing_cells(grid):
    cells = []
    for track in range(grid.num_tracks):
        for scene in range(grid.num_scenes):
            if grid.is_playing(track, scene):
                cells.append((track, scene))
    return cells


def plan_bounce(grid, marked, target, fixed_length_bars, in_progress):
    """Devuelve (origenes, largo_en_beats, motivo_rechazo)."""
    if in_progress:
        return ([], 0, REJECT_IN_PROGRESS)
    for track in range(grid.num_tracks):
        for scene in range(grid.num_scenes):
            if grid.is_recording(track, scene):
                return ([], 0, REJECT_RECORDING)
    if marked:
        origins = [key for key in marked if grid.is_playing(key[0], key[1])]
    else:
        origins = _playing_cells(grid)
    if not origins:
        return ([], 0, REJECT_NOTHING_PLAYING)
    target_track, target_scene = target
    if grid.has_clip(target_track, target_scene):
        return ([], 0, REJECT_TARGET_OCCUPIED)
    if target_track in [key[0] for key in origins]:
        return ([], 0, REJECT_TARGET_ON_ORIGIN_TRACK)
    if not grid.is_audio_track(target_track):
        return ([], 0, REJECT_TARGET_NOT_AUDIO)
    lengths = [grid.clip_length(key[0], key[1]) for key in origins]
    length = length_beats(lengths, grid.beats_per_bar, fixed_length_bars)
    if length > consts.BOUNCE_MAX_BARS * int(grid.beats_per_bar):
        return ([], 0, REJECT_TOO_LONG)
    return (origins, length, None)
