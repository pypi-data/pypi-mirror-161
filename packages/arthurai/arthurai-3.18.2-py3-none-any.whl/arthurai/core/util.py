import json
import logging
import os
from pathlib import Path
import re
from typing import Dict, Optional, Union, Any, List, Sequence, Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype, is_datetime64_any_dtype, is_float_dtype

import arthurai.util as arthur_util
from arthurai.common.constants import ValueType
from arthurai.common.exceptions import InternalValueError, InternalTypeError, UserTypeError

logger = logging.getLogger(__name__)


def retrieve_parquet_files(directory_path: str) -> List[Path]:
    """Checks whether a given directory and its subdirectories contain parquet files,
    if so this will return a list of the files

    :param directory_path:    local path to check files types

    :return: List of paths for parquet files that are found
    """
    parquet_files = []
    for path, subdir, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.parquet'):
                parquet_files.append(Path(os.path.join(path, file)))
    return parquet_files


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    @staticmethod
    def convert_value(obj):
        """Converts the given object from a numpy data type to a python data type, if the object is already a
        python data type it is returned

        :param obj: object to convert
        :return: python data type version of the object
        """
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64,
                            np.long, np.longlong)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, float) and np.isnan(obj):
            return None
        return obj


def standardize_pd_obj(data: Union[pd.DataFrame, pd.Series], dropna: bool, replacedatetime: bool,
                       attributes: Optional[Dict[str, Union[str, ValueType]]] = None) -> Union[pd.DataFrame, pd.Series]:
    """Standardize pandas object for nans and datetimes.
    
    Standardization includes casting correct type for int columns that are float due to nans and 
    for converting datetime objects into isoformatted strings.

    :param data: the pandas data to standardize
    :param dropna: if True, drop nans from numeric date columns
    :param replacedatetime: if True, replace timestamps with isoformatted strings
    :param attributes: if used for sending inferences, will handle column type conversions for columns with any nulls


    :return: the standardized pandas data
    :raises TypeError: timestamp is not of type `datetime.datetime`
    :raises ValueError: timestamp is not timezone aware and no location data is provided to remedy
    """

    def standardize_pd_series(series: pd.Series, datatype: Optional[str]) -> pd.Series:
        series = series.replace([np.inf, -np.inf], np.nan)
        nans_present = series.isnull().values.any()
        if dropna:
            series = series.dropna()

        if len(series) == 0:
            return series

        # Case 1: int column which has nans and there therefore seen as a float column
        if is_float_dtype(series) and nans_present and datatype == ValueType.Integer:
            valid_series = series.dropna()
            if len(valid_series) > 0 and np.array_equal(valid_series, valid_series.astype(int)):
                return series.astype(pd.Int64Dtype())
        # Case 2: datetime column or string column which are all datetime objects
        elif is_datetime64_any_dtype(series) or \
                (is_string_dtype(series) and arthur_util.datetime_valid(series.values[0])):
            formatted_series = series.apply(arthur_util.format_timestamp)
            if replacedatetime:
                return formatted_series

        return series

    if isinstance(data, pd.Series):
        datatype = None
        if attributes and data.name in attributes:
            datatype = attributes[data.name]
        return standardize_pd_series(data, datatype)

    elif isinstance(data, pd.DataFrame):
        if dropna:
            raise InternalValueError(f"Cannot use dropna={dropna} with data argument as pd.DataFrame.")
        df = data.copy()
        for column in df.columns:
            datatype = None
            if attributes and column in attributes:
                datatype = attributes[column]
            df[column] = standardize_pd_series(df[column], datatype)
        return df

    else:
        raise InternalTypeError("Cannot standardize object that is not pd.DataFrame or pd.Series.")


def dataframe_like_to_list_of_dicts(data: Union[List[Dict[str, Any]], Dict[str, List[Any]], pd.DataFrame]):
    """
    Standardize data in a List of Dicts format (e.g. `[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]`). Input can be formatted as
    a List of Dicts, Dict of Lists (e.g. `{'a': [1, 3], 'b': [2, 4]}`), or a Pandas DataFrame. May return the same
    object as input if it already matches the correct format.
    :param data: the input data to format
    :return: the data restructured as a Dict of Lists
    :raises UserTypeError: if the data is in an unexpected format
    """
    if len(data) == 0:
        return []

    if isinstance(data, list) and isinstance(data[0], dict):
        return data
    elif isinstance(data, dict):
        data = pd.DataFrame(data)

    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient='records')
    else:
        raise UserTypeError(f"Invalid input type {type(data)}, should be list of dicts, dict of lists, or DataFrame")


def update_column_in_list_of_dicts(data: List[Dict[str, Any]], target_column: str, column_values: Sequence[Any]) -> \
        None:
    """
    Adds column_values to target_column in a list of dicts **in place**. If values are present for target_column, they are
    overwritten.
    :param data: the List of Dict data to modify
    :param target_column: the name of the column to write values into
    :param column_values: the values to write
    :return: None (in place)
    :raises UserValueError: if the lengths don't match or aren't retrievable
    """
    try:
        if len(column_values) != len(data):
            raise ValueError(f"The dataset has {len(data)} elements but column {target_column} has "
                             f"{len(column_values)} elements. Cannot add values to data.")
    except TypeError:
        raise UserTypeError(f"Cannot compare lengths of data and values for column {target_column}, are you sure the "
                            "values have a definite length?")
    for i in range(len(data)):
        data[i][target_column] = column_values[i]


def intersection_is_non_empty(iter1: Iterable[Any], iter2: Iterable[Any]):
    """
    Returns True if the two iterables share at least one element
    :param iter1:
    :param iter2:
    :return:
    """
    for val in iter1:
        if val in iter2:
            return True
    return False
