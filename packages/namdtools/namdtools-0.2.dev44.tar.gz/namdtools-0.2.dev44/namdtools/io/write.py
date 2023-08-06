
def write_log(log, fname, header=0):
    df = log.copy()
    df.insert(0, 'etitle:', 'ENERGY')
    df.to_csv(fname, sep=' ', header=header, index=None)  # I should probably preserve the format
