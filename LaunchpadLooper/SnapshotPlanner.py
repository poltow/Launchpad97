"""Planificacion de un snapshot sobre la grilla 8x8. Modulo puro."""

REJECT_RECORDING = 'recording'
REJECT_NO_ROW = 'no_free_row'


def find_free_row(grid):
    """Primera fila, buscando desde la ultima hacia la primera, con
    todos sus slots vacios. None si no hay."""
    for row in range(grid.num_scenes - 1, -1, -1):
        free = True
        for track in range(grid.num_tracks):
            if grid.has_clip(track, row):
                free = False
                break
        if free:
            return row
    return None


def plan_snapshot(grid):
    """Devuelve (fila_destino, motivo_rechazo, copias).
    copias es una lista de (track, fila_origen) con los clips sonando."""
    for track in range(grid.num_tracks):
        for scene in range(grid.num_scenes):
            if grid.is_recording(track, scene):
                return (None, REJECT_RECORDING, [])
    row = find_free_row(grid)
    if row is None:
        return (None, REJECT_NO_ROW, [])
    copies = []
    for track in range(grid.num_tracks):
        for scene in range(grid.num_scenes):
            if grid.is_playing(track, scene):
                copies.append((track, scene))
    return (row, None, copies)
