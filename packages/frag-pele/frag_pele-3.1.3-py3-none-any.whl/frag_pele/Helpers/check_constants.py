import os
import frag_pele.constants as cs


def check():
    if not os.path.exists(cs.SCHRODINGER):
        raise OSError("Schrodinger path {} not found. Change the harcoded path under frag_pele/constants.py".format(cs.SCHRODINGER))
    if not os.path.exists(cs.PATH_TO_PELE):
        raise OSError("Pele path {} not found. Change the harcoded path under frag_pele/constants.py".format(cs.PATH_TO_PELE))
    elif cs.PATH_TO_PELE_DATA != None:
        if not os.path.exists(cs.PATH_TO_PELE_DATA):
            raise OSError("Pele data path {} not found. Change the harcoded path under frag_pele/constants.py".format(cs.PATH_TO_PELE_DATA))
    elif cs.PATH_TO_PELE_DOCUMENTS != None:
        if not os.path.exists(cs.PATH_TO_PELE_DOCUMENTS):
            raise OSError("Pele documents path {} not found. Change the harcoded path under frag_pele/constants.py".format(cs.PATH_TO_PELE_DOCUMENTS))
    elif not os.path.exists(cs.PATH_TO_LICENSE):
        raise OSError("Pele license path {} not found. Change the harcoded path under frag_pele/constants.py".format(cs.PATH_TO_LICENSE))
