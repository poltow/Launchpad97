"""Estado -> nombre de color de la skin. Modulo puro."""

EMPTY = 'empty'
STOPPED = 'stopped'
PLAYING = 'playing'
RECORDING = 'recording'
TRIGGERED_PLAY = 'triggered_play'
TRIGGERED_RECORD = 'triggered_record'
STOP_PENDING_PLAYING = 'stop_pending_playing'
STOP_PENDING_RECORDING = 'stop_pending_recording'
RECORDING_ENDING = 'recording_ending'

SOUNDING = (PLAYING, RECORDING, RECORDING_ENDING,
            STOP_PENDING_PLAYING, STOP_PENDING_RECORDING)
WITH_CLIP = (STOPPED, PLAYING, RECORDING, RECORDING_ENDING, TRIGGERED_PLAY,
             STOP_PENDING_PLAYING, STOP_PENDING_RECORDING)

NUM_FIXED_LENGTH_VALUES = 5
NUM_QUANTIZE_GRIDS = 5
QUANTIZE_AMOUNT_POSITIONS = (6, 7)


def slot_state(has_clip, is_triggered, will_record, is_playing, is_recording, stop_pending,
               ending_soon=False):
    if stop_pending and is_recording:
        return STOP_PENDING_RECORDING
    if stop_pending and is_playing:
        return STOP_PENDING_PLAYING
    if is_recording and (is_triggered or ending_soon):
        return RECORDING_ENDING
    if is_triggered:
        if will_record:
            return TRIGGERED_RECORD
        return TRIGGERED_PLAY
    if is_recording:
        return RECORDING
    if is_playing:
        return PLAYING
    if has_clip:
        return STOPPED
    return EMPTY


def slot_color(state, modifier, blink_on, is_copy_origin=False, init_pending=False,
               is_bounce_mark=False):
    if init_pending:
        return 'Looper.Slot.InitPending' if blink_on else 'Looper.Slot.Empty'
    if modifier == 'snapshot':
        if state != PLAYING:
            return 'Looper.Slot.Empty'
        if is_bounce_mark:
            return 'Looper.Slot.CopyOrigin' if blink_on else 'Looper.Slot.Empty'
        return 'Looper.Slot.Playing'
    if modifier == 'delete':
        if state in WITH_CLIP:
            return 'Looper.Slot.Delete'
        return 'Looper.Slot.Empty'
    if modifier == 'copy' and is_copy_origin:
        if blink_on:
            return 'Looper.Slot.CopyOrigin'
        return 'Looper.Slot.Empty'
    if state == EMPTY:
        return 'Looper.Slot.Empty'
    if state == STOPPED:
        return 'Looper.Slot.Stopped'
    if state == PLAYING:
        return 'Looper.Slot.Playing'
    if state == RECORDING:
        return 'Looper.Slot.Recording'
    if state == RECORDING_ENDING:
        return 'Looper.Slot.Recording' if blink_on else 'Looper.Slot.Playing'
    if state == TRIGGERED_PLAY:
        return 'Looper.Slot.Playing' if blink_on else 'Looper.Slot.Empty'
    if state == TRIGGERED_RECORD:
        return 'Looper.Slot.Recording' if blink_on else 'Looper.Slot.Empty'
    if state == STOP_PENDING_PLAYING:
        return 'Looper.Slot.StopPending' if blink_on else 'Looper.Slot.Playing'
    if state == STOP_PENDING_RECORDING:
        return 'Looper.Slot.StopPending' if blink_on else 'Looper.Slot.Recording'
    return 'Looper.Slot.Empty'


def scene_color(has_playing, has_clips, is_triggered, modifier, blink_on):
    """Lateral: verde si algo de la fila suena, ambar tenue (como un clip
    detenido) si solo hay clips parados, apagado si la fila esta vacia."""
    if modifier == 'snapshot':
        return 'Looper.Scene.Off'
    if modifier == 'delete':
        return 'Looper.Scene.Delete' if has_clips else 'Looper.Scene.Off'
    if modifier == 'stop':
        return 'Looper.Scene.Playing' if has_playing else 'Looper.Scene.Off'
    if is_triggered:
        return 'Looper.Scene.Playing' if blink_on else 'Looper.Scene.Off'
    if has_playing:
        return 'Looper.Scene.Playing'
    if has_clips:
        return 'Looper.Scene.Stopped'
    return 'Looper.Scene.Off'


def fixed_length_row(selected_index):
    row = []
    for index in range(8):
        if index >= NUM_FIXED_LENGTH_VALUES:
            row.append('Looper.Value.Off')
        elif index == selected_index:
            row.append('Looper.Value.Selected')
        else:
            row.append('Looper.Value.Idle')
    return row


def quantize_row(grid_index, amount_index):
    row = []
    for index in range(8):
        if index < NUM_QUANTIZE_GRIDS:
            row.append('Looper.Value.Selected' if index == grid_index else 'Looper.Value.Idle')
        elif index in QUANTIZE_AMOUNT_POSITIONS:
            position = QUANTIZE_AMOUNT_POSITIONS.index(index)
            row.append('Looper.Value.Selected' if position == amount_index else 'Looper.Value.Idle')
        else:
            row.append('Looper.Value.Off')
    return row
