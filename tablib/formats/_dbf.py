# -*- coding: utf-8 -*-

""" Tablib - DBF Support.
"""
import tempfile
import struct

from tablib.compat import StringIO
from tablib.packages.dbfpy import dbf
from tablib.packages.dbfpy import dbfnew
from tablib.packages.dbfpy import record as dbfrecord


title = 'dbf'
extensions = ('csv',)

DEFAULT_ENCODING = 'utf-8'

def export_set(dataset):
    """Returns DBF representation of a Dataset"""
    new_dbf = dbfnew.dbf_new()
    temp_file, temp_uri = tempfile.mkstemp()

    # create the appropriate fields based on the contents of the first row
    first_row = dataset[0]
    for fieldname, field_value in zip(dataset.headers, first_row):
        if type(field_value) in [int, float]:
            new_dbf.add_field(fieldname, 'N', 10, 8)
        else:
            new_dbf.add_field(fieldname, 'C', 80)

    new_dbf.write(temp_uri)

    dbf_file = dbf.Dbf(temp_uri, readOnly=0)
    for row in dataset:
        record = dbfrecord.DbfRecord(dbf_file)
        for fieldname, field_value in zip(dataset.headers, row):
            record[fieldname] = field_value
        record.store()

    dbf_file.close()
    if is_py3:
        stream = io.BytesIO(open(temp_uri, 'rb').read())
    else:
        stream = StringIO(open(temp_uri, 'rb').read())
    return stream.getvalue()

def import_set(dset, in_stream, headers=True):
    """Returns a dataset from a DBF stream."""

    dset.wipe()
    if is_py3:
        _dbf = dbf.Dbf(io.BytesIO(in_stream))
    else:
        _dbf = dbf.Dbf(StringIO(in_stream))
    dset.headers = _dbf.fieldNames
    for record in range(_dbf.recordCount):
        row = [_dbf[record][f] for f in _dbf.fieldNames]
        dset.append(row)

def detect(stream):
    """Returns True if the given stream is valid DBF"""
    #_dbf = dbf.Table(StringIO(stream))
    try:
        if is_py3:
            _dbf = dbf.Dbf(io.BytesIO(bytes(stream, 'utf-8')), readOnly=True)
        else:
            _dbf = dbf.Dbf(StringIO(stream), readOnly=True)
        return True
    except (ValueError, struct.error):
        # When we try to open up a file that's not a DBF, dbfpy raises a
        # ValueError.
        # When unpacking a string argument with less than 8 chars, struct.error is
        # raised.
        return False



