from quick_resto_API.quick_resto_objects.modules.core.payment_types import PaymentType
from quick_resto_API.quick_resto_objects.quick_resto_object import QuickRestoObject

class Payment(QuickRestoObject):
    @property
    def payment_type(self) -> PaymentType:
        return self._payment_type

    @property
    def partial_allowed(self) -> bool:
        return self._partial_allowed

    @property
    def require_admin_confirmation(self) -> bool:
        return self._require_admin_confirmation

    @property
    def require_customer_confirmation(self) -> bool:
        return self._require_customer_confirmation

    @property
    def customer_type(self) -> str:
        return self._customer_type

    @property
    def amount(self) -> float:
        return self._amount

    def __init__(self,paymentType:dict, partialAllowed: bool = None, requireAdminConfirmation: bool = None,
                 requireCustomerConfirmation: bool = None, customerType: str = None, amount:float = None, **kwargs):
        class_name = ""

        super().__init__(class_name=class_name, **kwargs)

        if paymentType is not None:
            self._payment_type = PaymentType(**paymentType)
        else:
            self._payment_type = None

        self._partial_allowed: bool = partialAllowed
        self._require_admin_confirmation: bool = requireAdminConfirmation
        self._require_customer_confirmation: bool = requireCustomerConfirmation
        self._customer_type: str = customerType
        self._amount = amount
