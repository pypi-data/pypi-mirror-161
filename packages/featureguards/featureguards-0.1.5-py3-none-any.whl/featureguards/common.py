from datetime import datetime
from typing import Mapping, Union

Attrs = Mapping[str, Union[str, bool, int, float, datetime]]


class FeatureToggleException(Exception):
    pass
