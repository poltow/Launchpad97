import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.dirname(HERE)

FORBIDDEN = [
    (re.compile(r'(?<![\w.])f"'), 'f-string'),
    (re.compile(r"(?<![\w.])f'"), 'f-string'),
    (re.compile(r'\bnonlocal\b'), 'nonlocal'),
    (re.compile(r':='), 'walrus'),
    (re.compile(r'\bsuper\(\)'), 'super() sin argumentos'),
    (re.compile(r'^\s*print\s+[^(\s]', re.M), 'print como sentencia'),
    (re.compile(r'\bexcept\s+\w+\s*,\s*\w+\s*:'), 'except X, e'),
    (re.compile(r'^\s*async\s+def\b', re.M), 'async def'),
    (re.compile(r'\bxrange\('), 'xrange'),
    (re.compile(r'\.iteritems\('), 'iteritems'),
    (re.compile(r'\bdef\s+\w+\([^)]*\)\s*->'), 'anotacion de retorno'),
]


def _source_files():
    for name in sorted(os.listdir(PACKAGE)):
        if name.endswith('.py'):
            yield os.path.join(PACKAGE, name)


class Py2SyntaxTest(unittest.TestCase):

    def test_no_python3_only_syntax(self):
        problems = []
        for path in _source_files():
            with open(path, 'r') as handle:
                text = handle.read()
            for pattern, label in FORBIDDEN:
                if pattern.search(text):
                    problems.append('%s: %s' % (os.path.basename(path), label))
        self.assertEqual([], problems)

    def test_consts_exist(self):
        from LaunchpadLooper import consts
        self.assertEqual(8, consts.GRID_SIZE)
        self.assertEqual((1, 2, 4, 8, 16), consts.FIXED_LENGTH_BARS)
        self.assertEqual(('1/4', '1/8', '1/8t', '1/16', '1/16t'), consts.QUANTIZE_GRID_NAMES)
        self.assertEqual(('undo', 'fixed_length', 'quantize'), consts.INIT_CHORD)
        self.assertEqual({'init': consts.INIT_CHORD}, consts.CHORDS, 'el setup del bounce ya no es acorde de superiores')
        self.assertEqual(('delete', 'stop', 'quantize'), consts.GRACE_MODIFIERS)
        self.assertTrue(0 < consts.MODIFIER_GRACE < 0.5)
