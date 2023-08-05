def preprocess(x):
    swat = x.iget_named_kw("SWAT", 0).numpy_copy()
    pressure = x.iget_named_kw("PRESSURE", 0).numpy_copy()

    return {"swat": swat, "pressure": pressure}
