import unittest

from LaunchpadLooper.ModifierState import ModifierState
from LaunchpadLooper import consts


# Acorde de tres superiores contiguos, como era el setup del bounce antes de
# pasar a los laterales: sirve para probar varios acordes a la vez.
SETUP = ('delete', 'stop', 'copy')
CHORDS = {'init': consts.INIT_CHORD, 'bounce_setup': SETUP}


def make():
    return ModifierState(consts.MODIFIER_NAMES, CHORDS)


def make_grace():
    return ModifierState(consts.MODIFIER_NAMES, CHORDS, grace=0.15,
                         grace_names=('delete', 'stop', 'quantize'))


class ChordsTest(unittest.TestCase):

    def test_held_chord_names_the_chord(self):
        state = make()
        self.assertIsNone(state.held_chord())
        for name in consts.INIT_CHORD:
            state.press(name)
        self.assertEqual('init', state.held_chord())
        self.assertTrue(state.chord_held())

    def test_bounce_setup_chord(self):
        state = make()
        for name in SETUP:
            state.press(name)
        self.assertEqual('bounce_setup', state.held_chord())
        for name in SETUP:
            self.assertIsNone(state.release(name), name)
        self.assertIsNone(state.held_chord())

    def test_single_tuple_still_accepted_as_init(self):
        state = ModifierState(consts.MODIFIER_NAMES, consts.INIT_CHORD)
        for name in consts.INIT_CHORD:
            state.press(name)
        self.assertEqual('init', state.held_chord())


class ActiveModifierTest(unittest.TestCase):

    def test_no_modifier_when_nothing_held(self):
        state = make()
        self.assertIsNone(state.active())

    def test_first_pressed_modifier_wins(self):
        state = make()
        state.press('delete')
        state.press('copy')
        self.assertEqual('delete', state.active())
        state.release('delete')
        self.assertEqual('copy', state.active())

    def test_non_modifier_buttons_are_not_active(self):
        state = make()
        state.press('undo')
        state.press('pulse')
        self.assertIsNone(state.active())
        state.press('stop')
        self.assertEqual('stop', state.active())

    def test_snapshot_is_a_modifier(self):
        state = make()
        state.press('snapshot')
        self.assertEqual('snapshot', state.active())
        self.assertIsNone(state.release('snapshot'))

    def test_is_held(self):
        state = make()
        self.assertFalse(state.is_held('stop'))
        state.press('stop')
        self.assertTrue(state.is_held('stop'))
        state.release('stop')
        self.assertFalse(state.is_held('stop'))


class ReleaseEventsTest(unittest.TestCase):

    def test_short_undo_release_returns_undo(self):
        state = make()
        state.press('undo')
        self.assertEqual('undo', state.release('undo'))

    def test_consumed_undo_release_returns_nothing(self):
        state = make()
        state.press('undo')
        state.consume('undo')
        self.assertIsNone(state.release('undo'))

    def test_release_without_press_returns_nothing(self):
        state = make()
        self.assertIsNone(state.release('undo'))

    def test_fixed_length_release_toggles_when_no_lateral_touched(self):
        state = make()
        state.press('fixed_length')
        self.assertEqual('toggle_fixed_length', state.release('fixed_length'))

    def test_fixed_length_release_does_not_toggle_after_lateral_touch(self):
        state = make()
        state.press('fixed_length')
        state.note_lateral_touch()
        self.assertIsNone(state.release('fixed_length'))

    def test_lateral_touch_is_forgotten_after_release(self):
        state = make()
        state.press('fixed_length')
        state.note_lateral_touch()
        state.release('fixed_length')
        state.press('fixed_length')
        self.assertEqual('toggle_fixed_length', state.release('fixed_length'))

    def test_other_buttons_release_nothing(self):
        state = make()
        for name in ('quantize', 'delete', 'stop', 'copy', 'snapshot', 'pulse'):
            state.press(name)
            self.assertIsNone(state.release(name))


class InitChordTest(unittest.TestCase):

    def test_chord_requires_all_three(self):
        state = make()
        state.press('undo')
        state.press('fixed_length')
        self.assertFalse(state.chord_held())
        state.press('quantize')
        self.assertTrue(state.chord_held())

    def test_chord_consumes_its_buttons(self):
        state = make()
        state.press('undo')
        state.press('fixed_length')
        state.press('quantize')
        state.release('quantize')
        self.assertFalse(state.chord_held())
        self.assertIsNone(state.release('undo'))
        self.assertIsNone(state.release('fixed_length'))

    def test_chord_does_not_consume_other_buttons(self):
        state = make()
        state.press('delete')
        state.press('undo')
        state.press('fixed_length')
        state.press('quantize')
        state.release('delete')
        self.assertFalse(state.is_held('delete'))

    def test_after_chord_released_buttons_work_again(self):
        state = make()
        for name in consts.INIT_CHORD:
            state.press(name)
        for name in consts.INIT_CHORD:
            state.release(name)
        state.press('undo')
        self.assertEqual('undo', state.release('undo'))

    def test_chord_in_any_order(self):
        state = make()
        state.press('quantize')
        state.press('undo')
        state.press('fixed_length')
        self.assertTrue(state.chord_held())


class GhostChordTest(unittest.TestCase):
    """Launchpad MK1 con Delete abajo manda Stop y Copy fantasma: eso
    armaba el acorde de setup e ignoraba los pads. Un modificador en uso
    sobre pads o laterales no puede formar acorde, y un pad con acorde
    abajo lo rompe hasta soltar todos sus botones."""

    def test_pad_touch_blocks_chords_with_used_modifier(self):
        state = make()
        state.press('delete')
        state.note_pad_touch()
        state.press('stop')
        state.press('copy')
        self.assertIsNone(state.held_chord())
        self.assertFalse(state.chord_held())
        self.assertEqual('delete', state.active())

    def test_lateral_touch_also_blocks_chords(self):
        state = make()
        state.press('fixed_length')
        state.note_lateral_touch()
        state.press('undo')
        state.press('quantize')
        self.assertIsNone(state.held_chord())

    def test_used_modifier_is_forgotten_after_release(self):
        state = make()
        state.press('delete')
        state.note_pad_touch()
        state.release('delete')
        for name in SETUP:
            state.press(name)
        self.assertEqual('bounce_setup', state.held_chord())

    def test_pad_touch_without_modifier_changes_nothing(self):
        state = make()
        state.note_pad_touch()
        for name in SETUP:
            state.press(name)
        self.assertEqual('bounce_setup', state.held_chord())

    def test_break_chord_returns_it_and_blocks_it(self):
        state = make()
        for name in SETUP:
            state.press(name)
        self.assertEqual('bounce_setup', state.break_chord())
        self.assertIsNone(state.held_chord())
        self.assertEqual('delete', state.active())

    def test_break_chord_without_chord_returns_none(self):
        state = make()
        state.press('delete')
        self.assertIsNone(state.break_chord())

    def test_broken_chord_stays_broken_while_any_button_held(self):
        state = make()
        for name in SETUP:
            state.press(name)
        state.break_chord()
        state.release('stop')
        state.release('copy')
        state.press('stop')
        state.press('copy')
        self.assertIsNone(state.held_chord(), 'delete sigue abajo')

    def test_broken_chord_works_again_after_full_release(self):
        state = make()
        for name in SETUP:
            state.press(name)
        state.break_chord()
        for name in SETUP:
            state.release(name)
        for name in SETUP:
            state.press(name)
        self.assertEqual('bounce_setup', state.held_chord())

    def test_breaking_one_chord_does_not_block_the_other(self):
        state = make()
        for name in SETUP:
            state.press(name)
        state.break_chord()
        for name in consts.INIT_CHORD:
            state.press(name)
        self.assertEqual('init', state.held_chord())


class GraceTest(unittest.TestCase):
    """Soltar Delete y bajar el pad en el mismo gesto llega al script como
    'release delete' y 16-50 ms despues el pad (Log.txt 2026-10-28 y
    2026-11-02): el clip se paraba en vez de borrarse. El modificador sigue
    activo un rato despues de soltarlo."""

    def test_released_modifier_stays_active_briefly(self):
        state = make_grace()
        state.press('delete')
        state.release('delete', now=10.0)
        self.assertEqual('delete', state.active(now=10.1))
        self.assertIsNone(state.active(now=10.2))

    def test_no_grace_by_default(self):
        state = make()
        state.press('delete')
        state.release('delete', now=10.0)
        self.assertIsNone(state.active(now=10.01))

    def test_grace_only_for_configured_modifiers(self):
        state = make_grace()
        state.press('copy')
        state.release('copy', now=10.0)
        self.assertIsNone(state.active(now=10.05))

    def test_grace_only_for_the_modifier_that_was_active(self):
        state = make_grace()
        state.press('delete')
        state.press('stop')
        state.release('stop', now=10.0)
        self.assertEqual('delete', state.active(now=10.05))
        state.release('delete', now=10.06)
        self.assertEqual('delete', state.active(now=10.1), 'stop nunca fue el activo')

    def test_held_modifier_beats_grace(self):
        state = make_grace()
        state.press('delete')
        state.release('delete', now=10.0)
        state.press('stop')
        self.assertEqual('stop', state.active(now=10.05))

    def test_is_held_ignores_grace(self):
        state = make_grace()
        state.press('delete')
        state.release('delete', now=10.0)
        self.assertFalse(state.is_held('delete'))

    def test_pad_touch_during_grace_does_not_block_chords(self):
        state = make_grace()
        state.press('delete')
        state.release('delete', now=10.0)
        state.note_pad_touch(now=10.05)
        for name in SETUP:
            state.press(name)
        self.assertEqual('bounce_setup', state.held_chord())


if __name__ == '__main__':
    unittest.main()
