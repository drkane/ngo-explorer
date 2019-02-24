import urllib.parse
import copy
import re

def get_scaling_factor(value):
    if value > 2000000000:
        return (1000000000, '{:,.1f} billion', '{:,.1f}bn')
    elif value > 1500000:
        return (1000000, '{:,.1f} million', '{:,.1f}m')
    else:
        return (1, '{:,.0f}', '{:,.0f}')

def update_url_values(url, values: dict):
    # update an url to include additional query parameters
    # changes the values if they're already present
    o = urllib.parse.urlparse(url)
    if o.query:
        query = urllib.parse.urlencode({
            **urllib.parse.parse_qs(o.query),
            **values,
        }, doseq=True)
    else:
        query = urllib.parse.urlencode(values, doseq=True)
    
    return urllib.parse.urlunparse((
        o.scheme, o.netloc, o.path, o.params, query, o.fragment
    ))

    
# from https://github.com/pandas-dev/pandas/blob/v0.24.0/pandas/io/json/normalize.py#L28-L96
# used under BSD licence
def nested_to_record(ds, prefix="", sep=".", level=0):
    """
    A simplified json_normalize.
    Converts a nested dict into a flat dict ("record"), unlike json_normalize,
    it does not attempt to extract a subset of the data.
    Parameters
    ----------
    ds : dict or list of dicts
    prefix: the prefix, optional, default: ""
    sep : string, default '.'
        Nested records will generate names separated by sep,
        e.g., for sep='.', { 'foo' : { 'bar' : 0 } } -> foo.bar
        .. versionadded:: 0.20.0
    level: the number of levels in the jason string, optional, default: 0
    Returns
    -------
    d - dict or list of dicts, matching `ds`
    Examples
    --------
    IN[52]: nested_to_record(dict(flat1=1,dict1=dict(c=1,d=2),
                                  nested=dict(e=dict(c=1,d=2),d=2)))
    Out[52]:
    {'dict1.c': 1,
     'dict1.d': 2,
     'flat1': 1,
     'nested.d': 2,
     'nested.e.c': 1,
     'nested.e.d': 2}
    """
    singleton = False
    if isinstance(ds, dict):
        ds = [ds]
        singleton = True

    new_ds = []
    for d in ds:

        new_d = copy.deepcopy(d)
        for k, v in d.items():
            # each key gets renamed with prefix
            if not isinstance(k, str):
                k = str(k)
            if level == 0:
                newkey = k
            else:
                newkey = prefix + sep + k

            # only dicts gets recurse-flattend
            # only at level>1 do we rename the rest of the keys
            if not isinstance(v, dict):
                if level != 0:  # so we skip copying for top level, common case
                    v = new_d.pop(k)
                    new_d[newkey] = v
                continue
            else:
                v = new_d.pop(k)
                new_d.update(nested_to_record(v, newkey, sep, level + 1))
        new_ds.append(new_d)

    if singleton:
        return new_ds[0]

    return new_ds

def correct_titlecase(s):
    s = re.sub(r'\'S\b', "'s", s)
    s = re.sub(r'\bOf\b', "of", s)
    s = re.sub(r'\bThe\b', "the", s)
    s = re.sub(r'\bFor\b', "for", s)
    s = re.sub(r'\bAnd\b', "and", s)
    s = re.sub(r'\bIn\b', "in", s)
    s = re.sub(r'\bWith\b', "with", s)
    s = re.sub(r'\bTo\b', "to", s)
    s = re.sub(r'\bUk\b', "UK", s)
    s = s[0].upper() + s[1:]
    return s