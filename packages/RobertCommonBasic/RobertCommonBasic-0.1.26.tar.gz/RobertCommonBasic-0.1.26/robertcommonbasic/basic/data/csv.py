import pandas as pd
from io import StringIO, BytesIO
from typing import Union, Optional


def read_csv(path: Union[str, BytesIO, StringIO], chunksize: Optional[int] = None, parse_dates: bool = False, date_parser: Optional[str] = None, keep_default_na: bool = True, na_values: Optional[list] = None, names: Optional[list] = None, sep: Optional[list] = None, true_values: Optional[list] = None, false_values: Optional[list] = None) -> list:
    results = []
    datas = pd.read_csv(path, chunksize=chunksize, parse_dates=parse_dates, date_parser=date_parser, names=names, sep=sep, true_values=true_values, false_values=false_values, keep_default_na=keep_default_na, na_values=na_values)
    if chunksize is not None:
        for data in datas:
            for index, row in data.iterrows():
                results.append(row.to_dict())
    else:
        for index, row in datas.iterrows():
            results.append(row.to_dict())
    return results