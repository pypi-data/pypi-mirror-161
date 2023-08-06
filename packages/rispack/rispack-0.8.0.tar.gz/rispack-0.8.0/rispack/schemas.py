from __future__ import annotations

from typing import Dict, Union

from marshmallow.utils import EXCLUDE
from marshmallow_dataclass import dataclass


class BaseSchema:
    @classmethod
    def load(cls, data: Union[dict, BaseSchema], unknown=EXCLUDE, **kwargs):
        if isinstance(data, BaseSchema):
            data = data.dump()

        return cls.Schema().load(data, unknown=unknown, **kwargs)

    def dump(self, **kwargs):
        return self.Schema(**kwargs).dump(self)
