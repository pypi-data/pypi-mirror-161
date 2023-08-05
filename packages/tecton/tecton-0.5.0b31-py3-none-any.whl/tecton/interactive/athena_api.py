from datetime import datetime
from typing import Optional
from typing import Union

import pandas

from tecton._internals import errors
from tecton.interactive.data_frame import DataFrame
from tecton_athena import sql_helper
from tecton_core.errors import TectonAthenaNotImplementedError
from tecton_core.feature_set_config import FeatureSetConfig
from tecton_core.time_utils import get_timezone_aware_datetime


def get_historical_features(
    feature_set_config: FeatureSetConfig,
    spine: Optional[Union[pandas.DataFrame, str]] = None,
    timestamp_key: Optional[str] = None,
    include_feature_view_timestamp_columns: bool = False,
    from_source: bool = False,
    save: bool = False,
    save_as: Optional[str] = None,
    start_time: datetime = None,
    end_time: datetime = None,
    entities: Optional[Union[pandas.DataFrame]] = None,
) -> DataFrame:
    if spine is None and timestamp_key is not None:
        raise errors.GET_HISTORICAL_FEATURES_WRONG_PARAMS(["timestamp_key"], "the spine parameter is not provided")
    if save or save_as is not None:
        raise TectonAthenaNotImplementedError("save is not supported for Athena")
    if timestamp_key is None and spine is not None:
        raise TectonAthenaNotImplementedError("timestamp_key must be specified")
    if entities is not None:
        raise TectonAthenaNotImplementedError("entities is not supported right now")
    if spine is not None and (start_time or end_time):
        raise TectonAthenaNotImplementedError("If a spine is provided, start_time and end_time must not be provided")

    start_time = get_timezone_aware_datetime(start_time)
    end_time = get_timezone_aware_datetime(end_time)

    return DataFrame._create(
        sql_helper.get_historical_features(
            spine=spine,
            timestamp_key=timestamp_key,
            feature_set_config=feature_set_config,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
            start_time=start_time,
            end_time=end_time,
        )
    )
