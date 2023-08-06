from enum import Enum


class MainArgSignatureArgsItemTypType2List(str, Enum):
    STR = "str"
    FLOAT = "float"
    INT = "int"
    EMAIL = "email"

    def __str__(self) -> str:
        return str(self.value)
