from hoshmap.value.ival import iVal


class CacheableiVal(iVal):
    replace: callable
    deps: dict

    def __init__(self, caches=None, did=None, dids=None):
        self.caches = caches
        self.did = did
        self.dids = dids

    def withcaches(self, caches, did, dids):
        # Only set cache on cacheless CacheableiVal objects
        if self.caches is not None:
            caches = []
        return self.replace(caches=caches, did=did, dids=dids)

    def __repr__(self):
        if not self.isevaluated:
            lst = (k + ("" if dep.isevaluated else f"={repr(dep)}") for k, dep in self.deps.items())
            return f"λ({' '.join(lst)})"
        return repr(self.value)
