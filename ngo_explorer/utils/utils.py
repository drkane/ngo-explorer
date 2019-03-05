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

def scale_value(value, abbreviate=False):
    scale = get_scaling_factor(value)
    if abbreviate:
        return scale[2].format(value / scale[0])
    else:
        return scale[1].format(value / scale[0])

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


def record_to_nested(fields: list):
    fields = [f.split(".") for f in fields]
    new_fields = {}
    for f in fields:
        this_field = new_fields
        for i in f:
            if i not in this_field:
                this_field[i] = {}
            this_field = this_field[i]
    return new_fields

    
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
    
    substitutions = [
        (r'\b([^aeiouAEIOU,0-9]+)\b', lambda x: x[0].upper() if x[0] else x),
        (r'\'S\b', "'s"),
        (r'\'T\b', "'t"),
        (r'\bOf\b', "of"),
        (r'\bThe\b', "the"),
        (r'\bFor\b', "for"),
        (r'\bAnd\b', "and"),
        (r'\bIn\b', "in"),
        (r'\bWith\b', "with"),
        (r'\bTo\b', "to"),
        (r'\bUk\b', "UK"),
        (r'\bSt\b', "St"),
        (r'([0,4-9])Th\b', r"\1th"),
        (r'1St\b', "1st"),
        (r'2Nd\b', "2nd"),
        (r'3Rd\b', "3rd"),
        (r'\bmr\b', "Mr"),
        (r'\bmrs\b', "Mrs"),
    ]

    for pattern, replacement in substitutions:
        try:
            s = re.sub(pattern, replacement, s, flags=re.IGNORECASE)
        except:
            continue
    
    s = s[0].upper() + s[1:]
    return s
