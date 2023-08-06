
#cython: language_level=3

import numpy as np
cimport numpy as np


def _parse_energy(fname, usecols):
    energy = []
    with open(fname, 'r') as handle:
        for line in handle:
            if line.startswith('ENERGY'):
                energy.append([float(word) for word in line.split()[1:]])
    return np.array(energy)[:, usecols]


def _parse_etitle(fname):
    etitle = ['ts', 'bond', 'angle', 'dihed', 'imprp', 'elect', 'vdw', 'boundary', 'misc', 'kinetic', 'total',
              'temp', 'potential', 'total3', 'tempavg', 'pressure', 'gpressure', 'volume', 'pressavg', 'gpressavg']
    with open(fname, 'r') as handle:
        for line in handle:
            if line.startswith('ETITLE'):
                etitle = line.lower().split()[1:]
                break
            elif line.startswith('ENERGY'):
                break
    return np.array(etitle)

