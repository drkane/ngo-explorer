import urllib.parse

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

    
