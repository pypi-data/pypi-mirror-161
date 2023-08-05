import numpy as np


def extract_permeability(init):
    permx = get_keyword("PERMX", init)
    permy = get_keyword("PERMY", init)
    permz = get_keyword("PERMZ", init)
    return permx, permy, permz


def extract_transmissibility(init):
    tranx = get_keyword("TRANX", init)
    trany = get_keyword("TRANY", init)
    tranz = get_keyword("TRANX", init)
    return tranx, trany, tranz


def extract_d(init):
    dx = get_keyword("DX", init)
    dy = get_keyword("DY", init)
    dz = get_keyword("DZ", init)
    return dx, dy, dz


def extract_regions(init):
    satnum = get_keyword("SATNUM", init)
    pvtnum = get_keyword("PVTNUM", init)
    eqlnum = get_keyword("EQLNUM", init)
    rocknum = get_keyword("ROCKNUM", init)
    return satnum, pvtnum, eqlnum, rocknum


def extract_props(init):
    swl = get_keyword("SWL", init)
    sowcr = get_keyword("SOWCR", init)
    swatinit = get_keyword("SWATINIT", init)
    return swl, sowcr, swatinit


def preprocess(init, endpoint=False):
    poro = get_keyword("PORO", init)
    porv = get_keyword("PORV", init)
    ntg = get_keyword("NTG", init)
    depth = get_keyword("DEPTH", init)
    permx, permy, permz = extract_permeability(init)
    tranx, trany, tranz = extract_transmissibility(init)
    dx, dy, dz = extract_d(init)
    satnum, pvtnum, eqlnum, rocknum = extract_regions(init)

    result_obj = {
        "depth": depth,
        "permx": permx,
        "permy": permy,
        "permz": permz,
        "tranx": tranx,
        "trany": trany,
        "tranz": tranz,
        "poro": poro,
        "porv": porv,
        "ntg": ntg,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "satnum": satnum,
        "pvtnum": pvtnum,
        "eqlnum": eqlnum,
        "rocknum": rocknum,
    }

    if endpoint:
        swl, sowcr, swatinit = extract_props(init)
        result_obj["swl"] = swl
        result_obj["sowcr"] = sowcr
        result_obj["swatinit"] = swatinit

    return result_obj


def get_keyword(keyword, init_file):
    try:
        return init_file.iget_named_kw(keyword, 0).numpy_copy()
    except:
        return np.empty(1)
