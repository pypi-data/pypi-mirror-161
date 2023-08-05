import pandas as pd
import numpy as np


def dod2df(dod, T=False):
    """
    conver a dict of dicts to a dataframe, sub_dict should have same keys and one dict will be a column

    input:
    dod = {
        'name' : {1:'xyx',2:'fkn'},
        'age' : {1:29,2:27}
    }

    output:
        name    age
    0   xyx     29
    1   fkn     27
    """

    dod_for_pd = {}
    for i in dod:
        dod_for_pd[i] = pd.Series(dod[i])

    return pd.DataFrame(dod_for_pd)


if __name__ == '__main__':
    pass
