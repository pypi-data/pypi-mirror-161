import numpy as np
from ecl.eclfile import EclKW


def get_keyword(keyword, grdecl):
    try:
        return EclKW.read_grdecl(grdecl, keyword).numpy_copy().astype(int)
    except:
        return np.empty(1)


def preprocess(grdecl, mapping):
    return {keyword.get("name").lower(): get_keyword(keyword.get("source"), grdecl) for keyword in mapping}
