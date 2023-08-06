from quick_resto_API.quick_resto_objects.modules.front.table import Table
from quick_resto_API.quick_resto_objects.quick_resto_object import QuickRestoObject


class Hall(QuickRestoObject):
    @property
    def deleted(self) -> bool:
        return self._deleted

    @property
    def tables(self) -> list:
        return self._tables

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def title(self) -> str:
        return self._title

    def __init__(self, deleted: bool = None, tables: list = None, width: int = None,
                 height: int = None, title: str = None, **kwargs):
        class_name = "ru.edgex.quickresto.modules.front.tablemanagement.hall.Hall"
        
        super().__init__(class_name=class_name, **kwargs)

        self._deleted: bool = deleted
        
        if tables is not None: 
            self._tables: list = [Table(**value) for value in tables]
        else:
            self._tables = None

        self._width: int = width
        self._height: int = height
        self._title: str = title
