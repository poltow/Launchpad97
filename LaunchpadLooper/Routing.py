"""Retorno BOUNCE y ruteo de entrada, por duck typing sobre la API de Live.

Live muestra los retornos en los menus de ruteo como 'A-Return' para un
retorno llamado 'A Return'; para un retorno llamado 'BOUNCE' puede mostrar
'BOUNCE', 'A-BOUNCE' o 'A BOUNCE'. Se acepta el nombre solo o precedido por
la letra que le corresponde por posicion."""


def _normalize(text):
    return ''.join(ch for ch in str(text).lower() if ch not in ' -_')


def _matches(shown, wanted):
    """El nombre mostrado es el buscado, sin distinguir mayusculas, espacios
    ni guiones, y aceptando una letra de retorno adelante ('A BOUNCE')."""
    shown = _normalize(shown)
    return shown == wanted or (len(shown) == len(wanted) + 1 and shown[0].isalpha() and shown[1:] == wanted)


def find_return(song, name):
    wanted = _normalize(name)
    for index, track in enumerate(song.return_tracks):
        if _matches(track.name, wanted):
            return (index, track)
    return (None, None)


def return_names(song):
    """Nombres reales de los retornos del set, para el log."""
    return [str(track.name) for track in song.return_tracks]


def ensure_return(song, name, sends_only):
    """Devuelve (indice, retorno, creado). (None, None, False) si no se pudo."""
    index, track = find_return(song, name)
    created = False
    if track is None:
        try:
            song.create_return_track()
        except RuntimeError:
            return (None, None, False)
        index = len(song.return_tracks) - 1
        if index < 0:
            return (None, None, False)
        track = song.return_tracks[index]
        track.name = name
        created = True
    if sends_only in list(track.output_routings) and track.current_output_routing != sends_only:
        track.current_output_routing = sends_only
    return (index, track, created)


def input_routing_for(track, return_index, return_name):
    """Cadena de track.input_routings que corresponde al retorno, o None."""
    wanted = _normalize(return_name)
    letter = chr(ord('a') + int(return_index))
    accepted = (wanted, letter + wanted)
    for candidate in track.input_routings:
        if _normalize(candidate) in accepted:
            return candidate
    return None
