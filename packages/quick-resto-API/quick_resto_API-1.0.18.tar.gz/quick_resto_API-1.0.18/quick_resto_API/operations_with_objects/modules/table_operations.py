from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.table import Table

class TableOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.tablemanagement.table"

    def get_list_of_table(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False) -> list[Table]:

        json_response = self._operations_with_objects.getList(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[Table] = list()

        for object in json_response:
            result.append(Table(**object))

        return result

    def get_tree_of_table(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False) -> list[Table]:

        json_response = self._operations_with_objects.getTree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[Table] = list()

        for object in json_response:
            result.append(Table(**object))

        return result

    def get_table(self, objectId: int, objectRid: int = None) -> Table:
        json_response = self._operations_with_objects.getObject(self._module_name, objectId, objectRid).json()

        return Table(**json_response)

    def get_table_with_subobjects(self, objectId: int, objectRid: int = None) -> Table:
        json_response = self._operations_with_objects.getObjectWithSubobjects(self._module_name, objectId, objectRid).json()

        return Table(**json_response)

    def create_table(self, object: Table,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Table:

        json_response = self._operations_with_objects.createObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Table(**json_response)

    def update_table(self, object: Table,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Table:

        json_response = self._operations_with_objects.updateObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Table(**json_response)

    def remove_table(self, object: Table,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Table:

        json_response = self._operations_with_objects.removeObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Table(**json_response)

    def recover_table(self, object: Table,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Table:

        json_response = self._operations_with_objects.recoverObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Table(**json_response)