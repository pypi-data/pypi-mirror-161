from typing import Union

from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import format_freshness_table
from tecton._internals.utils import get_all_freshness


@sdk_public_method
def get_feature_freshness(workspace_name) -> Union[Displayable, str]:
    """
    Fetch freshness status for features

    :param: workspace_name: workspace to fetch freshness statuses of features from.

    :return: Table or dictionary of freshness statuses for all features
    """
    # TODO: use GetAllFeatureFreshnessRequest once we implement Chronosphere based API.
    freshness_statuses = get_all_freshness(workspace_name)

    if len(freshness_statuses) == 0:
        return "No Feature Views found in this workspace"
    return format_freshness_table(freshness_statuses)
