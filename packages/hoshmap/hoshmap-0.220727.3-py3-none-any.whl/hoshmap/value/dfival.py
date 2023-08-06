#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the hoshmap project.
#  Please respect the license - more about this in the section (*) below.
#
#  hoshmap is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hoshmap is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hoshmap.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
import pickle
from typing import Union

from hosh import Hosh

from hoshmap.value import StrictiVal
from hoshmap.value.cacheableival import CacheableiVal


class DFiVal(CacheableiVal):
    """
    Lazy value of a pandas DataFrame or Series, keeping columns lazy when fetching from cache
    """

    def __init__(self, value, id: Union[str, Hosh] = None, caches=None):
        super().__init__(caches)
        self.value = value
        self.deps = {"TODO": "TODO"}  # TODO: put all series fields (strictsivals) here
        if id is None:
            try:
                self.hosh = Hosh(pickle.dumps(value, protocol=5))
            except TypeError as e:
                raise Exception(f"Cannot pickle: {e}")
        else:
            self.hosh = self.handle_id(id)
        self.results = {self.hosh.id: value}

    def replace(self, **kwargs):
        dic = dict(value=self.value, id=self.hosh, caches=self.caches)
        dic.update(kwargs)
        return DFiVal(**dic)

    # TODO: implementar 'def value'


# def column2np(df, colname):
#     import numpy as np
#     ar = df[colname].array
#     return np.reshape(ar, newshape=(df.shape[0],1))


def explode_df(df):
    """
    >>> from pandas import DataFrame
    >>> from hoshmap import idict
    >>> df = DataFrame({"x": [1,2,3], "y": [5,6,7]}, index=["a", "b", "c"])
    >>> d = idict(df=df)
    >>> d.df_.show(colored=False)
    {
        index: "«{'a': 'a', 'b': 'b', 'c': 'c'}»",
        x: "«{'a': 1, 'b': 2, 'c': 3}»",
        y: "«{'a': 5, 'b': 6, 'c': 7}»",
        _id: "CO3m4w1vqM.etZXkoHQoNxA.PS.kQI-LomW.H6VC",
        _ids: {
            index: "HBNoEs58wCDhsdWWisp0sjMwsWmNMXuwaGFE9UAt",
            x: "3F.7UkfLr2tpB-FxATaRJYIpbYpg9oa1r5M31M0j",
            y: "bqYjHGDn-brebdANtxtNo4OkpOXfDwwVYejlzo4t"
        }
    }
    >>> d.df
       x  y
    a  1  5
    b  2  6
    c  3  7
    """
    from hoshmap import FrozenIdict

    dic = {"index": df.index.to_series()}
    for col in df:
        dic[str(col)] = df[col]
    d = FrozenIdict(dic)
    return DFiVal(df, d.hosh), StrictiVal(d, d.hosh)
