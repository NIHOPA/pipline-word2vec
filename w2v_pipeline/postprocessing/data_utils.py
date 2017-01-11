import h5py, sqlite3, os, glob
import pandas as pd
import numpy as np
from tqdm import tqdm

# Required for import from previous path (may fix someday)
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import simple_config
from utils.os_utils import grab_files


def load_h5_file(f_h5, *args):
    '''
    Generically  loads a h5 files top level data structures (assumes
    no nesting). If *args is specified, only the *args subset will be loaded.
    '''
    data = {}
    
    with h5py.File(f_h5,'r') as h5:
        if not args:
            args = h5.keys()
            
        for key in args:
            if key not in h5:
                raise ValueError("{} not found in {}".format(key, f_h5))

        for key in args:
            data[key] = h5[key][:]
            
    return data

def load_dispersion_data():
    print "Loading dispersion data"

    config_post = simple_config.load("postprocessing")

    f_h5 = os.path.join(
        config_post["output_data_directory"],
        "cluster_dispersion.h5")

    return load_h5_file(f_h5)

def load_ORG_data(extra_columns=None):
    print "Loading import data"

    cols = ["_ref",]
    
    if extra_columns is not None:
        cols += extra_columns

    config_import = simple_config.load("import_data")

    # Load the input columns
    F_CSV = grab_files("*.csv", config_import["output_data_directory"])
    ITR = (pd.read_csv(f,usecols=cols) for f in F_CSV)
    df = pd.concat(list(ITR))

    # Require the _refs to be in order as a sanity check    
    if not (np.sort(df._ref) == df._ref).all():
        msg = "WARNING, data out of sort order from _refs"
        raise ValueError(msg)

    df = df.set_index('_ref')
    df['_ref'] = df.index
    
    return df

def load_metacluster_data(*args):

    config_metacluster = simple_config.load("metacluster")

    f_h5 = os.path.join(
        config_metacluster["output_data_directory"],
        config_metacluster["f_centroids"])

    return load_h5_file(f_h5, *args)


def load_document_vectors():
    config_score = simple_config.load("score")
    config_MC = simple_config.load("metacluster")

    score_method = config_MC['score_method']
    text_column  = config_MC['score_column']
    
    f_h5 = os.path.join(
        config_score["output_data_directory"],
        config_score['document_scores']["f_db"],
    )

    with h5py.File(f_h5,'r') as h5:
        g = h5[score_method]

        # Load the _refs
        _refs = g["_ref"][:]
        
        # Require the _refs to be in order as a sanity check
        if not (np.sort(_refs) == _refs).all():
            msg = "WARNING, data out of sort order from _refs"
            raise ValueError(msg)
        
        docv = g["V"][:]

        return {
            "docv" : docv,
            "_refs": _refs
        }

