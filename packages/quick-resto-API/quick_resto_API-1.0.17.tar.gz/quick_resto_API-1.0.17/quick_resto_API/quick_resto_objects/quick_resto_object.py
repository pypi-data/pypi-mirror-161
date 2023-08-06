import json
from enum import Enum

import quick_resto_API.quick_resto_objects.styler as styler

class QuickRestoObject(object):
    @property
    def id(self) -> int:
        return self._id

    @property
    def global_id(self) -> int:
        return self._global_id

    @property
    def class_name(self) -> str:
        return self._class_name

    def get_json_object(self) -> dict:
        as_dict = self.__dict__
        result = dict()

        for key, value in as_dict.items():
            parameter_name = styler.to_camel_case(key)

            if issubclass(type(value), QuickRestoObject):
                result[parameter_name] = value.get_json_object()
            elif issubclass(type(value), list):
                list_of_subobjects = []

                for obj in value:
                    if issubclass(type(obj), QuickRestoObject):
                        list_of_subobjects.append(obj.get_json_object())

                result[parameter_name] = list_of_subobjects
            else:
                result[parameter_name] = value

        return result

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return json.dumps(self.get_json_object(), cls=QuickRestoObjectEncoder, indent=4, ensure_ascii=False)

    def __init__(self, class_name: str, id: int = 0,  className: str = "", _id: int = 0, **kwargs):
        self._id: int = id
        self._global_id: int = _id

        # Server do not always return className
        if className == "":
            self._class_name: str = class_name
        else:
            self._class_name: str = className


class QuickRestoObjectEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, QuickRestoObject):
            return obj.__dict__
        elif isinstance(obj, Enum):
            return obj.value

        return json.JSONEncoder.default(self, obj)
