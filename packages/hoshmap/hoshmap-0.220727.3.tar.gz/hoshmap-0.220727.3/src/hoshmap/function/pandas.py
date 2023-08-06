def series2df(measures):
    import pandas as pd

    allseries = list(measures.values())
    try:
        table = pd.concat(allseries, axis=1)
        result = table
    except ValueError as e:
        if str(e) == "All objects passed were None":
            result = ...
        else:
            raise Exception(str(e))
    return result


def mseries2df(k, measures):
    if (df := series2df(measures)) is ...:
        return ...
    return k, df
