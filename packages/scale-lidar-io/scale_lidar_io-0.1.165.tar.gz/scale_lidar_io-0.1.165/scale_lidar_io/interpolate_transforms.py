import numpy as np
import pandas as pd

from .transform import Transform


def interpolate_transforms(data: pd.Series) -> pd.Series:
    # This is a mask of the elements that are NaN
    empty = data.isnull().values

    # Position and indexes of empty and valid values
    valid_loc = np.argwhere(~empty).squeeze(axis=-1)
    empty_loc = np.argwhere(empty).squeeze(axis=-1)
    valid_index = data.index[valid_loc].values
    empty_index = data.index[empty_loc].values

    # Missing values before first or after last valid are discarded
    empty_loc = empty_loc[(empty_loc > valid_loc.min()) & (empty_loc < valid_loc.max())]

    # Important bit! This tells you the which valid values must be used as interpolation ends for each missing value
    interp_loc_end = np.searchsorted(valid_loc, empty_loc)
    interp_loc_start = interp_loc_end - 1

    # Values to interpolate
    valid_transforms = data.values[valid_loc]

    for i in range(len(empty_loc)):
        transform_a: Transform = valid_transforms[interp_loc_start[i]]
        transform_b: Transform = valid_transforms[interp_loc_end[i]]
        index_a = valid_index[interp_loc_start[i]]
        index_b = valid_index[interp_loc_end[i]]
        factor = (empty_index[i] - index_a) / (index_b - index_a)
        current_transform = transform_a.interpolate(transform_b, factor)
        data.iloc[empty_loc[i]] = current_transform

    return data
