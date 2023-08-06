from quick_resto_API.quick_resto_objects.quick_resto_object import QuickRestoObject

class User(QuickRestoObject):
    @property
    def user_kind(self) -> str:
        return self._user_kind

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def login(self) -> str:
        return self._login

    @property
    def language(self) -> dict:
        return self._language

    @property
    def deleted(self) -> bool:
        return self._deleted

    @property
    def hidden(self) -> bool:
        return self._hidden

    @property
    def last_login_time(self) -> str:
        return self._last_login_time

    @property
    def tokens(self) -> list:
        return self._tokens

    def __init__(self, userKind: str = None, lastName: str = None, login: str = None, language: dict = None, deleted: bool = None, 
                hidden: bool = None, lastLoginTime: str = None, tokens: list = None, **kwargs):
        class_name = ""
        super().__init__(class_name=class_name, **kwargs)

        self._user_kind: str = userKind
        self._last_name: str = lastName
        self._login: str = login
        self._language: dict = language
        self._deleted: bool = deleted
        self._hidden: bool = hidden
        self._last_login_time: str = lastLoginTime
        self._tokens: list = tokens