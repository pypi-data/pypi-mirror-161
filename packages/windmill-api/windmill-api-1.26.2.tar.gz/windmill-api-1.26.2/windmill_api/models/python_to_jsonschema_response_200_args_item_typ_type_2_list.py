from enum import Enum


class PythonToJsonschemaResponse200ArgsItemTypType2List(str, Enum):
    STR = "str"
    FLOAT = "float"
    INT = "int"
    EMAIL = "email"

    def __str__(self) -> str:
        return str(self.value)
