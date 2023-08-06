import numpy as np
import pandas as pd
import pyarrow as pa

from .idhash import id_hash as id_hashrs, IDHasher

from typing import List, Union


def id_hash(
    data: Union[pa.Table, pd.DataFrame],
    chunksize: int = 1_024,
    n_cpus: int = 1
) -> int:
    """ Calculate the IDHash for a given Dataset

    Arguments
    ---------
    `data`
        Either the PyArrow Table or Pandas DataFrame to be Hashed
    `chunksize`
        The amount of rows to be included in each hashed batch - will impact
        performance as parallelisation is across batches.
    `n_cpus`
        > 1 - Parallel, ==1 - single core. All other options are ignored.

    """
    if isinstance(data, pd.DataFrame):
        return id_hashrs(
            pa.Table.from_pandas(data).to_batches(chunksize),
            [str(x) for x in data.columns],
            [str(data.dtypes[x]) for x in data.columns],
            n_cpus
        )
    else:
        return id_hashrs(
            data.to_batches(chunksize),
            data.column_names,
            [str(x) for x in data.schema.types],
            n_cpus
        )


def create_hasher(column_names: List[str], column_dtypes: List[Union[pa.lib.DataType, np.dtype]]) -> IDHasher:
    dtype_strings = [str(x) for x in column_dtypes]
    return IDHasher(field_names=column_names, field_types=dtype_strings)
