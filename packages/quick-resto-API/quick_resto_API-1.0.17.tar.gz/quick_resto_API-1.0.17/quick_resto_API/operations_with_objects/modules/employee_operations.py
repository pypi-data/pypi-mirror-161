from quick_resto_API.operations_with_objects.operations_with_objects import OperationsWithObjects
from quick_resto_API.operations_with_objects.system_object import SystemObject
from quick_resto_API.quick_resto_api import QuickRestoApi
from quick_resto_API.quick_resto_objects.modules.personnel.employee import Employee


class EmployeeOperations(SystemObject):
    def __init__(self, api: QuickRestoApi):
        self._operations_with_objects = OperationsWithObjects(api)

        self._module_name:str = "personnel.employee"

    def get_list_of_employee(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False) -> list[Employee]:

        json_response = self._operations_with_objects.getList(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[Employee] = list()

        for object in json_response:
            result.append(Employee(**object))

        return result

    def get_tree_of_employee(self, ownerContextId: int = None, ownerContextClassName: str = None,
                           showDeleted: bool = False) -> list[Employee]:

        json_response = self._operations_with_objects.getTree(self._module_name,
                                                              ownerContextId, ownerContextClassName, showDeleted).json()

        result:list[Employee] = list()

        for object in json_response:
            result.append(Employee(**object))

        return result

    def get_employee(self, objectId: int, objectRid: int = None) -> Employee:
        json_response = self._operations_with_objects.getObject(self._module_name, objectId, objectRid).json()

        return Employee(**json_response)

    def get_employee_with_subobjects(self, objectId: int, objectRid: int = None) -> Employee:
        json_response = self._operations_with_objects.getObjectWithSubobjects(self._module_name, objectId, objectRid).json()

        return Employee(**json_response)

    def create_employee(self, object: Employee,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Employee:

        json_response = self._operations_with_objects.createObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Employee(**json_response)

    def update_employee(self, object: Employee,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Employee:

        json_response = self._operations_with_objects.updateObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Employee(**json_response)

    def remove_employee(self, object: Employee,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Employee:

        json_response = self._operations_with_objects.removeObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Employee(**json_response)

    def recover_employee(self, object: Employee,ownerContextId: int = None,
                                                ownerContextClassName: str = None, parentContextId: int = None,
                                                parentContextClassName: str = None) -> Employee:

        json_response = self._operations_with_objects.recoverObject(object, self._module_name, ownerContextId, 
                                                ownerContextClassName, parentContextId, parentContextClassName).json()

        return Employee(**json_response)