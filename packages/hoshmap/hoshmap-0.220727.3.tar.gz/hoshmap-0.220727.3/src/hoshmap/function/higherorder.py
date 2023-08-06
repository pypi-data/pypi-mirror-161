from hoshmap import Let
from hoshmap.serialization.parsing import f2hosh


def dmap(f, field, in_out, aslist=False):
    """Apply 'f' to every element in dict 'field'

    Assume the pair key-element are the first two args of 'f'.
    'f' should receive and return key-value tuples.
    'field' should not apper inside 'in_out'.

    If 'aslist=True', the mapping is from dict to list.
    Ignore entries which result in '...'.
    """
    let = Let(f, in_out)
    input, outstr = let.input, let.outstr
    if let.parsed:
        it = iter(input.items())
        next(it)
        next(it)
        instr = " ".join(f"{k}:{v}" for k, v in it)
    else:
        instr = let.instr
    instr = f"{field}:collection{(' ' + instr) if instr else ''}"

    def fun(collection, **kwargs):
        if aslist:
            lst = []
            for k, v in collection.items():
                ret = f(k, v, **kwargs)
                if ret is not ...:
                    lst.append(ret)
            return lst
        else:
            dic = {}
            for k, v in collection.items():
                ret = f(k, v, **kwargs)
                if ret is not ...:
                    k, v = ret
                    dic[k] = v
            return dic

    fun.hosh = b"dmap()" * f2hosh(f)
    return fun, f"{instr}→{outstr}"


def lmap(f, field, in_out, asdict=False):
    """Apply 'f' to every element in list 'field'

    Assume the element goes as the first arg of 'f'.
    It should not apper inside 'in_out'.

    if 'asdict=True', f should return key-value tuples.
    Ignore entries which result in '...'.
    """
    let = Let(f, in_out)
    input, outstr = let.input, let.outstr
    if let.parsed:
        it = iter(input.items())
        next(it)
        instr = " ".join(f"{k}:{v}" for k, v in it)
    else:
        instr = let.instr
    instr = f"{field}:collection{(' ' + instr) if instr else ''}"

    def fun(collection, **kwargs):
        if asdict:
            dic = {}
            for item in collection:
                ret = f(item, **kwargs)
                if ret is not ...:
                    k, v = ret
                    dic[k] = v
            return dic
        else:
            lst = []
            for item in collection:
                ret = f(item, **kwargs)
                if ret is not ...:
                    lst.append(ret)
            return lst

    fun.hosh = b"lmap()" * f2hosh(f)
    return fun, f"{instr}→{outstr}"
