from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.front.hall import Hall

class HallOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "front.tablemanagement.hall"

    def get_list_of_hall(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False) -> list[Hall]:

        json_response = self._operations_with_objects.getList(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[Hall] = list()

        for object in json_response:
            result.append(Hall(**object))

        return result

    def get_tree_of_hall(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False) -> list[Hall]:

        json_response = self._operations_with_objects.getTree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[Hall] = list()

        for object in json_response:
            result.append(Hall(**object))

        return result

    def get_hall(self, objectId: int, objectRid: int = None) -> Hall:
        json_response = self._operations_with_objects.getObject(self._module_name, objectId, objectRid).json()

        return Hall(**json_response)

    def get_hall_with_subobjects(self, objectId: int, objectRid: int = None) -> Hall:
        json_response = self._operations_with_objects.getObjectWithSubobjects(self._module_name, objectId, objectRid).json()

        return Hall(**json_response)

    def create_hall(self, object: Hall,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Hall:

        json_response = self._operations_with_objects.createObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Hall(**json_response)

    def update_hall(self, object: Hall,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Hall:

        json_response = self._operations_with_objects.updateObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Hall(**json_response)

    def remove_hall(self, object: Hall,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Hall:

        json_response = self._operations_with_objects.removeObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Hall(**json_response)

    def recover_hall(self, object: Hall,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Hall:

        json_response = self._operations_with_objects.recoverObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Hall(**json_response)