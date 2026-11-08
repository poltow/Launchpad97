"""Textos para la barra de estado de Live. Modulo puro, solo ASCII.
Cortos, en mayusculas, para leerse de un vistazo."""

_TEMPLATES = {
    'record': 'REC  PISTA %(track)d  ESCENA %(scene)d',
    'record_fixed': 'REC %(bars)d COMPASES  PISTA %(track)d  ESCENA %(scene)d',
    'launch': 'PLAY  PISTA %(track)d  ESCENA %(scene)d',
    'stop_immediate': 'STOP YA  PISTA %(track)d',
    'close_recording': 'CIERRA REC  PISTA %(track)d  ESCENA %(scene)d',
    'delete_clip': 'BORRAR  PISTA %(track)d  ESCENA %(scene)d',
    'copy_origin': 'COPIAR  PISTA %(track)d  ESCENA %(scene)d',
    'copy_paste': 'PEGADO  PISTA %(track)d  ESCENA %(scene)d',
    'copy_reject': 'NO SE PEGA: SLOT OCUPADO',
    'quantize_clip': 'QUANTIZE %(grid)s %(percent)d%%  PISTA %(track)d  ESCENA %(scene)d',
    'stop_track': 'STOP EN SYNC  PISTA %(track)d',
    'scene': 'ESCENA %(scene)d%(suffix)s',
    'fixed_length_bars': 'FIXED LENGTH %(bars)d %(unit)s',
    'quantize_setting': 'QUANTIZE %(grid)s %(percent)d%%',
    'delete_row': 'BORRAR FILA %(scene)d',
    'stop_row': 'STOP EN SYNC  FILA %(scene)d',
    'undo': 'UNDO',
    'redo': 'REDO',
    'fixed_length': 'FIXED LENGTH %(state)s',
    'tap_tempo': 'TAP %(tempo).1f BPM',
    'tap_count': 'TAP %(count)d/%(needed)d',
    'metronome': 'METRONOMO %(state)s',
    'snapshot': 'SNAPSHOT EN FILA %(scene)d',
    'snapshot_reject': 'SNAPSHOT NO: %(why)s',
    'init_pending': 'INIT: MANTENER 1/2 SEG',
    'init_done': 'INIT: GRILLA VACIA, BOUNCE LISTO (UNDO RECUPERA LA GRILLA)',
    'init_done_created': 'INIT: GRILLA VACIA, RETORNO BOUNCE CREADO (UNDO RECUPERA LA GRILLA)',
    'init_done_no_bounce': 'INIT: GRILLA VACIA, NO SE PUDO CREAR EL RETORNO BOUNCE',
    'ready': 'LAUNCHPAD LOOPER OK',
    # al bajar cada superior, antes de que haga nada
    'press_undo': 'UNDO  (MANTENER = REDO)',
    'press_fixed_length': 'FIXED LENGTH  LATERALES = COMPASES',
    'press_quantize': 'QUANTIZE  LATERALES = GRILLA  PAD = APLICAR',
    'press_delete': 'DELETE  PAD = CLIP  LATERAL = FILA',
    'press_stop': 'STOP EN SYNC  PAD = PISTA  /  CLIP PARADO = PLAY  /  LATERAL = FILA',
    'press_copy': 'COPY  TOCAR CLIP ORIGEN, LUEGO SLOTS VACIOS',
    'press_pulse': 'TAP %(count)d/%(needed)d  (MANTENER = METRONOMO)',
    'press_snapshot': 'SNAPSHOT: SOLTAR = FOTO  /  + CLIPS + SLOT VACIO = BOUNCE  /  + CLIP + LATERAL = GAIN',
    # gain de clip (Snapshot abajo + lateral)
    'gain': 'GAIN  PISTA %(track)d  ESCENA %(scene)d: %(db)s',
    'gain_no_focus': 'GAIN: TOCAR UN CLIP SONANDO PRIMERO',
    'gain_failed': 'GAIN: ERROR DE LIVE (VER LOG)',
    # bounce
    'bounce_marked': 'BOUNCE: %(count)d CLIPS ELEGIDOS',
    'bounce_start': 'BOUNCE %(count)d CLIPS -> PISTA %(track)d  ESCENA %(scene)d  (%(bars)d COMPASES)',
    'bounce_reject': 'BOUNCE NO: %(why)s',
    'bounce_busy': 'BOUNCE EN CURSO',
    'bounce_cancelled': 'BOUNCE CANCELADO',
    'bounce_closing': 'BOUNCE: CIERRA EN EL COMPAS',
    'bounce_done': 'BOUNCE LISTO',
    'bounce_cut': 'BOUNCE CORTADO',
    'bounce_return_created': 'BOUNCE: RETORNO CREADO',
}

_REJECT_REASONS = {
    'recording': 'PISTA GRABANDO',
    'no_free_row': 'SIN FILA LIBRE',
}

_BOUNCE_REASONS = {
    'in_progress': 'YA HAY UNO EN CURSO',
    'recording': 'HAY PISTA GRABANDO',
    'nothing_playing': 'NADA SONANDO',
    'target_occupied': 'DESTINO OCUPADO',
    'target_on_origin_track': 'DESTINO EN PISTA DE ORIGEN',
    'target_not_audio': 'DESTINO NO ES PISTA DE AUDIO',
    'too_long': 'LARGO MAYOR A 64 COMPASES, USAR FIXED LENGTH',
    'no_return_input': 'SIN ENTRADA DESDE RETORNO',
    'no_return': 'SIN RETORNO BOUNCE, HACER INIT (3 DE LA IZQUIERDA)',
    'live_error': 'ERROR DE LIVE (VER LOG)',
}


def text(event, **kw):
    """Devuelve el texto del evento en mayusculas. Indices track/scene son 0-based."""
    template = _TEMPLATES.get(event)
    if template is None:
        return ''
    args = dict(kw)
    if 'track' in args:
        args['track'] = int(args['track']) + 1
    if 'scene' in args:
        args['scene'] = int(args['scene']) + 1
    if 'amount' in args:
        args['percent'] = int(round(float(args['amount']) * 100))
    if event == 'scene':
        name = args.get('name') or ''
        args['suffix'] = '  %s' % name if name else ''
    if event == 'fixed_length_bars':
        args['unit'] = 'COMPAS' if int(args['bars']) == 1 else 'COMPASES'
    if event == 'fixed_length':
        if args.get('on'):
            args['state'] = 'ON  %d COMPASES' % int(args['bars'])
        else:
            args['state'] = 'OFF'
    if event == 'metronome':
        args['state'] = 'ON' if args.get('on') else 'OFF'
    if event == 'snapshot_reject':
        args['why'] = _REJECT_REASONS.get(args.get('reason'), str(args.get('reason')))
    if event == 'bounce_reject':
        args['why'] = _BOUNCE_REASONS.get(args.get('reason'), str(args.get('reason')))
    return (template % args).upper()


# Resultado de LooperSession.setup_bounce_return() -> mensaje de INIT
INIT_DONE_BY_BOUNCE = {
    'taken': 'init_done',
    'created': 'init_done_created',
    'failed': 'init_done_no_bounce',
}
