from ecl2df import satfunc, pvt, EclFiles

from pathlib import Path


def extract_pvt(case_loc):
    ecl_files = EclFiles(case_loc)
    return pvt.df(ecl_files)


def extract_relperm(case_loc):
    ecl_files = EclFiles(case_loc)
    return satfunc.df(ecl_files)


def extract_size(case_loc):
    x_files = Path(case_loc).rglob(f"*.X*")
    count = 0
    min = 10000000
    max = -1
    for filepath in x_files:
        num = int(str(filepath).split(".X")[-1])
        count += 1
        if min > num:
            min = num
        elif max < num:
            max = num
    return {"size": count, "min": min, "max": max}


def preprocess(case_input_loc):
    # pvt_props = extract_pvt(case_input_loc)
    # relperm_props = extract_relperm(case_input_loc)
    size_props = extract_size(case_input_loc)
    return {
        # "pvt": pvt_props,
        # "satfunc": relperm_props,
        "info": size_props
    }
