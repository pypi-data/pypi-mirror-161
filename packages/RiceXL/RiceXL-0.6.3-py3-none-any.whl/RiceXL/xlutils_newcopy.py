from xlutils.filter import process, XLRDReader, XLWTWriter

def new_copy(wb):
    w = XLWTWriter()
    process(
        XLRDReader(wb, 'unknown.xls'),
        w
        )
    return w.output[0][1], w.style_list
