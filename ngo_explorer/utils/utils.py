import re
import urllib.parse
from typing import Any, overload

import titlecase


def get_scaling_factor(value: int | float) -> tuple[int, str, str]:
    # @TODO: translation...
    if value > 2000000000:
        return (1000000000, "{:,.1f} billion", "{:,.1f}bn")
    elif value > 1500000:
        return (1000000, "{:,.1f} million", "{:,.1f}m")
    else:
        return (1, "{:,.0f}", "{:,.0f}")


def scale_value(value: int | float, abbreviate: bool = False) -> str:
    scale = get_scaling_factor(value)
    if abbreviate:
        return scale[2].format(value / scale[0])
    else:
        return scale[1].format(value / scale[0])


def update_url_values(url: str, values: dict) -> str:
    # update an url to include additional query parameters
    # changes the values if they're already present
    o = urllib.parse.urlparse(url)
    if o.query:
        query = urllib.parse.urlencode(
            {
                **urllib.parse.parse_qs(o.query),
                **values,
            },
            doseq=True,
        )
    else:
        query = urllib.parse.urlencode(values, doseq=True)

    return urllib.parse.urlunparse(
        (o.scheme, o.netloc, o.path, o.params, query, o.fragment)
    )


def record_to_nested(fields: list[str]) -> dict[str, dict]:
    fields_split = [f.split(".") for f in fields]
    new_fields = {}
    for f in fields_split:
        this_field = new_fields
        for i in f:
            if i not in this_field:
                this_field[i] = {}
            this_field = this_field[i]
    return new_fields


# from https://github.com/pandas-dev/pandas/blob/v0.24.0/pandas/io/json/normalize.py#L28-L96
# used under BSD licence
@overload
def nested_to_record(
    ds: dict, prefix: str = "", sep: str = ".", level: int = 0
) -> dict[str, Any]: ...
@overload
def nested_to_record(
    ds: list[dict], prefix: str = "", sep: str = ".", level: int = 0
) -> list[dict[str, Any]]: ...
def nested_to_record(
    ds: dict | list[dict], prefix: str = "", sep: str = ".", level: int = 0
) -> dict[str, Any] | list[dict[str, Any]]:
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
        new_d = {}
        for k, v in d.items():
            # each key gets renamed with prefix
            if not isinstance(k, str):
                k = str(k)
            if prefix:
                newkey = prefix + sep + k
            else:
                newkey = k

            # only dicts gets recurse-flattend
            if isinstance(v, dict):
                new_d.update(nested_to_record(v, newkey, sep, level + 1))
            else:
                new_d[newkey] = v
        new_ds.append(new_d)

    if singleton:
        return new_ds[0]

    return new_ds


def correct_titlecase(s: str, first_upper=True) -> str:
    if not s:
        return s

    substitutions = [
        (r"\b([^aeiouyAEIOUY,0-9]+)\b", lambda x: x[0].upper() if x[0] else x),
        (r"\'S\b", "'s"),
        (r"\'T\b", "'t"),
        (r"\bOf\b", "of"),
        (r"\bThe\b", "the"),
        (r"\bFor\b", "for"),
        (r"\bAnd\b", "and"),
        (r"\bIn\b", "in"),
        (r"\bWith\b", "with"),
        (r"\bTo\b", "to"),
        (r"\bUk\b", "UK"),
        (r"\bSt\b", "St"),
        (r"([0,4-9])Th\b", r"\1th"),
        (r"1St\b", "1st"),
        (r"2Nd\b", "2nd"),
        (r"3Rd\b", "3rd"),
        (r"\bmr\b", "Mr"),
        (r"\bmrs\b", "Mrs"),
        (r"\bltd\b", "Ltd"),
        (r"\bdr\b", "Dr"),
        (r"\bdrs\b", "Drs"),
        (r"\bcwm\b", "Cwm"),
        (r"\bClwb\b", "Clwb"),
    ]

    for pattern, replacement in substitutions:
        try:
            s = re.sub(pattern, replacement, s, flags=re.IGNORECASE)
        except re.error:
            continue

    if first_upper:
        s = s[0].upper() + s[1:]
    return s


VOWELS = re.compile("[AEIOUYaeiouy]")
ORD_NUMBERS_RE = re.compile(r"([0-9]+(?:st|nd|rd|th))")
SENTENCE_SPLIT = re.compile(r"(\. )")


def title_exceptions(word: str, **kwargs) -> str | None:
    word_test = word.strip("(){}<>.")

    # lowercase words
    if word_test.lower() in ["a", "an", "of", "the", "is", "or"]:
        return word.lower()

    # uppercase words
    if word_test.upper() in [
        "UK",
        "FM",
        "YMCA",
        "PTA",
        "PTFA",
        "NHS",
        "CIO",
        "U3A",
        "RAF",
        "PFA",
        "ADHD",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "AFC",
        "CE",
        "CIC",
    ]:
        return word.upper()

    # words with no vowels that aren't all uppercase
    if word_test.lower() in [
        "st",
        "mr",
        "mrs",
        "ms",
        "ltd",
        "dr",
        "cwm",
        "clwb",
        "drs",
    ]:
        return word_test.title()

    # words with number ordinals
    if bool(ORD_NUMBERS_RE.search(word_test.lower())):
        return word.lower()

    # words with dots/etc in the middle
    for s in [".", "'", ")"]:
        dots = word.split(s)
        if len(dots) > 1:
            # check for possesive apostrophes
            if s == "'" and dots[-1].upper() == "S":
                return s.join(
                    [
                        titlecase.titlecase(i, callback=title_exceptions)
                        for i in dots[:-1]
                    ]
                    + [dots[-1].lower()]
                )
            # check for you're and other contractions
            if word_test.upper() in ["YOU'RE", "DON'T", "HAVEN'T"]:
                return s.join(
                    [
                        titlecase.titlecase(i, callback=title_exceptions)
                        for i in dots[:-1]
                    ]
                    + [dots[-1].lower()]
                )
            return s.join(
                [titlecase.titlecase(i, callback=title_exceptions) for i in dots]
            )

    # words with no vowels in (treat as acronyms)
    if not bool(VOWELS.search(word_test)):
        return word.upper()

    return None


def to_titlecase(s: str | None, sentence: bool = False) -> str | None:
    if not isinstance(s, str):
        return s

    s = s.strip()

    # if it contains any lowercase letters then return as is
    if not s.isupper() and not s.islower():
        return s

    # if it's a sentence then use capitalize
    if sentence:
        return "".join([sent.capitalize() for sent in re.split(SENTENCE_SPLIT, s)])

    # try titlecasing
    s = titlecase.titlecase(s, callback=title_exceptions)

    # Make sure first letter is capitalise
    return s[0].upper() + s[1:]
