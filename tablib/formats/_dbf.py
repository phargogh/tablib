# -*- coding: utf-8 -*-

""" Tablib - DBF Support.
"""
from types import IntType, FloatType
import tempfile

from tablib.compat import StringIO
import dbfpy
from dbfpy import dbf
from dbfpy import dbfnew
from dbfpy import record as dbfrecord


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
        if type(field_value) in [IntType, FloatType]:
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
    stream = StringIO(open(temp_uri, 'rbU').read())
    return stream.getvalue()

def import_set(dset, in_stream, headers=True):
    """Returns a dataset from a DBF stream."""

    dset.wipe()
    _dbf = dbf.Dbf(StringIO(in_stream))
    dset.headers = _dbf.fieldNames
    for record in range(_dbf.recordCount):
        row = [_dbf[record][f] for f in _dbf.fieldNames]
        dset.append(row)

def detect(stream):
    """Returns True if the given stream is valid DBF"""
    #_dbf = dbf.Table(StringIO(stream))
    try:
        _dbf = dbf.Dbf(StringIO(stream), readOnly=True)
        return True
    except ValueError:
        # When we try to open up a file that's not a DBF, dbfpy raises a
        # ValueError.
        return False



