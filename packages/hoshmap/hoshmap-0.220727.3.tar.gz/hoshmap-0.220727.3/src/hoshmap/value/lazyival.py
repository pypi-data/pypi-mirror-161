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
import operator
from functools import reduce
from itertools import chain
from typing import Iterable, Union

from hosh import Hosh

from hoshmap.serialization.parsing import f2hosh
from hoshmap.value.cacheableival import CacheableiVal


class LazyiVal(CacheableiVal):
    """
    Identified lazy value

    Threefold lazy: It is calculated only when needed, only once and it is cached.

    >>> from hoshmap.value import LazyiVal
    >>> cache = {}
    >>> from hoshmap.value.strictival import StrictiVal
    >>> deps = {"x": StrictiVal(2)}
    >>> lvx = LazyiVal(lambda x: x**2, 0, 1, deps, {}, caches=[cache])
    >>> lvx
    λ(x)
    >>> deps = {"x": lvx, "y": StrictiVal(3)}
    >>> result = {}
    >>> f = lambda x,y: [x+y, y**2]
    >>> lvy = LazyiVal(f, 0, 2, deps, result, caches=[cache])
    >>> lvz = LazyiVal(f, 1, 2, deps, result, caches=[cache])
    >>> lvx, lvy, lvz
    (λ(x), λ(x=λ(x) y), λ(x=λ(x) y))
    >>> deps = {"z": lvz}
    >>> f = lambda z: {"z":z**3, "w":z**5}
    >>> result = {}
    >>> lvz2 = LazyiVal(f, 0, 2, deps, result, caches=[cache])
    >>> lvw = LazyiVal(f, 1, 2, deps, result, caches=[cache])
    >>> lvx, lvy, lvz2, lvw
    (λ(x), λ(x=λ(x) y), λ(z=λ(x=λ(x) y)), λ(z=λ(x=λ(x) y)))
    >>> lvx.value, lvy.value, lvz2.value, lvw.value
    (4, 7, 729, 59049)
    >>> lvz2.id
    'DnEpPaV2RgSFqbiyUvIgF-yM-PRv-ZS5M55oY9D5'
    >>> lvw.id
    'tZhpXFv5YPuwH-2cFvPO2WsTKpwWui2gGHetySo-'
    >>> lvz2.hosh * lvw.hosh == lvz.hosh * lvw.fhosh
    True
    """

    def __init__(
        self,
        f: callable,
        i: int,
        n: int,
        deps: dict,
        results: dict,
        fid: Union[str, Hosh] = None,
        caches=None,
        did=None,
        dids=None,
    ):
        # if i >= len(result):  # pragma: no cover
        #     raise Exception(f"Index {i} inconsistent with current expected result size {len(result)}.")
        super().__init__(caches, did, dids)
        self.f = f
        self.i = i
        self.n = n
        self.deps = {} if deps is None else deps
        self.results = results
        self.fhosh = f2hosh(f) if fid is None else self.handle_id(fid)
        self.hosh = reduce(operator.mul, chain(self.deps.values(), [self.fhosh]))[i:n]
        self.results[self.id] = Unevaluated

    def replace(self, **kwargs):
        dic = dict(f=self.f, i=self.i, n=self.n, deps=self.deps, results=self.results, fid=self.fhosh, caches=self.caches)
        dic.update(kwargs)
        return LazyiVal(**dic)

    @property
    def value(self):
        if not self.isevaluated:
            if (fetched := self.fetch()) is not None:
                return fetched
            self.calculate()
            self.store()
        return self.results[self.id]

    def fetch(self):
        if self.caches is not None:
            from hoshmap import FrozenIdict

            outdated_caches = []
            for cache in self.caches:
                if self.id in cache:
                    for outdated_cache in outdated_caches:
                        outdated_cache[self.did] = {"_ids": self.dids}
                    val = self.traverse(self.id, cache, outdated_caches)
                    # TODO: receber iVal de dentro do cache, nao value
                    # TODO: passar cache pra ele quando for CacheableiVal
                    self.results[self.id] = val
                    return val
                outdated_caches.append(cache)

    def calculate(self):
        from hoshmap import idict

        argidxs = []
        kwargs = {}
        iterable_sources = {}
        for field, ival in self.deps.items():
            if isinstance(field, int):  # quando usa isso???
                argidxs.append(field)
            else:
                if len(split := field.split(":*")) == 2:
                    iterable_sources[split[1]] = iter(self.deps[field].value)
                else:
                    kwargs[field] = ival.value
        if iterable_sources:
            result = []
            loop = True
            while loop:
                i = None
                try:
                    for i, (target, it) in enumerate(iterable_sources.items()):
                        kwargs[target] = next(it)
                    r = self.f(*(self.deps[idx] for idx in sorted(argidxs)), **kwargs)
                    if isinstance(r, idict):
                        r = r.frozen
                    result.append(r)
                except StopIteration:
                    if i not in [0, len(iterable_sources)]:
                        raise ValueError("All iterable fields (e.g., 'xs:*x') should have the same length.")
                    loop = False
        else:
            result = self.f(*(self.deps[idx] for idx in sorted(argidxs)), **kwargs)
            if isinstance(result, idict):
                result = result.frozen
        if self.n == 1:
            result = [result]
        elif isinstance(result, dict):
            result = result.values()
        elif isinstance(result, list) and len(result) != self.n:  # pragma: no cover
            raise Exception(f"Wrong result length: {len(result)} differs from {self.n}")
        if not isinstance(result, Iterable):  # pragma: no cover
            raise Exception(f"Unsupported multi-valued result type: {type(result)}")
        for id, res in zip(self.results, result):
            self.results[id] = res

    def store(self):
        if self.caches is not None:
            from hoshmap import FrozenIdict

            for id, res in self.results.items():
                for cache in self.caches:
                    if self.did not in cache:
                        cache[self.did] = {"_ids": self.dids}
                    if isinstance(res, FrozenIdict):
                        # TODO:
                        #  if res=cacheableival: add current cache to res.'lazies*'.caches caso não tenham
                        #  [não faz sentido picklear caches, então...]
                        #  busca no cache anterior do subdict pelo resultado já pronto (e grava no corrente?)
                        #   senão:
                        #       se cache corrente contém fid, armazena field como lazy
                        #       senão, evaluate nesse field (p/ ser armazenado mais abaixo).
                        #
                        res.evaluate()  # <-- retirar depois de feito TODOs acima
                        if res.id not in cache:
                            # REMINDER: entry id differs from internal did
                            cache[id] = {"_ids": res.ids}
                        res >> [[cache]]
                    elif id not in cache:
                        cache[id] = res

    def traverse(self, id, cache, outdated_caches):
        if id not in cache:
            raise Exception(f"Id {id} not found.")
        val = cache[id]
        for outdated_cache in outdated_caches:
            outdated_cache[id] = val
        if isinstance(val, dict) and list(val.keys()) == ["_ids"]:
            from hoshmap import FrozenIdict

            ids = val["_ids"]
            data = {}
            for k, v in ids.items():
                data[k] = self.traverse(v, cache, outdated_caches)
            return FrozenIdict.fromdict(data, ids)
        return val


class Unevaluated:
    pass


Unevaluated = Unevaluated()
