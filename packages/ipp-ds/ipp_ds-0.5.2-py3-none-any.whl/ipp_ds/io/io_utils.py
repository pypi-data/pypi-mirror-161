import pyexcelerate
import itertools
import numpy as np

def pyx_to_excel(df, workbook_or_filename, sheet_name='Sheet1', index=False, header=True, na_rep='', inf_rep='inf'):

    """
    Write DataFrame to excel file using pyexelerate library
    """

    if not isinstance(workbook_or_filename, pyexcelerate.Workbook):
        location = workbook_or_filename
        workbook_or_filename = pyexcelerate.Workbook()
    else:
        location = None

    chain = []

    df = df.fillna(na_rep).replace({np.inf: inf_rep, -np.inf: f'-{inf_rep}'})

    index_headers = df.index.names
    cols = df.columns.values
    ind = df.index.values
    values = df.values

    if header:
        if index:
            chain.append(np.stack(index_headers, cols, axis=1).tolist())
        chain.append(cols.tolist())

    if index:
        chain.append(np.stack(ind, values, axis=1).tolist())
    chain.append(values.tolist())

    workbook_or_filename.new_sheet(sheet_name, data=itertools.chain(*chain))

    if location:
        workbook_or_filename.save(location)
