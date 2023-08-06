import io

import pandas as pd

from databutton.utils import (
    download_from_bucket,
    get_databutton_config,
    upload_to_bucket,
)


def get(key: str, ignore_not_found=True) -> pd.DataFrame:
    config = get_databutton_config()
    try:
        res = download_from_bucket(key, config)
        return pd.read_feather(io.BytesIO(res.content))
    except FileNotFoundError as e:
        if ignore_not_found:
            return pd.DataFrame()
        raise e


def put(df: pd.DataFrame, key: str):
    config = get_databutton_config()
    buf = io.BytesIO()
    df.to_feather(buf)
    # Reset to be able to upload
    buf.seek(0)

    upload_to_bucket(buf, config, key, content_type="vnd.apache.arrow.file")

    return True


def concat(
    key: str,
    other: pd.DataFrame,
    ignore_index: bool = False,
    verify_integrity: bool = False,
    sort: bool = False,
):
    df = get(key)
    new_df = pd.concat(
        [df, other],
        ignore_index=ignore_index,
        verify_integrity=verify_integrity,
        sort=sort,
    )
    put(new_df, key=key)
    return new_df


def add(key: str, entry):
    return concat(key=key, other=pd.DataFrame(entry, index=[0]), ignore_index=True)


def clear(key: str):
    """Empty the data at a certain key, leaving you with an empty dataframe on the next .get"""
    return put(pd.DataFrame(data=None).reset_index(), key=key)
