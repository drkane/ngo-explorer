
def get_scaling_factor(value):
    if value > 2000000000:
        return (1000000000, '{:,.1f} billion', '{:,.1f}bn')
    elif value > 1500000:
        return (1000000, '{:,.1f} million', '{:,.1f}m')
    else:
        return (1, '{:,.0f}', '{:,.0f}')
