import numpy as np
from ecl2df import EclFiles
from preprocessing.deck.section import get_includes


def preprocess(data_file_loc, download_func=None):
    get_includes(data_file_loc, download_func)
    data = EclFiles(data_file_loc)
    ecldeck = data.get_ecldeck()

    return {
        "phases": preprocess_phases(ecldeck),
        "start": preprocess_start(ecldeck),
        "endscale": find_keyword(ecldeck, "ENDSCALE"),
        "multout": find_keyword(ecldeck, "MULTOUT"),
        "dimens": preprocess_dimens(ecldeck),
    }


def preprocess_start(ecldeck):
    from datetime import datetime

    try:
        start = str(ecldeck["START"][0]).strip(" \n/")
        return datetime.strptime(start, "%d '%b' %Y")
    except Exception:
        return False


def preprocess_phases(ecldeck):
    return {
        "gas": find_keyword(ecldeck, "GAS"),
        "oil": find_keyword(ecldeck, "OIL"),
        "water": find_keyword(ecldeck, "WATER"),
    }


def preprocess_dimens(ecldeck):
    dimens = ecldeck["DIMENS"][0]
    return np.array([dimens[0].value, dimens[1].value, dimens[2].value])


def find_keyword(ecldeck, keyword):
    try:
        ecldeck[keyword]
        return True
    except:
        return False
