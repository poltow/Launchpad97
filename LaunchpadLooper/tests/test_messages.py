import unittest

from LaunchpadLooper import Messages as M


class MessagesTest(unittest.TestCase):

    def test_pad_messages_are_one_based(self):
        self.assertEqual('REC  PISTA 1  ESCENA 2', M.text('record', track=0, scene=1))
        self.assertEqual('REC 4 COMPASES  PISTA 3  ESCENA 8',
                         M.text('record_fixed', track=2, scene=7, bars=4))
        self.assertEqual('PLAY  PISTA 1  ESCENA 1', M.text('launch', track=0, scene=0))
        self.assertEqual('STOP YA  PISTA 5', M.text('stop_immediate', track=4))
        self.assertEqual('CIERRA REC  PISTA 1  ESCENA 1', M.text('close_recording', track=0, scene=0))
        self.assertEqual('BORRAR  PISTA 2  ESCENA 3', M.text('delete_clip', track=1, scene=2))
        self.assertEqual('COPIAR  PISTA 2  ESCENA 3', M.text('copy_origin', track=1, scene=2))
        self.assertEqual('PEGADO  PISTA 2  ESCENA 3', M.text('copy_paste', track=1, scene=2))
        self.assertEqual('NO SE PEGA: SLOT OCUPADO', M.text('copy_reject'))
        self.assertEqual('QUANTIZE 1/8T 50%  PISTA 2  ESCENA 3',
                         M.text('quantize_clip', track=1, scene=2, grid='1/8t', amount=0.5))
        self.assertEqual('STOP EN SYNC  PISTA 2', M.text('stop_track', track=1))

    def test_lateral_messages(self):
        self.assertEqual('ESCENA 3', M.text('scene', scene=2, name=''))
        self.assertEqual('ESCENA 3  SNAP', M.text('scene', scene=2, name='SNAP'))
        self.assertEqual('FIXED LENGTH 8 COMPASES', M.text('fixed_length_bars', bars=8))
        self.assertEqual('FIXED LENGTH 1 COMPAS', M.text('fixed_length_bars', bars=1))
        self.assertEqual('QUANTIZE 1/16T 100%', M.text('quantize_setting', grid='1/16t', amount=1.0))
        self.assertEqual('BORRAR FILA 4', M.text('delete_row', scene=3))
        self.assertEqual('STOP EN SYNC  FILA 4', M.text('stop_row', scene=3))

    def test_top_messages(self):
        self.assertEqual('UNDO', M.text('undo'))
        self.assertEqual('REDO', M.text('redo'))
        self.assertEqual('FIXED LENGTH ON  4 COMPASES', M.text('fixed_length', on=True, bars=4))
        self.assertEqual('FIXED LENGTH OFF', M.text('fixed_length', on=False, bars=4))
        self.assertEqual('TAP 120.0 BPM', M.text('tap_tempo', tempo=120.04))
        self.assertEqual('TAP 2/4', M.text('tap_count', count=2, needed=4))
        self.assertEqual('METRONOMO ON', M.text('metronome', on=True))
        self.assertEqual('METRONOMO OFF', M.text('metronome', on=False))
        self.assertEqual('SNAPSHOT EN FILA 8', M.text('snapshot', scene=7))
        self.assertEqual('SNAPSHOT NO: PISTA GRABANDO', M.text('snapshot_reject', reason='recording'))
        self.assertEqual('SNAPSHOT NO: SIN FILA LIBRE', M.text('snapshot_reject', reason='no_free_row'))
        self.assertEqual('INIT: MANTENER 1/2 SEG', M.text('init_pending'))
        self.assertEqual('INIT: GRILLA VACIA, BOUNCE LISTO (UNDO RECUPERA LA GRILLA)', M.text('init_done'))
        self.assertEqual('INIT: GRILLA VACIA, RETORNO BOUNCE CREADO (UNDO RECUPERA LA GRILLA)',
                         M.text('init_done_created'))
        self.assertEqual('INIT: GRILLA VACIA, NO SE PUDO CREAR EL RETORNO BOUNCE', M.text('init_done_no_bounce'))
        self.assertEqual({'taken': 'init_done', 'created': 'init_done_created', 'failed': 'init_done_no_bounce'},
                         M.INIT_DONE_BY_BOUNCE)
        for key in M.INIT_DONE_BY_BOUNCE.values():
            self.assertTrue(M.text(key), key)
        self.assertEqual('LAUNCHPAD LOOPER OK', M.text('ready'))

    def test_press_messages(self):
        self.assertEqual('UNDO  (MANTENER = REDO)', M.text('press_undo'))
        self.assertEqual('FIXED LENGTH  LATERALES = COMPASES', M.text('press_fixed_length'))
        self.assertEqual('DELETE  PAD = CLIP  LATERAL = FILA', M.text('press_delete'))
        self.assertEqual('TAP 1/4  (MANTENER = METRONOMO)', M.text('press_pulse', count=1, needed=4))
        self.assertEqual('', M.text('press_copy_paste_nope'))

    def test_bounce_messages(self):
        self.assertEqual('SNAPSHOT: SOLTAR = FOTO  /  + CLIPS + SLOT VACIO = BOUNCE  /  + CLIP + LATERAL = GAIN',
                         M.text('press_snapshot'))
        self.assertEqual('BOUNCE: 2 CLIPS ELEGIDOS', M.text('bounce_marked', count=2))
        self.assertEqual('BOUNCE 3 CLIPS -> PISTA 5  ESCENA 2  (4 COMPASES)',
                         M.text('bounce_start', count=3, track=4, scene=1, bars=4))
        self.assertEqual('BOUNCE EN CURSO', M.text('bounce_busy'))
        self.assertEqual('BOUNCE CANCELADO', M.text('bounce_cancelled'))
        self.assertEqual('BOUNCE: CIERRA EN EL COMPAS', M.text('bounce_closing'))
        self.assertEqual('BOUNCE LISTO', M.text('bounce_done'))
        self.assertEqual('BOUNCE CORTADO', M.text('bounce_cut'))
        self.assertEqual('BOUNCE: RETORNO CREADO', M.text('bounce_return_created'))

    def test_gain_messages(self):
        self.assertEqual('GAIN  PISTA 1  ESCENA 2: -3.0 DB', M.text('gain', track=0, scene=1, db='-3.0 dB'))
        self.assertEqual('GAIN: TOCAR UN CLIP SONANDO PRIMERO', M.text('gain_no_focus'))
        self.assertEqual('GAIN: ERROR DE LIVE (VER LOG)', M.text('gain_failed'))

    def test_bounce_reject_reasons(self):
        expected = {
            'in_progress': 'BOUNCE NO: YA HAY UNO EN CURSO',
            'recording': 'BOUNCE NO: HAY PISTA GRABANDO',
            'nothing_playing': 'BOUNCE NO: NADA SONANDO',
            'target_occupied': 'BOUNCE NO: DESTINO OCUPADO',
            'target_on_origin_track': 'BOUNCE NO: DESTINO EN PISTA DE ORIGEN',
            'target_not_audio': 'BOUNCE NO: DESTINO NO ES PISTA DE AUDIO',
            'too_long': 'BOUNCE NO: LARGO MAYOR A 64 COMPASES, USAR FIXED LENGTH',
            'no_return_input': 'BOUNCE NO: SIN ENTRADA DESDE RETORNO',
            'no_return': 'BOUNCE NO: SIN RETORNO BOUNCE, HACER INIT (3 DE LA IZQUIERDA)',
            'live_error': 'BOUNCE NO: ERROR DE LIVE (VER LOG)',
        }
        for reason, text in expected.items():
            self.assertEqual(text, M.text('bounce_reject', reason=reason), reason)

    def test_everything_is_uppercase_ascii(self):
        for event in ('record', 'launch', 'scene', 'undo', 'ready', 'press_snapshot', 'bounce_start'):
            out = M.text(event, track=0, scene=0, name='snap', count=1, bars=2)
            self.assertEqual(out, out.upper())
            out.encode('ascii')

    def test_unknown_event_is_empty(self):
        self.assertEqual('', M.text('nope'))


if __name__ == '__main__':
    unittest.main()
