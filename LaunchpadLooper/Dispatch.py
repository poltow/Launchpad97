"""Gesto + modificador activo -> accion. Modulo puro."""

try:
    from . import SlotColors as C
except (ImportError, ValueError):
    import SlotColors as C

NONE = 'none'
RECORD = 'record'
LAUNCH = 'launch'
STOP_IMMEDIATE = 'stop_immediate'
CLOSE_RECORDING = 'close_recording'
DELETE_CLIP = 'delete_clip'
COPY_SET_ORIGIN = 'copy_set_origin'
COPY_PASTE = 'copy_paste'
QUANTIZE_CLIP = 'quantize_clip'
STOP_TRACK = 'stop_track'
BOUNCE_MARK = 'bounce_mark'
BOUNCE_TARGET = 'bounce_target'

FIRE_SCENE = 'fire_scene'
SET_FIXED_LENGTH = 'set_fixed_length'
SET_QUANTIZE_GRID = 'set_quantize_grid'
SET_QUANTIZE_AMOUNT = 'set_quantize_amount'
DELETE_ROW = 'delete_row'
STOP_ROW = 'stop_row'
SET_GAIN = 'set_gain'

NUM_FIXED_LENGTH_VALUES = 5
NUM_QUANTIZE_GRIDS = 5
QUANTIZE_AMOUNT_POSITIONS = (6, 7)


def pad_action(modifier, state, has_copy_origin):
    """Accion al bajar un pad. `state` es uno de los estados de SlotColors."""
    if modifier == 'delete':
        return DELETE_CLIP if state in C.WITH_CLIP else NONE
    if modifier == 'copy':
        if state in (C.STOPPED, C.PLAYING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            return COPY_SET_ORIGIN
        if state == C.EMPTY and has_copy_origin:
            return COPY_PASTE
        return NONE
    if modifier == 'quantize':
        if state in (C.STOPPED, C.PLAYING, C.TRIGGERED_PLAY, C.STOP_PENDING_PLAYING):
            return QUANTIZE_CLIP
        return NONE
    if modifier == 'stop':
        # clip parado: se lanza en sync, asi la transicion con los stops
        # pedidos en el mismo compas sale junta
        return LAUNCH if state == C.STOPPED else STOP_TRACK
    if modifier == 'snapshot':
        if state == C.PLAYING:
            return BOUNCE_MARK
        if state == C.EMPTY:
            return BOUNCE_TARGET
        return NONE
    # sin modificador, o Fixed Length mantenido
    if state == C.EMPTY:
        return RECORD
    if state in (C.RECORDING, C.RECORDING_ENDING, C.STOP_PENDING_RECORDING):
        return CLOSE_RECORDING
    if state in (C.PLAYING, C.STOP_PENDING_PLAYING):
        return STOP_IMMEDIATE
    if state in (C.STOPPED, C.TRIGGERED_PLAY):
        return LAUNCH
    return NONE


def lateral_action(modifier, index):
    """Accion al bajar el lateral `index` (0..7). Devuelve (accion, valor)."""
    if modifier == 'fixed_length':
        if index < NUM_FIXED_LENGTH_VALUES:
            return (SET_FIXED_LENGTH, index)
        return (NONE, index)
    if modifier == 'quantize':
        if index < NUM_QUANTIZE_GRIDS:
            return (SET_QUANTIZE_GRID, index)
        if index in QUANTIZE_AMOUNT_POSITIONS:
            return (SET_QUANTIZE_AMOUNT, QUANTIZE_AMOUNT_POSITIONS.index(index))
        return (NONE, index)
    if modifier == 'delete':
        return (DELETE_ROW, index)
    if modifier == 'stop':
        return (STOP_ROW, index)
    if modifier == 'snapshot':
        return (SET_GAIN, index)  # gain del clip enfocado (ClipGain.LEVELS_DB)
    if modifier == 'copy':
        return (NONE, index)
    return (FIRE_SCENE, index)
