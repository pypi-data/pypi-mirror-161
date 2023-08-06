"""
read.py
language: Python3
author: C. Lockhart <clockha2@gmu.edu>
"""

from namdtools.core import Log


# Read output from NAMD run
# Convert to object? Store raw output?
def read_log(fname, glob=None, usecols=None):
    """
    Read output from NAMD.

    Parameters
    ----------
    fname : str
        Name of NAMD output file.
    glob : bool or dict
        Does `fname` need to be globbed? If a boolean, uses :ref:`glob`. If dictionary, uses :ref:`vglob`.
        (Default: None)
    usecols : list-like or callable
        (Optional) Specify columns to return.

    Returns
    -------
    Log
    """

    # Import to save time
    from functools import partial
    import pandas as pd

    # If glob, change fname to include all globbed files
    if glob:
        from pathogen import Path, vglob  #

        # Convert glob to a empty dictionary if necessary
        if not isinstance(glob, dict):
            glob = {}

        # Glob first; if glob is empty, throw an error
        fname_glob = vglob(fname, errors='raise', **glob)
        if not fname_glob:
            raise FileNotFoundError(fname)

        # Sort glob
        # fnames = sorted(fname_glob)
        fnames = fname_glob
    else:
        fnames = [fname]

    # Cycle over fnames and read in
    # df = None
    # for fname in fnames:
    #     data = _read_log(fname)
    #     if df is None:
    #         df = data
    #     else:
    #         df = pd.concat([df, data], ignore_index=True)
    data = list(map(partial(_read_log, usecols=usecols), fnames))
    if glob:
        data = [table.assign(**Path(fname).metadata) for fname, table in zip(fnames, data)]  # noqa

    # Concatenate
    data = data[0] if len(data) == 1 else pd.concat(data, ignore_index=True)

    # Return
    return Log(data)


# TODO make a Cython backend? Or a C backend? This is still slow.
def _read_log(fname, usecols=None):
    """
    Read NAMD output file.

    Parameters
    ----------
    fname : str
        Name of NAMD output file.
    usecols : list-like or callable
        (Optional) Specific columns to read in.

    Returns
    -------
    pandas.DataFrame
    """

    # # Import relevant packages
    # import numpy as np
    # import pandas as pd
    # import re
    #
    # # Read in entire log file
    # with open(fname) as stream:
    #     records = stream.read()
    #
    # # Find ETITLE, we only need the first record. Otherwise, guess that ETITLE follows standard format
    # etitle_start = records.find('ETITLE')
    # if etitle_start >= 0:
    #     etitle_end = records.find('ENERGY', etitle_start)
    #     etitle = records[etitle_start:etitle_end].lower().split()[1:]  # first column is ETITLE
    # else:
    #     etitle = ['ts', 'bond', 'angle', 'dihed', 'imprp', 'elect', 'vdw', 'boundary', 'misc', 'kinetic', 'total',
    #               'temp', 'potential', 'total3', 'tempavg', 'pressure', 'gpressure', 'volume', 'pressavg', 'gpressavg']
    #
    # # Convert usecols to integer if collection of strings
    # if usecols is not None:
    #     usecols = np.array(usecols)
    #     if issubclass(usecols.dtype.type, str):
    #         usecols = np.flatnonzero(np.in1d(etitle, usecols))
    # else:
    #     usecols = np.arange(len(etitle))
    #
    # # Extract only ENERGY records, then generate numpy array. We skip the first column which is ENERGY
    # energy_records = re.sub(r'^(?!ENERGY).*$', '', records, flags=re.MULTILINE)  #.split('\n')
    # energy_records = re.split('\n+', energy_records.strip())  # might be unnecessary
    # energy = np.genfromtxt(energy_records, autostrip=True, usecols=usecols+1)
    #
    # # Return as DataFrame
    # return pd.DataFrame(energy, columns=np.array(etitle)[usecols])  # .set_index(etitle[0])

    # Import relevant packages
    from namdtools.io._read_utils import _parse_energy, _parse_etitle
    import numpy as np
    import pandas as pd

    # Parse etitle
    etitle = _parse_etitle(fname)

    # Convert usecols to integer if collection of strings
    if usecols is not None:
        usecols = np.array(usecols)
        if issubclass(usecols.dtype.type, str):
            usecols = np.flatnonzero(np.in1d(etitle, usecols))
    else:
        usecols = np.arange(len(etitle))

    # Parse energy
    energy = _parse_energy(fname, usecols)

    # Return as DataFrame
    return pd.DataFrame(energy, columns=etitle[usecols])


def _read_log_old(fname):
    """


    Parameters
    ----------
    fname : str
        Name of NAMD output file.

    Returns
    -------

    """

    # Import pandas if not already loaded (to speed up namdtools in general)
    import pandas as pd

    # Initialize DataFrame information
    columns = None
    records = []

    # Read through log file and extract energy records
    # TODO read in with regex
    with open(fname, 'r') as stream:
        for line in stream.readlines():
            # Read first ETITLE
            if columns is None and line[:6] == 'ETITLE':
                columns = line.lower().split()[1:]

            # Save each energy record
            if line[:6] == 'ENERGY':
                records.append(line.split()[1:])

    # What if our file doesn't contain ETITLE? Should this return an error, or can we assume the columns?
    columns = ['ts', 'bond', 'angle', 'dihed', 'imprp', 'elect', 'vdw', 'boundary', 'misc', 'kinetic', 'total',
               'temp', 'potential', 'total3', 'tempavg', 'pressure', 'gpressure', 'volume', 'pressavg', 'gpressavg']

    # Return DataFrame
    return pd.DataFrame(records, columns=columns).set_index(columns[0]).astype(float)
