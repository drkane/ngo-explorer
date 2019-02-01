import datetime
import copy

def get_charity_row(c, number_format=True):
    if len(c['countries']) > 10:
        countries = "{:,.0f} countries".format(len(c['countries']))
    else:
        countries = ", ".join(c['countries'])

    income = c.get("income", {}).get(
        "latest", {}).get("total", None)
    if number_format:
        if income is None:
            income = 'Unknown'
        else:
            income = "£{:,.0f}".format(float(income))

    return {
        "Charity Number": c.get("ids", {}).get("GB-CHC", "Unknown"),
        # @TODO: currently DataTable doesn't support HTML in cells
        # "Name": html.A(
        #     href='https://charitybase.uk/charities/{}'.format(
        #         c.get("ids", {}).get("GB-CHC", "Unknown")),
        #     children=c.get("name", "Unknown"),
        #     target="_blank"
        # ),
        "Name": c.get("name", "Unknown"),
        "Income": income,
        "Countries of operation": countries
    }

def date_to_financial_year(datevalue, month_end=4):
    d = datetime.datetime.strptime(datevalue, "%Y-%m-%d")
    if d.month <= month_end:
        return "{}-{}".format(str(d.year-1), str(d.year)[2:4])
    else:
        return "{}-{}".format(str(d.year), str(d.year+1)[2:4])

def get_scaling_factor(value):
    if value > 2000000000:
        return (1000000000, '{:,.1f} billion', '{:,.1f}bn')
    elif value > 1500000:
        return (1000000, '{:,.1f} million', '{:,.1f}m')
    else:
        return (1, '{:,.0f}', '{:,.0f}')


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
