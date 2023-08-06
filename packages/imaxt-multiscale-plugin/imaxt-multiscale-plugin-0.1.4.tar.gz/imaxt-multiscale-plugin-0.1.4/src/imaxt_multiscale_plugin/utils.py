import numpy as np
from astropy.visualization import PercentileInterval


def get_display_range(arr, percentile=99):
    p = PercentileInterval(percentile)
    p_limits = {
        c: p.get_limits(arr.sel(channel=c).data.ravel().clip(0, 1000000))
        for c in arr.channel.values
    }
    p1 = np.array([*[p[0] for p in p_limits.values()]])[..., None, None]
    p2 = np.array([*[p[1] for p in p_limits.values()]])[..., None, None]
    return p1, p2
