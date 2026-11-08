"""Que se permite mientras hay un bounce en curso (matriz 2.3 de la spec).
Modulo puro. P1 = job sin empezar; P2/P3 = job.started."""

ALLOW = 'allow'
REJECT = 'reject'
CANCEL = 'cancel'
CLOSE = 'close'
IGNORE = 'ignore'

try:
    from . import SlotColors as C
except (ImportError, ValueError):
    import SlotColors as C

_VALUE_MODIFIERS = ('fixed_length', 'quantize')


def pad_decision(job, modifier, key, state):
    if job is None:
        return ALLOW
    track = key[0]
    if job.is_target(key):
        if modifier == 'delete':
            return CANCEL
        if modifier in (None, 'stop'):
            if not job.started:
                return CANCEL
            if job.closing or state == C.RECORDING_ENDING:
                return IGNORE
            return CLOSE
        return IGNORE
    if job.involves_track(track):
        return ALLOW if modifier == 'copy' else REJECT
    return ALLOW


def lateral_decision(job, modifier, scene_index, row_tracks):
    """row_tracks: pistas cuyo clip sonando esta en esa fila (para Stop)."""
    if job is None:
        return ALLOW
    if modifier in _VALUE_MODIFIERS or modifier == 'copy':
        return ALLOW
    if modifier == 'delete':
        return REJECT if job.involves_row(scene_index) else ALLOW
    if modifier == 'stop':
        for track in row_tracks:
            if job.is_origin_track(track):
                return REJECT
        return ALLOW
    return REJECT


def top_decision(job, name):
    if job is None:
        return ALLOW
    if name == 'snapshot':
        if not job.started:
            return CANCEL
        if job.closing:
            return IGNORE
        return CLOSE
    if name == 'undo':
        return REJECT
    return ALLOW


def chord_decision(job):
    return ALLOW if job is None else REJECT
