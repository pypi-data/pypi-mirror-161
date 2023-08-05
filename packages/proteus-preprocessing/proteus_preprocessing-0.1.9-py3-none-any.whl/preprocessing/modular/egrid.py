import numpy as np


def extract_logic(egrid):
    logic = egrid.export_actnum().numpyCopy()
    return logic


def preprocess(egrid):
    """Extracts logic and grid dimension information from an EclGrid object

    Args:
        egrid (EclGrid): the EclGrid object

    Returns:
        {np.array, np.array}: a dictionary with the logic and dimension numpy arrays
    """
    logic = extract_logic(egrid)

    return {"logic": logic}
