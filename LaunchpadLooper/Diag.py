"""Descripciones del estado de Live para el log de diagnostico. Modulo puro
por duck typing: nunca lanza, donde no pudo leer pone '?'. Las lineas salen
en Log.txt con la marca de tiempo de Live, asi que no se agrega hora."""


def attr(obj, name):
    try:
        return getattr(obj, name)
    except Exception:
        return '?'


def num(value):
    try:
        return '%.3f' % float(value)
    except Exception:
        return '?'


def quant(value):
    """'Quantization.q_bar' -> 'q_bar'."""
    text = str(value)
    return text.rsplit('.', 1)[-1]


def song_state(song):
    """Transporte y cuantizacion global."""
    try:
        return 'play=%s q=%s t=%s tempo=%s' % (
            attr(song, 'is_playing'),
            quant(attr(song, 'clip_trigger_quantization')),
            num(attr(song, 'current_song_time')),
            num(attr(song, 'tempo')))
    except Exception:
        return 'song=?'


def track_state(track, index=None):
    """Nombre, arm, monitor, entrada y slots activos de una pista."""
    try:
        prefix = 'pista %s' % index if index is not None else 'pista'
        return '%s %r arm=%s armable=%s mon=%s in=%r playing=%s fired=%s' % (
            prefix,
            str(attr(track, 'name')),
            attr(track, 'arm'),
            attr(track, 'can_be_armed'),
            attr(track, 'current_monitoring_state'),
            str(attr(track, 'current_input_routing')),
            attr(track, 'playing_slot_index'),
            attr(track, 'fired_slot_index'))
    except Exception:
        return 'pista=?'


def slot_state(slot):
    """Clip, disparo y grabacion de un slot."""
    try:
        has_clip = attr(slot, 'has_clip')
        text = 'slot clip=%s trig=%s will_rec=%s' % (
            has_clip, attr(slot, 'is_triggered'), attr(slot, 'will_record_on_start'))
        if has_clip is True:
            clip = attr(slot, 'clip')
            text += ' | clip play=%s rec=%s trig=%s len=%s loop=%s' % (
                attr(clip, 'is_playing'), attr(clip, 'is_recording'),
                attr(clip, 'is_triggered'), num(attr(clip, 'length')),
                attr(clip, 'looping'))
        return text
    except Exception:
        return 'slot=?'


def send_value(send):
    return num(attr(send, 'value'))


def send_values(tracks, send_index):
    """'t0=0.000 t1=1.000 ...' con el send `send_index` de cada pista."""
    parts = []
    for index, track in enumerate(tracks):
        try:
            send = track.mixer_device.sends[send_index]
            parts.append('t%s=%s' % (index, send_value(send)))
        except Exception:
            parts.append('t%s=?' % index)
    return ' '.join(parts)


def saved_sends(saved):
    """Sends guardados por bounce_start: '(pista, guardado, actual) ...'."""
    parts = []
    try:
        for send, value in saved.get('sends', []):
            parts.append('%s->%s' % (num(value), send_value(send)))
    except Exception:
        return '?'
    return ' '.join(parts) if parts else '(ninguno)'
