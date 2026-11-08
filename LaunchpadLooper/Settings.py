"""Ajustes del script. Modulo puro.

Nada se guarda en disco: cada vez que carga el script, Fixed Length arranca
apagado y en 1 compas, y Quantize en 1/16 al 100%. Los valores elegidos
con los laterales valen hasta cerrar Live o cambiar de script."""

try:
    from . import consts
except (ImportError, ValueError):
    import consts

DEFAULTS = {
    'fixed_length_on': False,
    'fixed_length_bars': 1,
    'quantize_grid': '1/16',
    'quantize_amount': 1.0,
}

VALID = {
    'fixed_length_on': (True, False),
    'fixed_length_bars': consts.FIXED_LENGTH_BARS,
    'quantize_grid': consts.QUANTIZE_GRID_NAMES,
    'quantize_amount': consts.QUANTIZE_AMOUNTS,
}


def _is_valid(key, value):
    if key not in VALID:
        return False
    allowed = VALID[key]
    if key == 'fixed_length_on':
        return value is True or value is False
    for candidate in allowed:
        if value == candidate and type(value) == type(candidate):
            return True
    return False


class Settings(object):

    def __init__(self, log=None):
        self._log = log or (lambda message: None)
        self._values = dict(DEFAULTS)

    def get(self, key):
        return self._values[key]

    def set(self, key, value):
        if not _is_valid(key, value):
            return False
        self._values[key] = value
        return True

    def toggle_fixed_length(self):
        self.set('fixed_length_on', not self._values['fixed_length_on'])
        return self._values['fixed_length_on']

    def fixed_length_index(self):
        return list(consts.FIXED_LENGTH_BARS).index(self._values['fixed_length_bars'])

    def quantize_grid_index(self):
        return list(consts.QUANTIZE_GRID_NAMES).index(self._values['quantize_grid'])

    def quantize_amount_index(self):
        return list(consts.QUANTIZE_AMOUNTS).index(self._values['quantize_amount'])

    def set_fixed_length_index(self, index):
        return self.set('fixed_length_bars', consts.FIXED_LENGTH_BARS[index])

    def set_quantize_grid_index(self, index):
        return self.set('quantize_grid', consts.QUANTIZE_GRID_NAMES[index])

    def set_quantize_amount_index(self, index):
        return self.set('quantize_amount', consts.QUANTIZE_AMOUNTS[index])
